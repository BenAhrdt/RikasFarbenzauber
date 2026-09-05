from django.db import migrations


def seed(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Installation = apps.get_model('studio', 'Installation')
    Installation.objects.using(schema_editor.connection.alias).get_or_create(
        pk=1, defaults={'completed': User.objects.using(schema_editor.connection.alias).filter(is_superuser=True).exists()}
    )


class Migration(migrations.Migration):
    dependencies = [('studio', '0002_installation')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
