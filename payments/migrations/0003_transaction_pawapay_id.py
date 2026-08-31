# Generated manually for PawaPay integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='pawapay_id',
            field=models.CharField(blank=True, db_index=True, max_length=36),
        ),
    ]
