# Generated by Django 3.2.4 on 2021-09-07 06:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20210907_1430'),
    ]

    operations = [
        migrations.RenameField(
            model_name='seat',
            old_name='camera_name',
            new_name='camera',
        ),
    ]