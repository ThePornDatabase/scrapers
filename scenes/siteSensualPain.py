import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteSensualPainSpider(BaseSceneScraper):
    name = 'SensualPain'
    network = 'Sensual Pain'
    parent = 'Sensual Pain'
    site = 'Sensual Pain'

    start_urls = [
        'https://www.sensualpain.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//div[@class="box video_detail"]/p/text()',
        'date': '',
        'image': '//video/@poster',
        'performers': '',
        'tags': '//strong[contains(text(), "Tags:")]/following-sibling::text()',
        'external_id': r'.*videos/(.*?)/',
        'trailer': '//video/source/@src',
        'pagination': '/pag_all.php?action=most_recent&pag=%s&c_i=0&s_i=&m_i=&k_word=&s_b=&featured=&latest_videos=1&amp;section=&view_type=view_thumbs'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"newthumbdesigns")]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
