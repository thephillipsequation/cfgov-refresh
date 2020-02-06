from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase, override_settings


class WagtailAPITests(TestCase):
    # Flag is always enabled in non-Production environments
    def test_api_urls_enabled_when_flag_enabled(self):
        response = self.client.get('/api/v2/pages/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/v2/documents/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/api/v2/images/')
        self.assertEqual(response.status_code, 200)

    def test_api_filters_pages_by_type(self):
        response = self.client.get('/api/v2/pages/?type=v1.LandingPage')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/api/v2/pages/?type=BogusPage')
        self.assertEqual(response.status_code, 400)
