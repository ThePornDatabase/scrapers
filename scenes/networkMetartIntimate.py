import re
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MetArtIntimateNetworkSpider(BaseSceneScraper):
    name = 'MetArtNetworkIntimate'
    network = 'metart'

    start_urls = [
        "https://www.metart.com",
    ]

    selector_map = {
        'external_id': 'movie\\/(.+)',
        'pagination': '/api/movies?galleryType=MOVIE&first=60&page=%s&intimateSelectionOnly=true&order=DATE&direction=DESC&type=MOVIE'
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

        item['image'] = 'https://cdn.metartnetwork.com/' + movie['siteUUID'] + item['image']

        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['duration'] = ''
        if "runtime" in movie:
            if movie['runtime'] > 60:
                item['duration'] = movie['runtime']

        item['date'] = self.parse_date(movie['publishedAt']).strftime('%Y-%m-%d')
        item['tags'] = movie['tags']
        item['trailer'] = self.format_url(
            response.url, '/api/m3u8/' + movie['UUID'] + '.m3u8')
        item['site'] = self.get_site(response)
        item['url'] = self.format_link(response, movie['path'])
        item['network'] = self.network
        item['parent'] = self.get_parent(response)
        res = re.search('movie/(\\d+)/(.+)', movie['path'])
        item['id'] = res.group(1) + "_" + res.group(2)

        days = int(self.days)
        if days > 27375:
            filterdate = "0000-00-00"
        else:
            filterdate = date.today() - timedelta(days)
            filterdate = filterdate.strftime('%Y-%m-%d')

        if self.debug:
            if not item['date'] > filterdate:
                item['filtered'] = "Scene filtered due to date restraint"
            print(item)
        else:
            if filterdate:
                if item['date'] > filterdate:
                    yield item
            else:
                yield item
