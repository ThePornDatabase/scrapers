import re
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MetArtNetworkSpider(BaseSceneScraper):
    name = 'MetArtNetwork'
    network = 'metart'

    start_urls = [
        "https://www.alsscan.com",
        # "https://www.eroticbeauty.com",
        "https://www.errotica-archives.com",
        "https://www.eternaldesire.com",
        "https://www.lovehairy.com",
        "https://www.metart.com",
        "https://www.metartx.com",
        "https://www.rylskyart.com",
        "https://www.sexart.com",
        "https://www.straplez.com",
        "https://www.stunning18.com",
        "https://www.thelifeerotic.com",
        "https://www.vivthomas.com",
        # 'https://www.hustlerunlimited.com',
        # 'https://www.barelylegal.com/'
    ]

    selector_map = {
        'external_id': 'movie\\/(.+)',
        'pagination': '/api/movies?galleryType=MOVIE&first=60&page=%s&staffSelectionHead=false&tabId&order=DATE&direction=DESC&type=MOVIE'
    }

    max_pages = 100

    def get_next_page_url(self, base, page):
        if "eroticbeauty" in base:
            pagination = '/api/updates?tab=stream&page=%s&direction=DESC&showPinnedGallery=true'
        else:
            pagination = self.get_selector_map('pagination')
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        movies = response.json()['galleries']
        for movie in movies:
            skip = False
            if "eroticbeauty" in response.url:
                if movie['type'] != "MOVIE":
                    skip = True
            res = re.search('movie/(\\d+)/(.+)', movie['path'])
            if not skip:
                yield scrapy.Request(url=self.format_link(response, '/api/movie?name=' + res.group(2) + '&date=' + res.group(1)), callback=self.parse_scene, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        movie = response.json()

        item = SceneItem()
        item['title'] = movie['name']
        item['description'] = movie['description']
        item['performers'] = []

        for performer in movie['models']:
            item['performers'].append(performer['name'])

        if 'coverCleanImagePath' in movie:
            item['image'] = movie['coverCleanImagePath']

        if 'splashImagePath' in movie:
            item['image'] = movie['splashImagePath']
        else:
            item['image'] = None

        if 'hustler' in response.url or "barelylegal" in response.url:
            item['image'] = 'https://cdn-hustlernetwork.metartnetwork.com/' + movie['media']['siteUUID'] + item['image']
        elif 'lovehairy' in response.url or 'straplez' in response.url or 'alsscan' in response.url:
            item['image'] = 'https://cdn.metartnetwork.com/' + movie['siteUUID'] + movie['splashImagePath']
        else:
            item['image'] = self.format_link(response, item['image'])

        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['duration'] = ''
        if "runtime" in movie:
            if movie['runtime'] > 60:
                item['duration'] = movie['runtime']

        item['date'] = self.parse_date(movie['publishedAt']).isoformat()
        item['tags'] = movie['tags']
        # ~ item['trailer'] = self.format_url(response.url, '/api/m3u8/' + movie['UUID'] + '.m3u8')
        item['trailer'] = ""

        item['site'] = self.get_site(response)
        item['url'] = self.format_link(response, movie['path']).replace(" ", "%20")
        item['network'] = self.network
        item['parent'] = self.get_parent(response)
        res = re.search('movie/(\\d+)/(.+)', movie['path'])
        item['id'] = res.group(1) + "_" + res.group(2)

        yield self.check_item(item, self.days)
