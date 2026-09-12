from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("studio", "0006_siteaccess")]
    operations = [
        migrations.AlterField(
            model_name="project",
            name="kind",
            field=models.CharField(
                choices=[
                    ("character", "Figur"),
                    ("room", "Raum"),
                    ("world", "Welt"),
                    ("scene", "Szene"),
                    ("drawing", "Zeichnung"),
                ],
                default="character",
                max_length=16,
            ),
        ),
    ]
