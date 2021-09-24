import scrapy
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper


class BangBrosSpider(BaseSceneScraper):
    name = 'BangBros'
    network = 'Bang Bros'

    start_urls = [
        'https://bangbros.com/'
    ]

    selector_map = {
        'title': "//div[@class='ps-vdoHdd']//h1/text()",
        'description': "//div[@class='vdoDesc']/text()",
        # 'date': "//div[contains(@class, 'stat')]//span[contains(text(),'Date:')]/following-sibling::span/text()",
        'image': '//img[@id="player-overlay-image"]/@src',
        'performers': "//div[@class='vdoAllDesc']//div[@class='vdoCast']//a[position()>1]/text()",
        'tags': "//div[@class='vdoTags']//a/text()",
        'external_id': r'\/([A-Za-z0-9-_+=%]+)$',
        'trailer': '//video//source/@src',
        'pagination': '/videos/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[@class='videosPopGrls']//div[@class='echThumb']")
        for scene in scenes:
            meta = {}

            if scene.xpath(
                    "//span[contains(@class, 'thmb_mr_cmn')][2]//span[@class='faTxt']/text()") is not None:
                date = scene.xpath(
                    "//span[contains(@class, 'thmb_mr_cmn')][2]//span[@class='faTxt']/text()").get()
                meta['date'] = dateparser.parse(date).isoformat()

            link = self.format_link(response, scene.css('a::attr(href)').get())
            yield scrapy.Request(url=link, callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath(
            "//div[@class='vdoAllDesc']//div[@class='vdoCast']//a[1]/text()").get()
        if 'casting' in site:
            return 'Bang Bros Casting'

        return site

    def get_trailer(self, response):
        return 'https:' + \
            self.process_xpath(
                response, self.get_selector_map('trailer')).get()
