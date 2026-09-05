#!/usr/bin/env python3
"""Root-owned updater service. Never accepts shell commands or paths from the web."""
import fcntl
import json
import os
import pwd
import shutil
import sqlite3
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
try:
    from .releases import manifest, version, download, unpack
except ImportError:
    from releases import manifest, version, download, unpack

class UpdateRunner:
    def __init__(self, config):
        self.config=config
        self.root=Path(config['root'])
        self.state=Path(config['state'])
        self.database=Path(config['database'])
        self.current=self.root/'current'
        self.job=None
        self.env=self.read_environment(Path(config['environment']))
        self.env['PATH']='/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
        self.env['PYTHONDONTWRITEBYTECODE']='1'
        self.target=None
    @staticmethod
    def read_environment(path):
        env={}
        for line in path.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith('#'):continue
            key,sep,value=line.partition('=')
            if sep:env[key.strip()]=value.strip()
        return env
    def status(self,state,progress,message,**extra):
        record={'job':self.job,'state':state,'progress':progress,'message':message,'updated_at':time.time(),**extra}
        with tempfile.NamedTemporaryFile(mode='w',dir=self.state,prefix='.status-',delete=False) as stream:
            json.dump(record,stream);temporary=stream.name
        os.chmod(temporary,0o644)
        os.replace(temporary,self.state/'status.json')
    def command(self,args,cwd=None,as_user=False):
        env={**self.env}
        identity={}
        if as_user:
            account=pwd.getpwnam(self.config['user'])
            identity={'user':account.pw_uid,'group':account.pw_gid,'extra_groups':[]}
        with open(self.config.get('log','/var/log/rikas-updater.log'),'ab') as log:
            subprocess.run(list(map(str,args)),cwd=cwd,env=env,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=900,**identity)
    def ownership(self,path,user):
        account=pwd.getpwnam(user)
        for parent,dirs,files in os.walk(path):
            os.chown(parent,account.pw_uid,account.pw_gid)
            if user=='root':os.chmod(parent,0o755)
            for name in dirs+files:
                entry=Path(parent)/name
                os.chown(entry,account.pw_uid,account.pw_gid,follow_symlinks=False)
                if user=='root' and not entry.is_symlink():
                    os.chmod(entry,0o755 if entry.is_dir() or entry.stat().st_mode & 0o100 else 0o644)
    def prepare(self,stage):
        self.ownership(stage,self.config['user'])
        self.command(['python3','-m','venv',stage/'.venv'],as_user=True)
        self.command([stage/'.venv/bin/pip','install','--disable-pip-version-check','-r',stage/'requirements.txt'],cwd=stage,as_user=True)
        self.command(['sh',stage/'scripts/build.sh'],cwd=stage,as_user=True)
        self.command([stage/'.venv/bin/python','manage.py','check','--deploy','--fail-level','WARNING'],cwd=stage,as_user=True)
    def migrate(self,stage):
        self.command([stage/'.venv/bin/python','manage.py','migrate','--noinput'],cwd=stage,as_user=True)
    def service(self,action):self.command(['systemctl',action,self.config['service']])
    def switch(self,release):
        temporary=self.root/'.current-next'
        temporary.unlink(missing_ok=True)
        temporary.symlink_to(release)
        os.replace(temporary,self.current)
    def backup(self,path):
        with sqlite3.connect(f'file:{self.database}?mode=ro',uri=True) as source,sqlite3.connect(path) as target:
            source.backup(target)
        os.chmod(path,0o600)
    def restore(self,backup):
        # The application is stopped; replace the DB atomically, remove journals.
        target=self.database.with_suffix('.restore')
        shutil.copyfile(backup,target)
        user=pwd.getpwnam(self.config['user'])
        os.chown(target,user.pw_uid,user.pw_gid);os.chmod(target,0o600)
        for suffix in ['-wal','-shm','-journal']:Path(str(self.database)+suffix).unlink(missing_ok=True)
        os.replace(target,self.database)
    def healthy(self,expected):
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for _ in range(40):
            try:
                req=urllib.request.Request('http://127.0.0.1:8000/health/',headers={'Host':self.config['host'],'X-Forwarded-Proto':'https'})
                with opener.open(req,timeout=2) as response:data=json.load(response)
                if data.get('ok') and data.get('version')==expected:return
            except Exception:pass
            time.sleep(1)
        raise RuntimeError('Neue Version wurde nach dem Neustart nicht gesund.')
    def run(self):
        request_path=self.state/'request.json'
        # O_NOFOLLOW prevents a user-controlled symlink from becoming a root read.
        import stat
        with os.fdopen(os.open(request_path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)) as source:
            info=os.fstat(source.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size>4096:raise ValueError('Ungültige Update-Anforderung')
            request=json.load(source)
        import uuid
        self.job=str(uuid.UUID(request['job']))
        os.close(os.open(self.state/'active',os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o644))
        request_path.unlink()
        old=self.current.resolve(strict=True)
        old_version=(old/'VERSION').read_text().strip()
        backup=None;backup_ready=False;stopped=False;stage=None;switched=False
        try:
            self.status('running',5,'Update-Quelle und Version werden geprüft …')
            release=manifest(self.config['manifest_url'])
            if request['version']!=release['version'] or request['sha256']!=release['sha256'] or version(release['version'])<=version(old_version):
                raise ValueError('Das Release hat sich geändert oder ist nicht neuer.')
            target=self.root/'releases'/release['version']
            if target.exists():raise ValueError('Dieses Versionsverzeichnis existiert bereits. Bitte Administrator prüfen lassen.')
            stage=Path(tempfile.mkdtemp(prefix='.staging-',dir=self.root/'releases'))
            archive=stage/'release.zip'
            self.status('running',12,'Update wird heruntergeladen und geprüft …')
            download(release,archive)
            code=stage/'code';code.mkdir()
            unpack(archive,code,release['version'])
            self.status('running',25,'Neue Version wird vorbereitet. Die bisherige Version läuft weiter …')
            # Build in final path: virtualenv entry points contain absolute paths.
            code.rename(target);self.target=target
            self.prepare(target)
            self.status('running',60,'Anwendung wird für Sicherung und Datenbankupdate angehalten …')
            self.service('stop');stopped=True
            backup=Path(self.config['backups'])/f'{old_version}-{self.job}.sqlite3'
            self.backup(backup)
            backup_ready=True
            self.status('running',70,'Sicherung erstellt. Datenbank wird aktualisiert …')
            self.migrate(target)
            self.ownership(target,'root')
            self.status('running',85,'Neue Version wird aktiviert …')
            self.switch(target);switched=True
            self.service('start')
            self.healthy(release['version'])
            self.status('success',100,f'Update auf Version {release["version"]} erfolgreich. Die Seite wird neu geladen.',version=release['version'])
        except Exception as error:
            rollback=False
            try:
                if stopped:
                    self.service('stop')
                    if backup_ready:self.restore(backup)
                    if switched:self.switch(old)
                    self.service('start');self.healthy(old_version);rollback=True
            except Exception:
                self.status('error',0,'Update fehlgeschlagen. Die automatische Wiederherstellung braucht eine manuelle Prüfung. Details im Updater-Protokoll.')
                raise
            message='Update fehlgeschlagen. '+('Die bisherige Version und Datenbank wurden wiederhergestellt.' if rollback else 'Die bisherige Version bleibt unverändert.')
            self.status('error',0,message)
            with open(self.config.get('log','/var/log/rikas-updater.log'),'a') as log:log.write(f'\n{type(error).__name__}: {error}\n')
            if self.target and self.target.exists() and self.current.resolve()!=self.target:shutil.rmtree(self.target)
        finally:
            self.state.joinpath('active').unlink(missing_ok=True)
            if stage:shutil.rmtree(stage,ignore_errors=True)

def main():
    config_path=Path('/etc/rikas-updater.json')
    config=json.loads(config_path.read_text())
    state=Path(config['state'])
    with open('/run/rikas-updater.lock','w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if (state/'request.json').exists():
            runner=UpdateRunner(config)
            try:runner.run()
            except Exception:
                runner.status('error',0,'Updater konnte nicht starten. Bitte das Dienstprotokoll prüfen.')
                (state/'request.json').unlink(missing_ok=True)
                (state/'active').unlink(missing_ok=True)
if __name__=='__main__':main()
