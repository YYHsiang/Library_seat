# Generated by Django 3.2.4 on 2021-08-08 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ip_camera', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='password',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
