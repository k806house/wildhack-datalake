#!/usr/bin/python3

import json
import os

import requests
from bs4 import BeautifulSoup

INPUT_WORDS_FILE = 'ecowords.txt'
OUTPUT_DIR = 'kam24'


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


def date_format(day, date):
    month_and_year = date.split(',')[0]
    month, year = month_and_year.split()
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
    r = requests.get(f'https://kam24.ru{link}')
    soup = BeautifulSoup(r.text, 'lxml')
    day = soup.find('span', class_='day').text.strip()
    date = soup.find('span', class_='data-in').text.strip()
    
    announce = soup.find('div', class_='announce').b.text.strip()
    content_news = soup.find_all('div', class_='contentNews')

    content = []
    for i in content_news:
        for p_elm in i.find_all('p'):
            content.append(p_elm.text)

    content = content[:-1]

    location, lat, lon = get_coords()

    return {
        'date': date_format(day, date),
        'location': location,
        'lat': lat,
        'lon': lon,
        'title': announce,
        'text': '\n'.join(content)
    }


def parse_page(r, num):
    print(f'Parse page {num}')
    soup = BeautifulSoup(r.text, 'lxml')
    news = soup.find_all('span', class_='hd')

    news_links = []
    for preview in news:
        for a_elm in preview.find_all('a'):
            ref = a_elm.attrs['href']
            if 'about_us' not in ref:
                news_links.append(ref)

    result_news = []
    for link in news_links:
        res = get_news(link)
        result_news.append(res)

    print(f'Finish parsing page {num}')
    return result_news


def parse(search_word):
    page_counter = 1
    news_all_page = []
    base_url = 'https://kam24.ru/Content/news/search'
    r = requests.get(base_url, params={'search': search_word})
    news_all_page.extend(parse_page(r, page_counter))
    page_counter += 1

    prev_ref = ''
    while True:
        try:
            soup = BeautifulSoup(r.text, 'lxml')
            next_page = soup.find('li', class_='next')
            ref = next_page.a.attrs['href']

            if prev_ref == ref:
                break

            prev_ref = ref
            next_url = f'https://kam24.ru{ref}'
            r = requests.get(next_url)
            news_all_page.extend(parse_page(r, page_counter))
            page_counter += 1
        except Exception as ex:
            if page_counter == 2:
                print('Only 1 page')
            else:
                print(ex)
            break

    return news_all_page


def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(INPUT_WORDS_FILE) as f:
        for word in f:
            print(f'Proccesing: {word}')
            word = word.strip()
            news = parse(word)
            with open(f'{OUTPUT_DIR}/{word.replace("", "_")}.json', 'w') as f:
                json.dump(news, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
