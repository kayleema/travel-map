from django.db import migrations


def create_japan_map(apps, schema_editor):
    Map = apps.get_model('travelregistration', 'Map')
    Region = apps.get_model('travelregistration', 'Region')
    japan = Map.objects.create(name='日本', name_en='Japan', slug='japan')
    Region.objects.update(map=japan)


class Migration(migrations.Migration):

    dependencies = [
        ('travelregistration', '0009_add_map_model'),
    ]

    operations = [
        migrations.RunPython(create_japan_map, migrations.RunPython.noop),
    ]
