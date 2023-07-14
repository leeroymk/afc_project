import logging

from django.core import management
from django.core.management.base import BaseCommand

from fwa.management.commands.utils import process_timer


class Command(BaseCommand):
    help = 'Master parser command'

    def add_arguments(self, parser):
        pass

    @process_timer
    def handle(self, *args, **options):

        logging_fwa = logging.getLogger(__name__)
        logging_fwa.info('Парсинг всей статистики...')

        management.call_command("parser_teams")
        management.call_command("parser_table_epl")
        management.call_command("parser_goals_epl")
        management.call_command("parser_assists_epl")
        management.call_command("parser_calendar")

        logging_fwa.info('Парсинг всей статистики завершен!')
