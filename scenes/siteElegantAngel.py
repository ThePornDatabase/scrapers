import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.helpers.http import Http


class SiteElegantAngelSpider(BaseSceneScraper):
    name = 'ElegantAngel'
    network = 'Elegant Angel'
    parent = 'Elegant Angel'
    site = 'Elegant Angel'

    start_url = 'https://www.elegantangel.com'

    paginations = [
        '/watch-newest-elegant-angel-clips-and-scenes.html?page=%s&hybridview=member',
        '/watch-exclusive-elegant-angel-scenes.html?page=%s&hybridview=member',
    ]

    cookies = [{"name": "ageConfirmed", "value": True}]

    selector_map = {
        'title': '//h1[@class="description"]/text()',
        'description': '//h1[@class="description"]/text()',
        'date': '//span[contains(text(), "Released:")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="video-performer"]/a/span/span/text()',
        'tags': '//span[contains(text(), "Tags:")]/following-sibling::a/text()',
        'trailer': '',
        'external_id': r'/(\d{2,8})/',
        'pagination': '/watch-newest-elegant-angel-clips-and-scenes.html?page=%s&hybridview=member'
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

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            link = self.start_url
            yield scrapy.Request(url=self.get_next_page_url(link, self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

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

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="scene-preview-container"]')
        for scene in scenes:
            image = scene.xpath('./a/img/@src')
            if image:
                image = image.get()
                image = re.search(r'.*/(\d+_\d+)', image)
                if image:
                    image = f"https://caps1cdn.adultempire.com/r/9701/1280/{image.group(1)}_1280c.jpg"
                    image_blob = self.get_image_blob_from_link(image)
                    if image_blob:
                        meta['image'] = image
                        meta['image_blob'] = image_blob

            scene = scene.xpath('./a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = super().get_title(response)
        if title:
            if "Scene" in title:
                subtitle = response.xpath('//h1[@class="description"]/following-sibling::p/a/text()').get()
                title = string.capwords(f"{subtitle.strip()} - {title}")
            return title
        return ""

    def get_image_from_link(self, image):
        if image:
            req = Http.get(image, verify=False)
            if req and req.ok:
                return req.content
        return None
