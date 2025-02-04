import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class SiteHungarianHoneysSpider(BaseSceneScraper):
    name = 'HungarianHoneys'
    network = 'Hungarian Honeys'
    parent = 'Hungarian Honeys'
    site = 'Hungarian Honeys'

    start_urls = [
        'https://www.hungarianhoneys.com',
    ]

    # ~ cookies =

    selector_map = {
        'title': '//article/section/div/div/div[@class="title-block"]/h2[@class="section-title"]/text()',
        'description': '//h3[contains(text(), "Description")]/following-sibling::text()',
        'date': '//h3[contains(text(), "Video")]/following-sibling::div[1]//strong[contains(text(), "Released")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[contains(@class, "player-window-play")]/following-sibling::img/@src0_1x',
        'performers': '//div[contains(@class, "models-list")]/ul/li/a/span/text()',
        'tags': '//h3[contains(text(), "Tags:")]/following-sibling::ul/li/a/text()',
        'duration': '//h3[contains(text(), "Video")]/following-sibling::div[1]//strong[contains(text(), "Runtime")]/following-sibling::text()',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        print(self.cookies)
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videothumb")]')
        for scene in scenes:
            sceneid = scene.xpath('./@class')
            if sceneid:
                sceneid = sceneid.get()
                meta['id'] = re.search(r'(\w\d+)_', sceneid).group(1)
            scene = scene.xpath('./a[1]/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
