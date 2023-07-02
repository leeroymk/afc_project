from unittest import TestCase
from django.test import Client


class TestConnection(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_page(self):
        # Тест соединения с главной страницей
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_news_page(self):
        # Тест соединения со страницей новостей
        response = self.client.get("/news/")
        self.assertEqual(response.status_code, 200)
