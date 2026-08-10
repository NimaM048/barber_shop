from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_homepage_renders_primary_conversion_flow(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="hero-heading"', count=1)
        self.assertContains(response, 'id="services"', count=1)
        self.assertContains(response, 'id="gallery"', count=1)
        self.assertContains(response, reverse("appointments:create"))
        self.assertContains(response, reverse("catalog:list"))
        self.assertContains(response, reverse("consultations:hub"))

    def test_homepage_keeps_accessible_landmarks_and_metadata(self):
        response = self.client.get(reverse("core:home"))

        self.assertContains(response, '<html lang="fa" dir="rtl">')
        self.assertContains(response, 'aria-labelledby="hero-heading"')
        self.assertContains(response, 'aria-labelledby="gallery-heading"')
        self.assertContains(response, 'type="application/ld+json"')
