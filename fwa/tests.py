from unittest import TestCase
from django.test import Client
from fwa.models import Teams


class TestConnection(TestCase):
    def setUp(self):
        self.client = Client()

    if Teams.objects.exists():

        # Тест соединения с главной страницей
        def test_index_page(self):
            for team in Teams.objects.filter(league='АПЛ'):
                response = self.client.get(f"/?team_name={team.name}")
                self.assertEqual(response.status_code, 200)

        # Тест соединения со страницей новостей
        def test_news_page(self):
            for team in Teams.objects.filter(league='АПЛ'):
                response = self.client.get(f"/news/?team_name={team.name}")
                self.assertEqual(response.status_code, 200)

        # Тест соединения со страницей статистики
        def test_stats_page(self):
            for team in Teams.objects.filter(league='АПЛ'):
                response = self.client.get(f"/stats/?team_name={team.name}")
                self.assertEqual(response.status_code, 200)

        # Тест соединения со страницей бомбардиров
        def test_goalscorers_page(self):
            for team in Teams.objects.filter(league='АПЛ'):
                response = self.client.get(f"/goalscorers/?team_name={team.name}")
                self.assertEqual(response.status_code, 200)

        # Тест соединения со страницей ассистентов
        def test_assistants_page(self):
            for team in Teams.objects.filter(league='АПЛ'):
                response = self.client.get(f"/assistants/?team_name={team.name}")
                self.assertEqual(response.status_code, 200)

        # Тест соединения со страницей календаря
        def test_calendar_page(self):
            for team in Teams.objects.filter(league='АПЛ'):
                response = self.client.get(f"/calendar/?team_name={team.name}")
                self.assertEqual(response.status_code, 200)
