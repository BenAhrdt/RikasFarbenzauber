#!/usr/bin/env python3
"""Fresh, root-managed LXC installation. Never overwrites an existing install."""
import argparse
import json
import os
import pwd
import re
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE=Path(__file__).resolve().parent.parent
ROOT=Path('/opt/rikas-farbenzauber')
STATE=Path('/var/lib/rikas-farbenzauber')
ENV=Path('/etc/rikas-farbenzauber.env')
USER='rikas'

def command(args,**kwargs):subprocess.run(list(map(str,args)),check=True,**kwargs)
def write(path,text,mode=0o644):path.write_text(text);path.chmod(mode)
def main():
    parser=argparse.ArgumentParser(description='Rikas Farbenzauber im LXC mit lokalem Zugang und optionalen HTTPS-Adressen installieren.')
    parser.add_argument('--https-address','--host',dest='addresses',action='append',help='Freigegebene HTTPS-Adresse; mehrfach möglich')
    parser.add_argument('--local-only',action='store_true',help='Nur lokal, ohne HTTPS-Adressen installieren')
    parser.add_argument('--manifest-url',default='https://github.com/BenAhrdt/RikasFarbenzauber/releases/latest/download/latest.json',help='HTTPS-URL zum Release-Manifest; optional später einrichten')
    parser.add_argument('--install-packages',action='store_true',help='Benötigte Debian/Ubuntu-Pakete mit apt installieren')
    args=parser.parse_args()
    if os.geteuid()!=0:parser.error('Bitte mit sudo/root starten.')
    if args.local_only and args.addresses:parser.error('--local-only und --https-address schließen sich aus.')
    if args.addresses is None and not args.local_only:
        if not sys.stdin.isatty():parser.error('Ohne Terminal bitte --local-only oder --https-address angeben.')
        print('Rikas Farbenzauber – LXC-Installation')
        answer=input('HTTPS-Adresse freigeben? [Y/n]: ').strip().lower()
        if answer not in ('','y','j','yes','ja','n','no','nein'):parser.error('Bitte Y oder n eingeben.')
        if answer not in ('n','no','nein'):
            args.addresses=[input('Welche HTTPS-Adresse? ').strip()]
    from access_config import origin
    try:addresses=list(dict.fromkeys(origin(value) for value in (args.addresses or [])))
    except ValueError as error:parser.error(str(error))
    if sys.version_info < (3,12):parser.error('Python 3.12 oder neuer wird benötigt.')
    os.umask(0o022)
    if args.manifest_url:
        from releases import https_url
        https_url(args.manifest_url)
    if ROOT.exists() or ENV.exists() or STATE.exists():parser.error('Installation existiert bereits. Verwende das Update-Skript; vorhandene Daten werden nicht überschrieben.')
    if args.install_packages:
        command(['apt-get','update'])
        command(['apt-get','install','-y','python3','python3-venv','python3-pip','nginx','ca-certificates'])
    for executable in ['python3','systemctl','runuser','nginx']:
        if not shutil.which(executable):parser.error(f'{executable} fehlt. Systempakete installieren oder --install-packages verwenden.')
    try:pwd.getpwnam(USER)
    except KeyError:command(['useradd','--system','--home-dir',str(STATE/'data'),'--shell','/usr/sbin/nologin',USER])
    account=pwd.getpwnam(USER)
    root_version=(SOURCE/'VERSION').read_text().strip()
    from releases import version
    version(root_version)
    release=ROOT/'releases'/root_version
    release.parent.mkdir(parents=True)
    shutil.copytree(SOURCE,release,ignore=shutil.ignore_patterns('.git','.venv','.env','.agents','.codex','data','staticfiles','__pycache__','*.pyc','node_modules','dist','test-results'))
    STATE.mkdir(mode=0o755)
    data=STATE/'data';data.mkdir(mode=0o700);os.chown(data,account.pw_uid,account.pw_gid)
    updates=STATE/'updates';updates.mkdir(mode=0o770);os.chown(updates,0,account.pw_gid)
    backups=STATE/'backups';backups.mkdir(mode=0o700)
    (release/'data').symlink_to(data)
    environment={
        'DJANGO_DEBUG':'false','DJANGO_SECRET_KEY':secrets.token_urlsafe(64),
        'DJANGO_ALLOWED_HOSTS':'localhost,127.0.0.1','RIKA_LOCAL_ACCESS':'true','RIKA_HTTPS_ORIGINS':','.join(addresses),
        'DATABASE_PATH':str(data/'db.sqlite3'),'UPDATE_STATE_DIR':str(updates),
        'UPDATE_MANIFEST_URL':args.manifest_url,'UPDATE_INSTALL_ENABLED':'true',
    }
    write(ENV,'\n'.join(f'{k}={v}' for k,v in environment.items())+'\n',0o600)
    def as_user(cmd):command(cmd,cwd=release,env={**os.environ,**environment},user=account.pw_uid,group=account.pw_gid,extra_groups=[])
    command(['chown','-R',f'{USER}:{USER}',release])
    as_user(['python3','-m','venv',release/'.venv'])
    as_user([release/'.venv/bin/pip','install','-r',release/'requirements.txt'])
    as_user([release/'.venv/bin/python','manage.py','migrate','--noinput'])
    as_user(['sh','scripts/build.sh'])
    as_user([release/'.venv/bin/python','manage.py','check','--deploy','--fail-level','WARNING'])
    # Do not recursively follow the persistent data symlink.
    for parent,dirs,files in os.walk(release):
        os.chown(parent,0,0);os.chmod(parent,0o755)
        for name in dirs+files:
            entry=Path(parent)/name
            os.chown(entry,0,0,follow_symlinks=False)
            if not entry.is_symlink():os.chmod(entry,0o755 if entry.is_dir() or entry.stat().st_mode & 0o100 else 0o644)
    (ROOT/'current').symlink_to(release)
    updater=Path('/usr/local/lib/rikas-updater');updater.mkdir(parents=True,exist_ok=True)
    for name in ['runner.py','releases.py','request_update.py']:shutil.copyfile(SOURCE/'deployment'/name,updater/name)
    write(updater/'update.sh',(SOURCE/'update.sh').read_text(),0o755)
    config={'root':str(ROOT),'state':str(updates),'database':str(data/'db.sqlite3'),'backups':str(backups),'environment':str(ENV),'manifest_url':args.manifest_url,'user':USER,'service':'rikas-farbenzauber.service','host':'localhost'}
    write(Path('/etc/rikas-updater.json'),json.dumps(config,indent=2)+'\n',0o600)
    unit=f'''[Unit]
Description=Rikas Farbenzauber
After=network.target
[Service]
User={USER}
Group={USER}
WorkingDirectory={ROOT}/current
EnvironmentFile={ENV}
ExecStart={ROOT}/current/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --access-logfile - --error-logfile -
Restart=on-failure
UMask=0077
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths={data} {updates}
[Install]
WantedBy=multi-user.target
'''
    write(Path('/etc/systemd/system/rikas-farbenzauber.service'),unit)
    write(Path('/etc/systemd/system/rikas-updater.service'),f'''[Unit]
Description=Rikas Farbenzauber Update Worker
After=network-online.target
[Service]
Type=oneshot
ExecStart={updater}/update.sh --worker
TimeoutStartSec=2400
UMask=0077
''')
    write(Path('/etc/systemd/system/rikas-updater.path'),f'''[Unit]
Description=Watch for Rikas Farbenzauber update requests
[Path]
PathExists={updates}/request.json
Unit=rikas-updater.service
[Install]
WantedBy=multi-user.target
''')
    # This local gateway accepts direct LAN HTTP and the user's HTTPS proxy.
    # The application validates Host against actual interface IPs and saved origins.
    nginx=f"""map $http_x_forwarded_proto $rika_scheme {{
    default $scheme;
    https https;
}}
server {{
    listen 8080 default_server;
    listen [::]:8080 default_server;
    server_name _;
    client_max_body_size 100k;
    location /static/ {{ alias {ROOT}/current/staticfiles/; }}
    location = /api/photos/ {{
        client_max_body_size 13m;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $rika_scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }}
    location / {{
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $rika_scheme;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
"""
    write(Path('/etc/nginx/sites-available/rikas-farbenzauber'),nginx)
    Path('/etc/nginx/sites-enabled/rikas-farbenzauber').symlink_to('/etc/nginx/sites-available/rikas-farbenzauber')
    command(['nginx','-t']);command(['systemctl','daemon-reload'])
    command(['systemctl','enable','--now','rikas-farbenzauber.service','rikas-updater.path','nginx.service'])
    command(['systemctl','reload','nginx'])
    print(f'Installiert: Version {root_version}. Lokal: http://LXC-IP:8080')
    print('HTTPS-Freigaben: '+(', '.join(addresses) or 'keine – nur lokaler Zugriff'))
    print('Proxy-Ziel: http://LXC-IP:8080; ursprünglichen Host und X-Forwarded-Proto: https weiterreichen.')
    print('Adressen später unter Verwaltung → Zugangsadressen ändern.')
    print(f'Konfiguration: {ENV}; Update-Quelle zusätzlich in /etc/rikas-updater.json.')
if __name__=='__main__':main()
