import re
import scrapy
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'alphamales-toolbox': 'Alpha Males Toolbox',
        'aplphamales-2-0': 'Alpha Males 2.0',
        'men-of-the-world': 'Men of the World',
        'blue-blake': 'Blue Blake',
        'hardbritladse': 'Hard Brit Lads',
        'hot-spunks-studios': 'Hot Spunk Studios'
    }
    return match.get(argument, argument)


class SiteAlphaMales(BaseSceneScraper):
    name = 'AlphaMales'
    network = 'Alpha Males'

    url = 'https://www.alphamales.com'

    paginations = [
        # ~ '/en/videos/alphamales/?page=%s',
        '/en/videos/alphamales-toolbox/?page=%s',
        '/en/videos/alphamales/?page=%s',
        '/en/videos/men-of-the-world/?page=%s',
        '/en/videos/blue-blake/?page=%s',
        '/en/videos/hardbritlads/?page=%s',
        '/en/videos/cazzo/?page=%s',
        '/en/videos/hot-spunks-studios/?page=%s'
    ]

    selector_map = {
        'title': '//div[contains(@class, "text-center")]/h1/text()',
        'description': '//div[contains(@class, "col-12")]/h2/text()',
        'date': '//script[contains(text(), "datePublished")]/text()',
        're_date': r'datePublished.*?(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[contains(@class, "models-list-img")]/a/div[contains(@class, "text")]/text()',
        'tags': '//div[contains(@class, "text-center")]//h3[contains(@class, "h120")]/text()',
        'external_id': r'detail/(\d+)-',
        'pagination': '/?page=%s'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination):
        if int(page) == 1:
            url = url + re.search(r'(.*)/', pagination).group(1)
            print(url)
            return url
        page = str(int(page) - 1)
        return self.format_url(url, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"video-gallery")]/a[contains(@href, "en/videos/detail")][1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        meta = response.meta
        site = re.search(r'videos/(.*?)/', meta['pagination']).group(1)
        return match_site(site)

    def get_parent(self, response):
        meta = response.meta
        parent = re.search(r'videos/(.*?)/', meta['pagination']).group(1)
        return match_site(parent)

    def get_duration(self, response):
        duration = response.xpath('//i[contains(@class, "fa-clock")]/following-sibling::text()[1]')
        if duration:
            duration = duration.get()
            duration = "".join(duration).replace("\n", "").replace("\t", "").replace(" ", "").lower()
            duration = re.search(r'(\d+)min', duration)
            if duration:
                duration = duration.group(1)
                duration = str(int(duration) * 60)
                return duration
        return None

    def get_performers_data(self, response):
        performers = super().get_performers(response)
        performers_data = []
        for performer in performers:
            performer = string.capwords(performer.strip())
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['network'] = "AlphaMales"
            performer_extra['site'] = "AlphaMales"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Male"
            performers_data.append(performer_extra)
        return performers_data
