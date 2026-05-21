import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelregistration', '0010_populate_japan_map'),
    ]

    operations = [
        migrations.AlterField(
            model_name='region',
            name='map',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='travelregistration.map',
            ),
        ),
    ]
