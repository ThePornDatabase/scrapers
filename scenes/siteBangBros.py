import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class BangBrosSpider(BaseSceneScraper):
    name = 'BangBros'
    network = 'Bang Bros'
    parent = 'Bang Bros'

    start_urls = [
        'https://bangbros.com/'
    ]

    selector_map = {
        'title': "//div[@class='ps-vdoHdd']//h1/text()",
        'description': "//div[@class='vdoDesc']/text()",
        'date': "",
        'image': '//img[@id="player-overlay-image"]/@src',
        'performers': "//div[@class='vdoAllDesc']//div[@class='vdoCast']//a[position()>1]/text()",
        'tags': "//div[@class='vdoTags']//a/text()",
        'external_id': r'/([A-Za-z0-9-_+=%]+)$',
        'trailer': '//video//source[contains(@src, "mp4") and not(contains(@src, "mpd")) and not(contains(@src, "m3u8"))]/@src',
        'pagination': '/videos/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath("//div[@class='videosPopGrls']//div[@class='echThumb']")
        for scene in scenes:
            date = scene.xpath(".//span[contains(@class, 'thmb_mr_cmn')][2]//span[@class='faTxt']/text()")
            if date:
                date = self.parse_date(date.get(), date_formats=['%b %d, %Y']).isoformat()
            else:
                date = self.parse_date('today').isoformat()

            link = self.format_link(response, scene.css('a::attr(href)').get())
            yield scrapy.Request(url=link, callback=self.parse_scene, meta={'date': date})

    def get_site(self, response):
        site = response.xpath(
            "//div[@class='vdoAllDesc']//div[@class='vdoCast']//a[1]/text()").get()
        if 'casting' in site:
            return 'Bang Bros Casting'
        if 'party of 3' in site.lower():
            return 'Party of Three'
        return site

    def get_id(self, response):
        external_id = response.xpath('//img[@id="player-overlay-image"]/@src')
        if external_id:
            external_id = re.search(r'shoots/(.*?)/', external_id.get())
            if external_id:
                return external_id.group(1)
        return super().get_id(response)
