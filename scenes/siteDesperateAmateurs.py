import scrapy
import re
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDesperateAmateursSpider(BaseSceneScraper):
    name = 'DesperateAmateurs'
    network = 'Desperate Amateurs'
    parent = 'Desperate Amateurs'
    site = 'Desperate Amateurs'

    start_urls = [
        'https://www.desperateamateurs.com'
    ]

    selector_map = {
        'title': '//div[@class="title_bar"]/comment()/following-sibling::text()',
        'description': '//div[@class="gallery_description"]/text()',
        'performers': '//td[contains(text(),"Featuring")]/following-sibling::td/a/text()',
        'date': '//td[@class="date"][1]/text()',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@class="movie_background"]/script[contains(text(),"picarr")][1]/text()',
        're_image': r'.*\"(.*?.jpg)\"',
        'tags': '//td[@class="plaintext"]/a[@class="model_category_link"]/text()',
        'trailer': '//div[@class="movie_background"]/script[contains(text(),"picarr")][1]/text()',
        're_trailer': r'.*\"(.*?.mp4)\".*',
        'external_id': r'id=(\d+)',
        'pagination': '/fintour/category.php?id=5&page=%s&s=d&'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//span[@class="update_title"]/a/@href').getall()
        for scene in scenes:
            scene = "https://www.desperateamateurs.com/fintour/" + scene
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)


    def get_date(self, response):
        if 'date' in self.get_selector_map():
            scenedate = self.get_element(response, 'date', 're_date')
            if scenedate:
                if isinstance(scenedate, list):
                    scenedate = scenedate[0]
                date_formats = self.get_selector_map('date_formats') if 'date_formats' in self.get_selector_map() else None
                scenedate = re.search(r'(\d{2}/\d{2}/\d{4})', scenedate)
                if scenedate:
                    scenedate = scenedate.group(1)
                return self.parse_date(self.cleanup_text(scenedate), date_formats=date_formats).isoformat()
        return self.parse_date('today').isoformat()
