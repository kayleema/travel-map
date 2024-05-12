# Generated by Django 4.2.12 on 2024-05-12 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelregistration', '0003_locationentry_location_and_user_uniq'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='name_en',
            field=models.CharField(default='no english name', max_length=100),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='locationentry',
            name='status',
            field=models.CharField(choices=[('lived', 'Lived'), ('stayed', 'Stayed'), ('walked', 'Walked'), ('passed through', 'Passed Through')], max_length=64),
        ),
    ]