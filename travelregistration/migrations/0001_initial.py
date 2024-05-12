# Generated by Django 4.2.11 on 2024-05-06 07:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('display_x', models.IntegerField()),
                ('display_y', models.IntegerField()),
                ('display_width', models.IntegerField()),
                ('display_height', models.IntegerField()),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travelregistration.region')),
            ],
        ),
    ]