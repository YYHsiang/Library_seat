# Generated by Django 3.2.4 on 2021-07-01 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seat_number', models.IntegerField()),
                ('seat_position_x', models.FloatField(max_length=200)),
                ('seat_position_y', models.FloatField(max_length=200)),
                ('occupy', models.BooleanField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.location')),
            ],
        ),
        migrations.CreateModel(
            name='Occupy_History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('seat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.seat')),
            ],
        ),
    ]