import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class MovieExcaliburFilmsSpider(BaseSceneScraper):
    name = 'MovieExcaliburFilms'

    start_urls = [
        'https://www.excaliburfilms.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '//h1/following-sibling::table[1]//font[contains(text(), "Released:")]/following-sibling::font[1]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//h1/following-sibling::table[1]//img[contains(@src, "reviews")]/@src',
        'performers': '//h1/following-sibling::table[1]//font[contains(text(), "Starring:")]/following-sibling::font[1]/a/text()',
        'tags': '//font[contains(text(), "Fetish:")]/following-sibling::a/text()',
        'director': '//h1/following-sibling::table[1]//font[contains(text(), "Director:")]/following-sibling::a[1]/text()',
        'external_id': r'.*/(\w+?)_.*',
        'pagination': '/adultdvdmovies.htm?pagenum=1&page=1&sortBy=date&searchCT=ALL&searchSN=&searchST=&searchKW=&searchWord=&letterIn=&priceIn=All&searchFor=&jumpTo=1&PaginationPage=%s',
        'type': 'Scene',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@class, "searchTitle18")]')
        for scene in scenes:
            meta['title'] = scene.xpath('./text()').get()
            meta['type'] = "Movie"
            meta['store'] = "Excalibur Films"

            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//h1/following-sibling::table[1]//font[contains(text(), "By:")]/following-sibling::a[1]/text()')
        if site:
            site = site.get()
        else:
            site = "Excalibur Films"
        return site

    def get_parent(self, response):
        return self.get_site(response)

    def get_network(self, response):
        return self.get_site(response)

    def get_image(self, response):
        image = super().get_image(response)
        if "dvd_" in image:
            image = re.search(r'(.*)/(.*?)$', image)
            image = f"{image.group(1)}/largemoviepic/{image.group(2)}"
        return image

    def get_back_image(self, response):
        image = self.get_image(response)
        if re.search(r'(.*)(\.\w{3,4})$', image):
            image = re.search(r'(.*)(\.\w{3,4})$', image)
            image = f"{image.group(1)}-b{image.group(2)}"
            return image
        return ""

    def get_duration(self, response):
        duration = response.xpath('//h1/following-sibling::table[1]//font[contains(text(), "Run Time:")]/following-sibling::font[1]/text()')
        if duration:
            duration = re.sub(r'[^a-z0-9]+', '', duration.get())
            if "min" in duration:
                duration = re.search(r'(\d+)', duration)
                if duration:
                    duration = str(int(duration.group(1)) * 60)
                    return duration
        return ""
