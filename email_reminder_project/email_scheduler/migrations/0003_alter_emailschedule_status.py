# Generated by Django 4.2.16 on 2024-12-12 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('email_scheduler', '0002_emailschedule_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailschedule',
            name='status',
            field=models.CharField(choices=[('unsent', 'Unsent'), ('sent', 'Sent'), ('canceled', 'Canceled')], default='unsent', max_length=10),
        ),
    ]
