import copy
import tempfile
from pathlib import Path
from django.conf import settings
from django.test import SimpleTestCase, override_settings
from django.template.loader import get_template
from django.core.management import get_commands
from studio.management.commands.runserver import Command

class LoadingTests(SimpleTestCase):
    def test_dev_template_changes_without_restart(self):
        templates=copy.deepcopy(settings.TEMPLATES)
        templates[0]['APP_DIRS']=False
        templates[0]['OPTIONS']['loaders']=['django.template.loaders.filesystem.Loader','django.template.loaders.app_directories.Loader']
        with tempfile.TemporaryDirectory() as folder:
            templates[0]['DIRS']=[folder]
            path=Path(folder)/'loading-probe.html'
            path.write_text('Old structure')
            with override_settings(TEMPLATES=templates):
                self.assertEqual(get_template('loading-probe.html').render(),'Old structure')
                path.write_text('New structure')
                self.assertEqual(get_template('loading-probe.html').render(),'New structure')

    def test_dev_server_override_is_selected(self):
        self.assertEqual(get_commands()['runserver'],'studio')

    @override_settings(DEBUG=True)
    def test_dev_static_requests_are_not_cached(self):
        from unittest.mock import patch
        seen={}
        def application(environ,start_response):
            seen.update(environ)
            start_response('200 OK',[('Cache-Control','max-age=600')])
            return [b'fresh']
        with patch('django.contrib.staticfiles.management.commands.runserver.Command.get_handler',return_value=application):
            handler=Command().get_handler()
        headers=[]
        result=handler({'HTTP_IF_MODIFIED_SINCE':'old','HTTP_IF_NONE_MATCH':'old'},lambda status,values,exc=None:headers.extend(values))
        self.assertEqual(result,[b'fresh'])
        self.assertNotIn('HTTP_IF_MODIFIED_SINCE',seen)
        self.assertIn(('Cache-Control','no-store'),headers)
