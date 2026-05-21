from django.contrib.auth import get_user_model

from travelregistration.models import Location, LocationEntry, Map, Region


def create_user(username="traveler", password="password"):
    return get_user_model().objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password=password,
    )


def create_map(name="テスト", name_en="Test Map", slug="test-map"):
    obj, _ = Map.objects.get_or_create(slug=slug, defaults={"name": name, "name_en": name_en})
    return obj


def create_region(name="Test Region", color="#abc", map=None):
    return Region.objects.create(name=name, color=color, map=map or create_map())


def create_location(
    *,
    name="北海道",
    name_en="hokkaido",
    region=None,
    display_x=1,
    display_y=1,
    display_width=1,
    display_height=1,
    **kwargs,
):
    return Location.objects.create(
        name=name,
        name_en=name_en,
        region=region or create_region(),
        display_x=display_x,
        display_y=display_y,
        display_width=display_width,
        display_height=display_height,
        **kwargs,
    )


def create_entry(user, location, status="lived"):
    return LocationEntry.objects.create(user=user, location=location, status=status)
