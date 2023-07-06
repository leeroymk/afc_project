from django.core import management
from django.core.management.base import BaseCommand
import logging
import sys


class Command(BaseCommand):
    help = 'Master parser command'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
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

        management.call_command("parser_table_epl")
        management.call_command("parser_goals_epl")
        management.call_command("parser_assists_epl")
