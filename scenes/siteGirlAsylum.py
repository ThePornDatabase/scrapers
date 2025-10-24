import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGirlAsylumSpider(BaseSceneScraper):
    name = 'GirlAsylum'
    network = 'GirlAsylum'
    parent = 'GirlAsylum'
    site = 'GirlAsylum'

    start_urls = [
        'https://www.girlasylum.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '',
        'date': '//i[contains(@class, "clock")]/following-sibling::text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//article/div[@class="entry"]/a[contains(@href, "join")][1]/img/@src',
        'performers': '//li[contains(text(), "Model")]/a/text()',
        'tags': '//ul[contains(@class, "post-meta")]//li/a[contains(@href, "category")]/text()',
        'external_id': r'',
        'pagination': '/page/%s/',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//a[contains(@href, ".zip") and contains(@href, "avi")]/ancestor::article[contains(@id, "post-")]')
        for scene in scenes:
            sceneid = scene.xpath('./@id')
            if sceneid:
                sceneid = sceneid.get()
                meta['id'] = re.search(r'(\d+)', sceneid).group(1)

            origid = scene.xpath('.//a[contains(@href, ".zip") and not(contains(@href, "avi"))]/text()')
            meta['origid'] = ""
            if origid:
                origid = origid.get()
                origid = re.search(r'(.*)\.zip', origid).group(1)
                meta['origid'] = origid.upper()

            scene = scene.xpath('.//h2/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        meta = response.meta
        title = super().get_title(response)
        if meta['origid']:
            title = f"{meta['origid']}: {title}"
        return title
