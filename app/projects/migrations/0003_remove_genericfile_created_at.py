# Generated by Django 2.2.6 on 2019-11-18 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20191118_1233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='genericfile',
            name='created_at',
        ),
    ]
