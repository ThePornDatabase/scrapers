import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class HushpassSpider(BaseSceneScraper):
    name = 'Hushpass'
    network = "Hushpass"
    parent = "Hushpass"

    start_urls = [
        'https://hushpass.com'
    ]

    selector_map = {
        'title': '//meta[@name="twitter:title"]/@content',
        'description': '//h3[contains(text(),"Description")]/following-sibling::text()',
        'date': '//div[@class="update-info-row"]/strong[contains(text(),"Released")]/following-sibling::text()',
        'image': '//div[@class="player-thumb"]/img[@class="update_thumb thumbs stdimage"]/@src0_1x',
        'performers': '//div[@class="update-info-block models-list-thumbs"]/ul/li/a/span/text()',
        'tags': '//div[@class="update-info-block"]/ul[@class="tags"]/li/a/text()',
        'external_id': '.*\\/(.*?)\\.html',
        'trailer': '//script[contains(text(),"video_content")]',
        'pagination': '/t1/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            '//div[@class="content-div"]/h4/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(
                response, self.get_selector_map('trailer')).get()
            if trailer:
                trailer = "https://hushpass.com" + \
                    re.search('src=\"(.*.mp4)\"', trailer).group(1).strip()
                return trailer.replace(" ", "%20")
        return ''
