# Generated by Django 3.2.4 on 2021-09-08 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ip_camera', '0007_alter_camera_thumbnail'),
        ('main', '0005_rename_camera_name_seat_camera'),
    ]

    operations = [
        migrations.AlterField(
            model_name='seat',
            name='camera',
            field=models.ManyToManyField(blank=True, to='ip_camera.Camera'),
        ),
        migrations.AlterField(
            model_name='seat',
            name='camera_data',
            field=models.ManyToManyField(blank=True, to='main.Camera_Data'),
        ),
    ]
