# Generated by Django 4.2.11 on 2024-05-06 08:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('travelregistration', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('lived', 'lived'), ('stayed', 'stayed'), ('walked', 'walked'), ('passed through', 'passed through')], max_length=64)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travelregistration.location')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
