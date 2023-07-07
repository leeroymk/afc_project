from django.core import management
from django.core.management.base import BaseCommand
import logging


class Command(BaseCommand):
    help = 'Master parser command'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        logging_fwa = logging.getLogger(__name__)
        logging_fwa.info('Парсинг всей статистики...')

        management.call_command("parser_table_epl")
        management.call_command("parser_goals_epl")
        management.call_command("parser_assists_epl")

        logging_fwa.info('Парсинг всей статистики завершен!')
