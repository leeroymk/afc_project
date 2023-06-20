import pandas as pd


def pandas_parser_table(table_url):
    src = pd.read_html(table_url, encoding='utf-8')
    table_data = src[1]
    dict_table = table_data.to_dict()

    # model_instances = [StatEpl(
    #     position=record[''],
    #     team=record['Команда'],
    #     matches=record['М'],
    #     win=record['В'],
    #     draw=record['Н'],
    #     loss=record['П'],
    #     scored=record['Заб'],
    #     conceded=record['Проп'],
    #     points=record['О'],
    #     season='2022/2023',
    # ) for record in dict_table]

    #   StatEpl.objects.bulk_create(model_instances)
    #   StatEpl.save()


table_url = 'https://www.sports.ru/epl/table/'

pandas_parser_table(table_url)
