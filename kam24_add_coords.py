import json
import random
import os

OUTPUT_DIR = 'kam24'

with open('coords.json') as f:
    COORDS_DICT = json.load(f)


def get_coords():
    location, coords = random.choice(list(COORDS_DICT.items()))
    left, right = coords['left_down'], coords['right_up']
    lx, ly = float(left[0]), float(left[1])
    rx, ry = float(right[0]), float(right[1])

    x = random.uniform(lx, rx)
    y = random.uniform(ly, ry)

    return (location, x, y)


def main():
    if not os.path.exists(f'{OUTPUT_DIR}_coords'):
        os.makedirs(f'{OUTPUT_DIR}_coords')

    with open('ecowords.txt') as f_eco:
        for word in f_eco:
            word = word.strip()
            try:
                with open(f'{OUTPUT_DIR}/{word}.json') as f:
                    d = json.load(f)
            except:
                print(f'Word "{word}" not found in {OUTPUT_DIR}/')
                continue

            res = []
            for i in d:
                for news in i:
                    location, lat, lon = get_coords()
                    news['lat'] = lat
                    news['lon'] = lon
                    news['location'] = location
                    res.append(news)

            with open(f'{OUTPUT_DIR}_coords/{word.strip()}.json', 'w') as f:
                json.dump(res, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    main()
