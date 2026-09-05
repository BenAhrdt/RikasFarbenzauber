import os
import pwd
import tempfile
from pathlib import Path
from unittest.mock import patch
from django.test import SimpleTestCase
from deployment import install

class InstallationTests(SimpleTestCase):
    def test_interactive_install_generates_shared_update_service(self):
        self.install_case(['y','https://farben.example.org'],'https://farben.example.org')

    def test_local_only_install_skips_address_prompt(self):
        self.install_case(['n'],'')

    def install_case(self, answers, expected):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'source';source.mkdir()
            (source/'VERSION').write_text('0.5.2')
            (source/'update.sh').write_text((Path(__file__).resolve().parent.parent/'update.sh').read_text())
            (source/'deployment').mkdir()
            for name in ['runner.py','releases.py','request_update.py']:
                (source/'deployment'/name).write_text('# fixture')
            for directory in ['etc/systemd/system','etc/nginx/sites-available','etc/nginx/sites-enabled','etc/caddy']:
                (root/directory).mkdir(parents=True)
            def sandbox_path(value):
                p=Path(value)
                return root/str(p).lstrip('/') if str(p).startswith(('/etc/','/usr/')) else p
            from deployment import releases, access_config
            with patch.object(install,'SOURCE',source), patch.object(install,'ROOT',root/'opt/app'), patch.object(install,'STATE',root/'state'), patch.object(install,'ENV',root/'etc/app.env'), patch.object(install,'Path',side_effect=sandbox_path), patch.object(install,'command') as command, patch('deployment.install.os.geteuid',return_value=0), patch('deployment.install.os.chown'), patch('deployment.install.os.umask'), patch('deployment.install.pwd.getpwnam',return_value=pwd.getpwuid(os.getuid())), patch('deployment.install.shutil.which',return_value='/bin/fixture'), patch('deployment.install.sys.argv',['install.py','--install-packages']), patch('deployment.install.sys.stdin.isatty',return_value=True), patch('builtins.input',side_effect=answers), patch.dict('sys.modules',{'releases':releases,'access_config':access_config}):
                install.main()
            unit=(root/'etc/systemd/system/rikas-updater.service').read_text()
            self.assertIn('/usr/local/lib/rikas-updater/update.sh --worker',unit)
            wrapper=root/'usr/local/lib/rikas-updater/update.sh'
            self.assertTrue(os.access(wrapper,os.X_OK))
            self.assertEqual((root/'state/updates').stat().st_mode & 0o777,0o770, 'App group must be able to publish update requests despite umask')
            self.assertIn('runner.py',wrapper.read_text())
            nginx=(root/'etc/nginx/sites-available/rikas-farbenzauber').read_text()
            self.assertIn('listen 8080 default_server',nginx)
            self.assertIn('proxy_set_header Host $http_host',nginx)
            self.assertNotIn('deny all',nginx)
            self.assertTrue((root/'opt/app/current').is_symlink())
            self.assertEqual((root/'etc/app.env').stat().st_mode & 0o777,0o600)
            self.assertEqual((root/'state/updates').stat().st_mode & 0o777,0o770)
            self.assertIn('RIKA_HTTPS_ORIGINS='+expected,(root/'etc/app.env').read_text())
            self.assertTrue(any(call.args[0][:2]==['apt-get','install'] for call in command.call_args_list))
