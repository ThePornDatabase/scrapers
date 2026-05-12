import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class MovieErotikSpider(BaseSceneScraper):
    name = 'MovieDVDErotikByStudio'
    network = 'Erotik'

    start_urls = [
        'https://api.dvderotik.com',
    ]

    selector_map = {
        'description': '//div[@class="details-teaser"]/div/p/text()',
        'date': '',
        'performers': '//div[@class="star-grid-element"]//div[@class="star-image"]/a/div/div/div/span/text()',
        'tags': '//section[contains(@class, "details-movie")]//div[@class="inner-wrapper"]//div[@class="details-element"]/h4[contains(text(), "Categories")]/following-sibling::a/text()',
        'external_id': r'',
        'pagination': '',
        'type': 'Movie',
    }

    pagination = {
        'GGG': '/dvd/search/movies?filter[studio][]=99&itemsPerPage=48&page=%s&source=moviesoverview',
        'Deutscheland Porno': '/dvd/search/movies?filter[studio][]=157&itemsPerPage=48&page=%s&source=moviesoverview',
        'Mannermagnet': '/dvd/search/movies?filter[studio][]=441&itemsPerPage=48&page=%s&source=moviesoverview',
        '666': '/dvd/search/movies?filter[studio][]=111&itemsPerPage=48&page=%s&source=moviesoverview',
        'Aische Perverse': '/dvd/search/movies?filter[studio][]=784&itemsPerPage=48&page=%s&source=moviesoverview',
        'AlexD': '/dvd/search/movies?filter[studio][]=9&itemsPerPage=48&page=%s&source=moviesoverview',
        'Amateur Check In': '/dvd/search/movies?filter[studio][]=440&itemsPerPage=48&page=%s&source=moviesoverview',
        'Anny Aurora': '/dvd/search/movies?filter[studio][]=1498&itemsPerPage=48&page=%s&source=moviesoverview',
        'Anstoss': '/dvd/search/movies?filter[studio][]=1679&itemsPerPage=48&page=%s&source=moviesoverview',
        'Blue Movie': '/dvd/search/movies?filter[studio][]=1487&itemsPerPage=48&page=%s&source=moviesoverview',
        'Color Climax': '/dvd/search/movies?filter[studio][]=724&itemsPerPage=48&page=%s&source=moviesoverview',
        'Create-X': '/dvd/search/movies?filter[studio][]=1704&itemsPerPage=48&page=%s&source=moviesoverview',
        'Danger Women': '/dvd/search/movies?filter[studio][]=1416&itemsPerPage=48&page=%s&source=moviesoverview',
        'Gang Bang Amateure': '/dvd/search/movies?filter[studio][]=605&itemsPerPage=48&page=%s&source=moviesoverview',
        'MMV': '/dvd/search/movies?filter[studio][]=87&itemsPerPage=48&page=%s&source=moviesoverview',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.57',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 4,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        studio = self.settings.get('STUDIO')
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, studio), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, base, page, studio=None):
        return self.format_url(base, self.pagination.get(studio) % page)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = json.loads(response.text)
        for movie in jsondata['movies']:
            meta['id'] = movie['itemNumber']
            meta['image'] = movie['src']['default']
            # ~ meta['duration'] = movie['durationSeconds']
            if "studio" in movie and movie['studio']:
                if "name" in movie['studio'] and movie['studio']['name']:
                    meta['site'] = movie['studio']['name']
                    meta['studio'] = meta['site']
                    meta['parent'] = meta['site']
                    meta['network'] = meta['site']
            if movie['name']['en']:
                meta['title'] = movie['name']['en']
            else:
                meta['title'] = movie['name']['de']
            if movie['directors']:
                if "name" in movie['directors'][0] and movie['directors'][0]['name']:
                    meta['directors'] = movie['directors'][0]['name']
            if len(movie['href']['en'].strip()) > 1:
                meta['url'] = "https://en.erotik.com/" + movie['href']['en']
                yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)
            # ~ print(meta)

    def get_date(self, response):
        prod_year = response.xpath('//h4[contains(text(),"Release")]/following-sibling::p/text()')
        if prod_year:
            prod_year = prod_year.get().strip()
            prod_year = re.sub(r'[^0-9]', '', prod_year)
        if not prod_year:
            prod_year = response.xpath('//h4[contains(text(),"Production")]/following-sibling::p/text()')
            if prod_year:
                prod_year = prod_year.get().strip()
                prod_year = re.sub(r'[^0-9]', '', prod_year)

        if prod_year:
            prod_date = f"{prod_year}-01-01"
            return prod_date
        return None

    def get_tags(self, response):
        tags = super().get_tags(response)
        if tags:
            tags2 = tags.copy()
            for tag in tags2:
                matches = ['hour', 'uhd', 'avn', 'award', 'best', 'recommended', 'feature']
                if any(x in tag.lower() for x in matches):
                    tags.remove(tag)
            tags = list(map(lambda x: x.strip().title(), tags))

        return tags
