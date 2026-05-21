import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travelregistration', '0012_make_location_region_optional'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='region',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='travelregistration.region',
            ),
        ),
    ]
