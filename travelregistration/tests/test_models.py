from django.db import IntegrityError
from django.test import TestCase
from django.utils.translation import override

from travelregistration.models import LocationEntry
from travelregistration.tests.factories import create_entry, create_location, create_region, create_user


class ModelTests(TestCase):
    def test_region_and_location_strings_and_grid_helpers(self):
        region = create_region(name="Kanto", color="#123")
        location = create_location(
            name="東京都",
            name_en="tokyo",
            region=region,
            display_x=3,
            display_y=4,
            display_width=2,
            display_height=5,
        )

        self.assertEqual(str(region), "Kanto")
        self.assertEqual(str(location), "東京都")
        self.assertEqual(location.get_display_x_end(), 5)
        self.assertEqual(location.get_display_y_end(), 9)

    def test_location_entry_string_uses_choice_display(self):
        user = create_user()
        location = create_location()
        entry = create_entry(user, location, status="passed through")

        with override("en"):
            self.assertEqual(str(entry), "北海道 : Passed Through")

    def test_location_entry_unique_per_user_and_location(self):
        user = create_user()
        location = create_location()
        create_entry(user, location, status="lived")

        with self.assertRaises(IntegrityError):
            create_entry(user, location, status="stayed")

    def test_all_status_choices_are_valid(self):
        choices = {value for value, _label in LocationEntry._meta.get_field("status").choices}

        self.assertEqual(
            choices,
            {"none", "lived", "stayed", "walked", "passed through"},
        )
