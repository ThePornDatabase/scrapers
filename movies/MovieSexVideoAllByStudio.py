import re
import json
import scrapy
from slugify import slugify
import unidecode
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieSexVideoAllByStudioSpider(BaseSceneScraper):
    name = 'MovieSexVideoAllByStudio'

    start_urls = [
        'https://www.sexvideoall.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',  # Eromaxx
        'type': 'Movie',
    }

    headers = {'Content-Type': 'application/json'}

    studios = [
        {"id": 609, "name": "SG Video"}, # Scat Videos
        {"id": 502, "name": "Eromaxx"},
        {"id": 865, "name": "Czech"},
        {"id": 424, "name": "Purzel"},
        {"id": 148, "name": "MMV"},
        {"id": 145, "name": "Goldlight"},
        {"id": 323, "name": "Z-Faktor"},
        {"id": 185, "name": "Tabu"},
        {"id": 174, "name": "DBM"},
        {"id": 181, "name": "Inflagranti"},
        {"id": 221, "name": "Muschi Movie"},
        {"id": 330, "name": "Ribu Film"},
        {"id": 452, "name": "Telsev"},
        {"id": 187, "name": "Videorama"},
        {"id": 735, "name": "Belrose"},
        {"id": 307, "name": "EVS"},
        {"id": 541, "name": "Foxy Media"},
        {"id": 303, "name": "Herzog Video"},
        {"id": 182, "name": "MJP"},
        {"id": 667, "name": "Pervision"},
        {"id": 147, "name": "Puaka"},
        {"id": 295, "name": "Erotic Planet"},
        {"id": 2050, "name": "Movie Star"},
        {"id": 3317, "name": "Mia Bella"},
        {"id": 780, "name": "MVW.xxx"},
        {"id": 146, "name": "Magma Film"},
        {"id": 291, "name": "GMV"},
        {"id": 278, "name": "Fun Movies"},
        {"id": 736, "name": "Uschi Haller"},
        {"id": 920, "name": "Fantas P"},
        {"id": 3284, "name": "Love Arts"},
        {"id": 2060, "name": "Jodete Porn"},
        {"id": 2076, "name": "GB Media"},
        {"id": 401, "name": "Oftly Goldwin"},
        {"id": 479, "name": "Metabolic"},
        {"id": 454, "name": "Corrupt Media"},
        {"id": 532, "name": "Nebenan"},
        {"id": 294, "name": "Create-X"},
        {"id": 511, "name": "Cruel Media"},
        {"id": 601, "name": "Maximum Grind"},
        {"id": 522, "name": "Euro Extrem"},
        {"id": 243, "name": "Shots Video"},
        {"id": 563, "name": "Fick Tiv"},
        {"id": 179, "name": "Horny Heaven"},
        {"id": 128, "name": "Erotic Entertainment"},
        {"id": 319, "name": "Pleasure Verlag"},
        {"id": 503, "name": "21 Sextury Video"},
        {"id": 944, "name": "Teen X"},
        {"id": 483, "name": "Ultra Deca"},
    ]

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        link = "https://www.sexvideoall.com/main"
        yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        for studio in self.studios:
            meta['studio'] = studio['name']
            meta['studio_id'] = studio['id']
            link = f"https://www.asiacollection.net/api/item/getStudioCat/{meta['studio_id']}"
            yield scrapy.Request(link, callback=self.start_requests_3, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_3(self, response):
        meta = response.meta
        meta['categories'] = json.loads(response.text)
        meta['categories'] = meta['categories']['studiocate']
        meta['pagination'] = self.get_selector_map('pagination')
        meta['payload'] = {"cat": 0, "studio": meta['studio_id'], "subcat": 0, "email": "", "lan": "en", "ip": "66.85.229.220", "page": int(meta['page']), "size": 20, "sort": 4}
        meta['link'] = 'https://www.asiacollection.net/api/item/StudioCategory'
        yield scrapy.Request(meta['link'], callback=self.parse, method="POST", body=json.dumps(meta['payload']), meta=meta, headers=self.headers)

    def parse(self, response):
        meta = response.meta
        movies = self.get_movies(response)
        count = 0
        for movie in movies:
            count += 1
            yield movie

        page_json = json.loads(response.text)
        total_pages = page_json['totalPages']
        if 'page' in response.meta and response.meta['page'] < self.limit_pages and response.meta['page'] < total_pages:
            meta['page'] = meta['page'] + 1
            meta['payload']['page'] = meta['page']
            print(f"NEXT PAGE: {str(meta['page'])} of {total_pages} for Studio: {meta['studio']}:  The last page had: {count} items")
            yield scrapy.Request(meta['link'], callback=self.parse, method="POST", body=json.dumps(meta['payload']), meta=meta, headers=self.headers, cookies=self.cookies)

    def get_movies(self, response):
        meta = response.meta
        moviejson = json.loads(response.text)
        moviejson = moviejson['results']['cresults']
        for movie in moviejson:
            link = f"https://www.asiacollection.net/api/item/Getitem/{movie['id']}/x"
            yield scrapy.Request(link, callback=self.parse_movie, method="POST", meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_movie(self, response):
        meta = response.meta
        moviedata = json.loads(response.text)
        movie = moviedata['cresults']
        item = SceneItem()

        item['title'] = self.cleanup_title(unidecode.unidecode(movie['nameE'])).replace("&", "and")
        if movie['releaseDate']:
            item['date'] = self.parse_date(movie['releaseDate'], date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
        else:
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', movie['datum']).group(1)
        if "length" in movie and movie['length']:
            item['duration'] = str(int(movie['length']) * 60)
        else:
            item['duration'] = None
        item['description'] = movie['beschreibungE']
        if "No Regional Coding" in item['description']:
            item['description'] = ''
        item['id'] = movie['id']
        item['url'] = f"https://www.sexvideoall.com/item/{item['id']}/en/{slugify(item['title'])}"
        item['performers'] = []
        for performer in moviedata['pornstars']:
            item['performers'].append(performer['name'])
        item['site'] = meta['studio']
        item['parent'] = meta['studio']
        item['network'] = meta['studio']
        item['image'] = f"https://static.sexvideoall.com/SamplePhoto/{item['id']}.jpg"
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['back'] = f"https://static.sexvideoall.com/SamplePhoto/{item['id']}f.jpg"
        item['back_blob'] = self.get_image_blob_from_link(item['back'])
        item['type'] = "Movie"

        item['trailer'] = None
        item['tags'] = []
        for kat in movie['kat'].split(','):
            for genre in meta['categories']:
                if int(kat.strip()) == genre['id']:
                    if "European " in genre['kat']:
                        genre['kat'] = genre['kat'].replace("European ", "")
                        item['tags'].append("European")
                    if "3p" in genre['kat']:
                        genre['kat'] = "Threesome"
                    if "Cumshots" in genre['kat']:
                        genre['kat'] = "Cumshots"
                    if "Out Door" in genre['kat']:
                        genre['kat'] = "Outdoors"
                    if "Teens/College Girls" in genre['kat']:
                        genre['kat'] = "18+ Teens"
                    if "Nylon/Stocking" in genre['kat']:
                        genre['kat'] = "Stockings"
                    if "Extreme/Rough Sex" in genre['kat']:
                        genre['kat'] = "Rough Sex"
                    if "Women with Glasses" in genre['kat']:
                        genre['kat'] = "Glasses"
                    if "P.O.V." in genre['kat']:
                        genre['kat'] = "POV"
                    if "Cream Pie" in genre['kat']:
                        genre['kat'] = "Creampie"
                    if "WC" in genre['kat']:
                        genre['kat'] = "Bathroom"
                    item['tags'].append(genre['kat'])

        yield self.check_item(item, self.days)
