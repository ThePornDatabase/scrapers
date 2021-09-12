import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class AmateurAllureSpider(BaseSceneScraper):
    name = 'AmateurAllure'
    network = 'Amateur Allure'
    parent = 'Amateur Allure'
    site = 'Amateur Allure'

    start_urls = [
        'https://www.amateurallure.com'
    ]

    selector_map = {
        'title': '//span[@class="title_bar_hilite"]/text()',
        'date': '//div[@class="cell update_date"]/text()',
        'description': '//span[@class="update_description"]/text()',
        'image': '',  # images not on site
        'performers': '//span[@class="update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': 'scenes/(.+)\\.html',
        'trailer': '',
        'pagination': '/tour/updates/page_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_thumbnail"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene)

    def get_image(self, response):
        return ''

    def get_trailer(self, response):
        trailer = response.xpath('//script[contains(text(),".mp4")]').get()
        if trailer:
            trailer = re.search(r'\"(\/tour.*720(?:.{1,4})?.mp4)\"', trailer).group(1)
            if trailer:
                return "https://www.amateurallure.com/" + trailer

        return ''

    def get_site(self, response):
        return "Amateur Allure"
