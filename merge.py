import os
import json

from os import listdir
from os.path import isfile, join


def format_date(dt):
    _, m, y = dt.split('.')
    return f'{y}.{m}'


def format_date_output(dt):
    y, m = dt.split('.')
    return f'{m}.{y}'


def main():
    merged_news = []

    with open('kamtoday/output.json') as f:
        merged_news.extend(json.load(f))

    path = 'kam24'
    files = [f for f in listdir(path) if isfile(join(path, f))]
    for filename in files:
        with open(f'{path}/{filename}') as f:
            merged_news.extend(json.load(f))

    merged_news = sorted(merged_news, key=lambda d: format_date(d['date']))

    result = []
    dates = []
    cur_date = format_date(merged_news[0]['date'])
    tmp = []
    for news in merged_news:
        if format_date(news['date']) > cur_date:
            dates.append(format_date_output(cur_date))
            result.append(tmp)
            tmp = []
            cur_date = format_date(news['date'])
        else:
            tmp.append(news)

    if tmp:
        dates.append(format_date_output(cur_date))
        result.append(tmp)

    with open(f'dates.json', 'w') as f:
        json.dump(dates, f, indent=4, ensure_ascii=False)

    with open(f'data.json', 'w') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)



if __name__ == '__main__':
    main()