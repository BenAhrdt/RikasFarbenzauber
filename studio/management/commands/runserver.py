from django.conf import settings
from django.contrib.staticfiles.management.commands.runserver import Command as StaticCommand

class Command(StaticCommand):
    def get_handler(self, *args, **options):
        application = super().get_handler(*args, **options)
        if not settings.DEBUG:
            return application
        def uncached(environ, start_response):
            # Even clients holding old cached assets must receive fresh content.
            environ.pop('HTTP_IF_MODIFIED_SINCE', None)
            environ.pop('HTTP_IF_NONE_MATCH', None)
            def start(status, headers, exc_info=None):
                headers = [(k, v) for k, v in headers if k.lower() != 'cache-control']
                headers.append(('Cache-Control', 'no-store'))
                return start_response(status, headers, exc_info)
            return application(environ, start)
        return uncached
