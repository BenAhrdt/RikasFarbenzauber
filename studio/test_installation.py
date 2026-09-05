import os
import pwd
import tempfile
from pathlib import Path
from unittest.mock import patch
from django.test import SimpleTestCase
from deployment import install

class InstallationTests(SimpleTestCase):
    def test_interactive_install_generates_shared_update_service(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'source';source.mkdir()
            (source/'VERSION').write_text('0.5.2')
            (source/'update.sh').write_text((Path(__file__).resolve().parent.parent/'update.sh').read_text())
            (source/'deployment').mkdir()
            for name in ['runner.py','releases.py','request_update.py']:
                (source/'deployment'/name).write_text('# fixture')
            for directory in ['etc/systemd/system','etc/nginx/sites-available','etc/nginx/sites-enabled']:
                (root/directory).mkdir(parents=True)
            def sandbox_path(value):
                p=Path(value)
                return root/str(p).lstrip('/') if str(p).startswith(('/etc/','/usr/')) else p
            from deployment import releases
            with patch.object(install,'SOURCE',source), patch.object(install,'ROOT',root/'opt/app'), patch.object(install,'STATE',root/'state'), patch.object(install,'ENV',root/'etc/app.env'), patch.object(install,'Path',side_effect=sandbox_path), patch.object(install,'command') as command, patch('deployment.install.os.geteuid',return_value=0), patch('deployment.install.os.chown'), patch('deployment.install.os.umask'), patch('deployment.install.pwd.getpwnam',return_value=pwd.getpwuid(os.getuid())), patch('deployment.install.shutil.which',return_value='/bin/fixture'), patch('deployment.install.sys.argv',['install.py','--install-packages']), patch('deployment.install.sys.stdin.isatty',return_value=True), patch('builtins.input',side_effect=['farben.example.org','192.168.2.10']), patch.dict('sys.modules',{'releases':releases}):
                install.main()
            unit=(root/'etc/systemd/system/rikas-updater.service').read_text()
            self.assertIn('/usr/local/lib/rikas-updater/update.sh --worker',unit)
            wrapper=root/'usr/local/lib/rikas-updater/update.sh'
            self.assertTrue(os.access(wrapper,os.X_OK))
            self.assertIn('runner.py',wrapper.read_text())
            self.assertTrue((root/'opt/app/current').is_symlink())
            self.assertEqual((root/'etc/app.env').stat().st_mode & 0o777,0o600)
            self.assertIn('DJANGO_ALLOWED_HOSTS=farben.example.org',(root/'etc/app.env').read_text())
            self.assertTrue(any(call.args[0][:2]==['apt-get','install'] for call in command.call_args_list))
