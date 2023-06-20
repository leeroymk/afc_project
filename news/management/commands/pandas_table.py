import pandas as pd
from models import StatEpl


def pandas_parser_table(table_url):
    src = pd.read_html(table_url, encoding='utf-8')
    table_data = src[1]
    dict_table = table_data.to_dict()

    model_instances = [
       StatEpl(
        position=int(record['']),
        team=record['Команда'],
        matches=int(record['М']),
        win=int(record['В']),
        draw=int(record['Н']),
        loss=int(record['П']),
        scored=int(record['Заб']),
        conceded=int(record['Проп']),
        points=int(record['О']),
        season='2022/2023',
        ) for record in dict_table]

    migr = StatEpl.objects.bulk_create(model_instances)
    migr.save()


table_url = 'https://www.sports.ru/epl/table/'

pandas_parser_table(table_url)
