# Generated by Django 3.0.10 on 2020-12-20 10:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20201209_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='poll',
            name='start',
            field=models.DateTimeField(blank=True, db_index=True, default=django.utils.timezone.now, null=True),
        ),
    ]
