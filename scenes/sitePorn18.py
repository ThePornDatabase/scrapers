import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.utils.project import get_project_settings


class SitePorn18Spider(BaseSceneScraper):
    name = 'Porn18'
    network = 'Porn 18'
    parent = 'Porn 18'
    site = 'Porn 18'

    start_url = 'http://www.porn18.com/models/'

    selector_map = {
        'title': '//h2/text()',
        'description': '//div[@class="item"]/em/text()',
        'date': '',
        'image': '//div[@class="player-holder"]//img/@src',
        'performers': '//div[@class="item"]/a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="item" and contains(text(), "Categories")]/a/text()',
        'trailer': '//script[contains(text(), "video_url")]/text()',
        're_trailer': r'video_url.*?(http.*?\.mp4)',
        'external_id': r'videos/(\d+)/',
        'pagination': ''
    }

    def start_requests(self):
        settings = get_project_settings()

        meta = {}
        meta['page'] = self.page
        if 'USE_PROXY' in settings.attributes.keys():
            use_proxy = settings.get('USE_PROXY')
        else:
            use_proxy = None

        if use_proxy:
            print(f"Using Settings Defined Proxy: True ({settings.get('PROXY_ADDRESS')})")
        else:
            try:
                if self.proxy_address:
                    meta['proxy'] = self.proxy_address
                    print(f"Using Scraper Defined Proxy: True ({meta['proxy']})")
            except Exception:
                print("Using Proxy: False")

        yield scrapy.Request(url=self.start_url,
                             callback=self.get_model_pages,
                             meta=meta,
                             headers=self.headers,
                             cookies=self.cookies)

    def get_model_pages(self, response):
        meta = response.meta
        models = response.xpath('//a[@class="item" and contains(@href, "/models/")]/@href').getall()
        for model in models:
            yield scrapy.Request(url=self.format_link(response, model), callback=self.get_scenes, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item-inner"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        image = super().get_image(response)
        if not image or "contents" not in image:
            image = response.xpath('preview_url')
            if image:
                image = image.get()
                image = re.search(r'preview_url.*?(http.*?\.jpg)', image)
                if image:
                    image = self.format_link(response, image.group(1))
        return image
