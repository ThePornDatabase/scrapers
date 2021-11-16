import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class JimSlipSpider(BaseSceneScraper):
    name = 'JimSlip'
    network = 'JimSlip'

    start_urls = ['https://www.jimslip.com/updates.php']

    selector_map = {
        'title': "b font::text",
        'description': "div.textarea::text",
        'performers': ".has-text-white-ter a.is-dark::text",
        'external_id': 'slug=(.+)',
        'trailer': '',
        'tags': '',
        'image': 'img[hspace]::attr(src)',
        'pagination': '/updates.php?page=%s'
    }

    max_pages = 200

    def get_scenes(self, response):
        scenes = response.css(
            "[width] > tbody > tr > td > table > tbody > tr > td")
        for scene in scenes:
            link = scene.css('a::attr(href)').get()
            meta = {}
            if scene.css('td.gray::text').get():
                text = scene.css('td.gray::text').get().strip().replace(
                    'added ', '').replace('.', '-')
                meta['date'] = self.parse_date(text.strip(), date_formats=['%d.%m.%Y']).isoformat()
            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)
