# Generated by Django 3.2.4 on 2021-08-08 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ip_camera', '0002_alter_camera_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='camera',
            name='frame',
            field=models.ImageField(blank=True, upload_to='img'),
        ),
        migrations.AlterField(
            model_name='camera',
            name='thumbnail',
            field=models.ImageField(blank=True, upload_to='img'),
        ),
    ]