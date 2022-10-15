import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy.utils.project import get_project_settings


class SiteRiggsFilmsSpider(BaseSceneScraper):
    name = 'RiggsFilms'
    network = 'Riggs Films'
    parent = 'Riggs Films'
    site = 'Riggs Films'

    start_urls = [
        'https://riggsfilms.com',
    ]

    selector_map = {
        'title': '//span[@class="entry-title"]/text()',
        'description': '//h1/../following-sibling::div[contains(@class, "fusion-text")]/p[1]/text()',
        'date': '//meta[@property="article:published_time"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'date_formats': ['%Y-%m-%d'],
        'image': '//meta[@property="og:image"][1]/@content',
        'performers': '//strong[contains(text(), "Starring")]/a/text()',
        'tags': '',
        'duration': '//strong[contains(text(), "Duration")]/following-sibling::text()[1]',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'type': 'Scene',
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

        link = 'https://riggsfilms.com/scenes'
        yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//h4/following-sibling::a[@class="fusion-link-wrapper"]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
