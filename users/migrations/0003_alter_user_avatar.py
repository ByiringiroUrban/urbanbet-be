from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_passwordresettoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
