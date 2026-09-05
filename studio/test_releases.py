import hashlib
import io
import json
import os
import pwd
import sqlite3
import tempfile
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch
from django.test import SimpleTestCase
from deployment.releases import version, https_url, unpack, download
from deployment.runner import UpdateRunner

class ReleaseTests(SimpleTestCase):
    def test_release_remains_readable_after_root_ownership(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            code=root/'code';code.mkdir(mode=0o700)
            plain=code/'VERSION';plain.write_text('0.5.0');plain.chmod(0o600)
            executable=code/'python';executable.write_text('');executable.chmod(0o700)
            private=root/'data';private.mkdir(mode=0o700)
            (code/'data').symlink_to(private)
            runner=object.__new__(UpdateRunner)
            with patch('deployment.runner.os.chown'):
                runner.ownership(code,'root')
            self.assertEqual(code.stat().st_mode & 0o777,0o755)
            self.assertEqual(plain.stat().st_mode & 0o777,0o644)
            self.assertEqual(executable.stat().st_mode & 0o777,0o755)
            self.assertEqual(private.stat().st_mode & 0o777,0o700)
    def test_versions_and_urls(self):
        self.assertGreater(version('0.10.0'),version('0.9.9'))
        for value in ['../1','1.0','1.0.0;rm','01.0.0']:
            with self.assertRaises(ValueError):version(value)
        for value in ['http://host/file','file:///etc/passwd','https://user:pass@host/file']:
            with self.assertRaises(ValueError):https_url(value)
    def test_archive_traversal_and_links_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            for index,name in enumerate(['../outside','/absolute','.env','data/db.sqlite3','bad\\path']):
                archive=root/f'{index}.zip'
                with zipfile.ZipFile(archive,'w') as z:z.writestr(name,'bad')
                with self.assertRaises(ValueError):unpack(archive,root/'out','1.0.0')
            archive=root/'link.zip'
            info=zipfile.ZipInfo('link');info.external_attr=(0o120777<<16)
            with zipfile.ZipFile(archive,'w') as z:z.writestr(info,'/etc/passwd')
            with self.assertRaises(ValueError):unpack(archive,root/'out','1.0.0')
    def test_checksum_mismatch(self):
        response=io.BytesIO(b'wrong');response.url='https://updates.example.org/release.zip'
        with tempfile.TemporaryDirectory() as folder,patch('urllib.request.urlopen',return_value=response):
            with self.assertRaises(ValueError):download({'url':response.url,'sha256':'0'*64},Path(folder)/'archive.zip')
    def test_success_and_rollback_with_real_database(self):
        for fail in [False,True]:
            with self.subTest(fail=fail),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);(root/'releases/0.1.0').mkdir(parents=True)
                (root/'releases/0.1.0/VERSION').write_text('0.1.0')
                (root/'current').symlink_to(root/'releases/0.1.0')
                (root/'state').mkdir();(root/'backups').mkdir();(root/'env').write_text('DJANGO_DEBUG=false\n')
                database=root/'db.sqlite3'
                with sqlite3.connect(database) as db:db.execute('CREATE TABLE data (value TEXT)');db.execute("INSERT INTO data VALUES ('original')")
                archive=root/'fixture.zip'
                with zipfile.ZipFile(archive,'w') as z:
                    for name,content in {'VERSION':'0.2.0','manage.py':'','requirements.txt':'','scripts/build.sh':'','config/wsgi.py':''}.items():z.writestr(name,content)
                release={'version':'0.2.0','url':'https://updates.example.org/new.zip','sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
                request={'job':str(uuid.uuid4()),'version':'0.2.0','sha256':release['sha256']}
                (root/'state/request.json').write_text(json.dumps(request))
                config={'root':str(root),'state':str(root/'state'),'database':str(database),'backups':str(root/'backups'),'environment':str(root/'env'),'manifest_url':'https://updates.example.org/latest.json','user':pwd.getpwuid(os.getuid()).pw_name,'service':'test','host':'test','log':str(root/'log')}
                class LocalRunner(UpdateRunner):
                    def prepare(self,stage):pass
                    def ownership(self,path,user):pass
                    def service(self,action):pass
                    def migrate(self,stage):
                        with sqlite3.connect(self.database) as db:db.execute("UPDATE data SET value='migrated'")
                        if fail:raise RuntimeError('Simulated failed migration')
                    def healthy(self,expected):
                        assert (self.current/'VERSION').read_text()==expected
                    def restore(self,backup):
                        import shutil
                        shutil.copyfile(backup,self.database)
                def fixture_download(release,destination):destination.write_bytes(archive.read_bytes())
                with patch('deployment.runner.manifest',return_value=release),patch('deployment.runner.download',side_effect=fixture_download):LocalRunner(config).run()
                state=json.loads((root/'state/status.json').read_text())
                self.assertEqual(state['state'],'error' if fail else 'success')
                self.assertEqual((root/'current/VERSION').read_text(),'0.1.0' if fail else '0.2.0')
                with sqlite3.connect(database) as db:self.assertEqual(db.execute('SELECT value FROM data').fetchone()[0],'original' if fail else 'migrated')
                self.assertFalse((root/'state/active').exists())
