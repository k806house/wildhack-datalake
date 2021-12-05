#!/usr/bin/python3

import json
import os
import random
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup

OUTPUT_DIR = 'kamtoday'

DATE_REPLACE = {
    'января': '01',
    'февраля': '02',
    'марта': '03',
    'апреля': '04',
    'мая': '05',
    'июня': '06',
    'июля': '07',
    'августа': '08',
    'сентября': '09',
    'октября': '10',
    'ноября': '11',
    'декабря': '12'
}

with open('coords.json') as f:
    COORDS_DICT = json.load(f)


def date_format(dt):
    if 'сегодня' in dt:
        return datetime.today().strftime('%d.%m.%Y')
    elif 'вчера' in dt:
        d = datetime.today() - timedelta(days=1)
        return d.strftime('%d.%m.%Y')
    elif 'позавчера' in dt:
        d = datetime.today() - timedelta(days=2)
        return d.strftime('%d.%m.%Y')

    dmy = dt.split(',')[0]
    day, month, year = dmy.split()
    month = DATE_REPLACE[month]
    return f'{day}.{month}.{year}'


def get_coords():
    location, coords = random.choice(list(COORDS_DICT.items()))
    left, right = coords['left_down'], coords['right_up']
    lx, ly = float(left[0]), float(left[1])
    rx, ry = float(right[0]), float(right[1])

    x = random.uniform(lx, rx)
    y = random.uniform(ly, ry)

    return (location, x, y)


def get_news(link):
    r = requests.get(f'https://kamtoday.ru{link}')
    soup = BeautifulSoup(r.text, 'lxml')
    datetime = soup.find('div', class_='news-date-time darkgray').text.strip()

    news_detail = soup.find('div', class_='news-detail')
    announce = news_detail.find('div', class_='name').text.strip()

    content = []
    for p_elm in news_detail.find_all('p'):
        content.append(p_elm.text.strip().replace(u'\xa0', u' '))

    location, lat, lon = get_coords()

    return {
        'date': date_format(datetime),
        'location': location,
        'lat': lat,
        'lon': lon,
        'title': announce,
        'text': '\n'.join(content)
    }


def parse_page(r, num):
    print(f'Parse page {num}')
    soup = BeautifulSoup(r.text, 'lxml')
    news_list = soup.find('div', class_='news-list')
    rows = news_list.find_all('div', class_='row')

    news_links = []
    for row in rows:
        for a_elm in row.find_all('a', class_='news-link'):
            ref = a_elm.attrs['href']
            news_links.append(ref)

    result_news = []
    for link in news_links:
        res = get_news(link)
        result_news.append(res)

    print(f'Finish parsing page {num}')
    #print(result_news)
    return result_news


def parse():
    page_counter = 1
    news_all_page = []
    base_url = 'https://kamtoday.ru/news/ecologics/'
    r = requests.get(base_url)
    news_all_page.extend(parse_page(r, page_counter))
    page_counter += 1

    while True:
        try:
            soup = BeautifulSoup(r.text, 'lxml')
            next_page = soup.find('a', class_='modern-page-next d-flex align-items-center')
            ref = next_page.attrs['href']

            next_url = f'https://kamtoday.ru{ref}'
            r = requests.get(next_url)
            news_all_page.extend(parse_page(r, page_counter))
            page_counter += 1
        except Exception as ex:
            if page_counter == 2:
                print('Only 1 page')
                print(ex)
            else:
                print(ex)
            break

    return news_all_page


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    news = parse()
    with open(f'{OUTPUT_DIR}/output2.json', 'w') as f:
        json.dump(news, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
