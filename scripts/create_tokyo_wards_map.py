#!/usr/bin/env python
"""Creates a map of Tokyo's 23 special wards. Run from the project root:
    .venv/bin/python scripts/create_tokyo_wards_map.py
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "travelmap.settings")
django.setup()

from travelregistration.models import Location, Map, Region  # noqa: E402

# Approximate grid layout (name, name_en, col, row)
WARDS = [
    ("練馬区", "Nerima",    2, 1),
    ("板橋区", "Itabashi",  3, 1),
    ("北区",   "Kita",      4, 1),
    ("足立区", "Adachi",    5, 1),
    ("葛飾区", "Katsushika",6, 1),
    ("杉並区", "Suginami",  1, 2),
    ("中野区", "Nakano",    2, 2),
    ("豊島区", "Toshima",   3, 2),
    ("荒川区", "Arakawa",   4, 2),
    ("江戸川区","Edogawa",  6, 2),
    ("世田谷区","Setagaya", 1, 3),
    ("渋谷区", "Shibuya",   2, 3),
    ("新宿区", "Shinjuku",  3, 3),
    ("文京区", "Bunkyo",    4, 3),
    ("台東区", "Taito",     5, 3),
    ("墨田区", "Sumida",    6, 3),
    ("目黒区", "Meguro",    2, 4),
    ("港区",   "Minato",    3, 4),
    ("千代田区","Chiyoda",  4, 4),
    ("中央区", "Chuo",      5, 4),
    ("江東区", "Koto",      6, 4),
    ("大田区", "Ota",       2, 5),
    ("品川区", "Shinagawa", 3, 5),
]

map_obj = Map.objects.create(name="東京23区", name_en="Tokyo Wards", slug="tokyo-wards")
region = Region.objects.create(map=map_obj, name="東京23区", color="#e8a0a0")

locations = [
    Location(name=name, name_en=name_en, region=region,
             display_x=col, display_y=row, display_width=1, display_height=1)
    for name, name_en, col, row in WARDS
]

occupied = {(loc.display_y, loc.display_x) for loc in locations}
for loc in locations:
    loc.border_radius_top_left     = (loc.display_y, loc.display_x - 1) not in occupied and (loc.display_y - 1, loc.display_x) not in occupied
    loc.border_radius_top_right    = (loc.display_y, loc.display_x + 1) not in occupied and (loc.display_y - 1, loc.display_x) not in occupied
    loc.border_radius_bottom_left  = (loc.display_y, loc.display_x - 1) not in occupied and (loc.display_y + 1, loc.display_x) not in occupied
    loc.border_radius_bottom_right = (loc.display_y, loc.display_x + 1) not in occupied and (loc.display_y + 1, loc.display_x) not in occupied

Location.objects.bulk_create(locations)
print(f"Created map '{map_obj.name_en}' with {len(locations)} wards.")
