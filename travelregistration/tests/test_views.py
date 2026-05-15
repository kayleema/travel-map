from django.core import signing
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.translation import override

from travelregistration.models import LocationEntry
from travelregistration.tests.factories import create_entry, create_location, create_region, create_user
from travelregistration.views import SHARE_MAP_SALT, homepage, shared_map, update_location


class HomepageViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = create_user(username="kaylee")
        self.other_user = create_user(username="other")
        self.region = create_region()
        self.hokkaido = create_location(
            name="北海道",
            name_en="hokkaido",
            region=self.region,
            display_x=1,
            display_y=1,
            display_width=1,
            display_height=1,
        )
        self.tokyo = create_location(
            name="東京都",
            name_en="tokyo",
            region=self.region,
            display_x=2,
            display_y=1,
            display_width=1,
            display_height=1,
        )

    def get_homepage_response(self, user=None):
        request = self.factory.get(reverse("homepage"), HTTP_HOST="localhost")
        request.user = user or AnonymousUser()
        return homepage(request)

    def test_anonymous_homepage_is_public_landing_page(self):
        response = self.get_homepage_response()

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("Start your map", body)
        self.assertIn(reverse("account_signup"), body)
        self.assertIn(reverse("account_login"), body)
        self.assertNotIn("/update/", body)
        self.assertNotIn("Share your map", body)

    def test_authenticated_homepage_renders_editable_map_and_share_link(self):
        create_entry(self.user, self.hokkaido, status="lived")

        response = self.get_homepage_response(user=self.user)
        body = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Click a prefecture on the map to update its status.", body)
        self.assertIn("What do the categories mean?", body)
        self.assertIn("Share your map", body)
        self.assertIn("/update/北海道", body)
        self.assertIn('class="lived location"', body)
        self.assertIn('class="none location"', body)

        token = signing.dumps(self.user.pk, salt=SHARE_MAP_SALT)
        self.assertIn(reverse("shared_map", args=[token]), body)

    def test_japanese_homepage_renders_localized_copy(self):
        with override("ja"):
            response = self.get_homepage_response(user=self.user)

        body = response.content.decode()
        self.assertIn("旅した都道府県の地図", body)
        self.assertIn("地図上の都道府県をクリックしてステータスを更新できます。", body)
        self.assertIn("カテゴリーの意味", body)
        self.assertIn("地図を共有", body)

    def test_shared_map_is_public_read_only_and_identifies_owner(self):
        create_entry(self.user, self.hokkaido, status="walked")
        create_entry(self.other_user, self.tokyo, status="stayed")
        token = signing.dumps(self.user.pk, salt=SHARE_MAP_SALT)

        request = self.factory.get(reverse("shared_map", args=[token]))
        request.user = AnonymousUser()
        response = shared_map(request, token)
        body = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Shared Travel Map", body)
        self.assertIn("This is kaylee's read-only shared map.", body)
        self.assertIn('class="walked location"', body)
        self.assertIn('class="none location"', body)
        self.assertIn("北海道 walked", body)
        self.assertIn("東京都 none", body)
        self.assertNotIn("/update/", body)
        self.assertNotIn("Click a prefecture on the map to update its status.", body)

    def test_shared_map_rejects_bad_token(self):
        request = self.factory.get(reverse("shared_map", args=["not-a-real-token"]))
        request.user = AnonymousUser()

        with self.assertRaises(Http404):
            shared_map(request, "not-a-real-token")

    def test_shared_map_renders_japanese_owner_copy(self):
        token = signing.dumps(self.user.pk, salt=SHARE_MAP_SALT)

        with override("ja"):
            request = self.factory.get(reverse("shared_map", args=[token]))
            request.user = AnonymousUser()
            response = shared_map(request, token)

        body = response.content.decode()
        self.assertIn("共有された旅の地図", body)
        self.assertIn("これはkayleeさんの閲覧専用の共有地図です。", body)


class UpdateLocationViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = create_user(username="kaylee")
        self.location = create_location(name="テスト県", name_en="testland")

    def test_update_page_requires_login(self):
        response = self.client.get(reverse("update", args=[self.location.name]))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("account_login"), response["Location"])

    def test_update_page_renders_prompt_buttons_and_bottom_category_guide(self):
        self.client.force_login(self.user)

        request = self.factory.get(reverse("update", args=[self.location.name]))
        request.user = self.user
        response = update_location(request, self.location.name)
        body = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Click a button to update the status for Testland prefecture.", body)
        self.assertIn('value="Lived"', body)
        self.assertLess(body.index('value="Lived"'), body.index("What do the categories mean?"))

    def test_update_page_renders_japanese_prompt(self):
        self.client.force_login(self.user)

        with override("ja"):
            request = self.factory.get(reverse("update", args=[self.location.name]))
            request.user = self.user
            response = update_location(request, self.location.name)

        body = response.content.decode()
        self.assertIn("テスト県のステータスを更新するには、ボタンをクリックしてください。", body)
        self.assertIn("カテゴリーの意味", body)

    def test_post_each_status_creates_or_updates_entry(self):
        self.client.force_login(self.user)

        for status in ["none", "lived", "stayed", "walked", "passed through"]:
            response = self.client.post(
                reverse("update", args=[self.location.name]),
                {"status": status},
            )

            self.assertRedirects(response, reverse("homepage"), fetch_redirect_response=False)
            self.assertEqual(
                LocationEntry.objects.get(user=self.user, location=self.location).status,
                status,
            )
            self.assertEqual(LocationEntry.objects.filter(user=self.user, location=self.location).count(), 1)
