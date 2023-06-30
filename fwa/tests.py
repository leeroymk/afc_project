import logging
import sys
from unittest import TestCase

from django.test import Client
from django.db.utils import OperationalError


root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

logging.basicConfig(level=logging.INFO,
                    filename='log_parsing.log',
                    format="[%(asctime)s] %(levelname)s - %(funcName)s: %(lineno)d - %(message)s",
                    datefmt='%H:%M:%S',
                    )


class TestConnection(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_page(self):
        # Тест соединения с главной страницей
        try:
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
        except OperationalError as er:
            logging.error(f'Connection issues at index page: {er}')

    def test_news_page(self):
        # Тест соединения со страницей новостей
        try:
            response = self.client.get("/news/")
            self.assertEqual(response.status_code, 200)
        except OperationalError as er:
            logging.error(f'Connection issues at news page: {er}')

    logging.info('Start testing connection...')
