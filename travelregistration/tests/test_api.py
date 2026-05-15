from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from travelregistration.tests.factories import create_entry, create_location, create_region, create_user


class ApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(username="api-user")
        self.region = create_region(name="Kansai", color="#456")
        self.location = create_location(name="大阪府", name_en="osaka", region=self.region)
        self.entry = create_entry(self.user, self.location, status="stayed")

    def test_anonymous_api_requests_are_rejected(self):
        for route_name in ["location-list", "region-list", "locationentry-list"]:
            response = self.client.get(reverse(route_name))
            self.assertIn(response.status_code, [401, 403])

    def test_authenticated_api_lists_locations_regions_and_entries(self):
        self.client.force_authenticate(user=self.user)

        locations_response = self.client.get(reverse("location-list"))
        regions_response = self.client.get(reverse("region-list"))
        entries_response = self.client.get(reverse("locationentry-list"))

        self.assertEqual(locations_response.status_code, 200)
        self.assertEqual(regions_response.status_code, 200)
        self.assertEqual(entries_response.status_code, 200)

        locations = locations_response.json()
        regions = regions_response.json()
        entries = entries_response.json()

        self.assertIn(
            {"name": "大阪府", "name_en": "osaka"},
            [{"name": location["name"], "name_en": location["name_en"]} for location in locations],
        )
        self.assertIn(
            {"name": "Kansai", "color": "#456"},
            [{"name": region["name"], "color": region["color"]} for region in regions],
        )
        self.assertIn(
            {"status": "stayed", "location": self.location.pk, "user": self.user.pk},
            [
                {"status": entry["status"], "location": entry["location"], "user": entry["user"]}
                for entry in entries
            ],
        )
