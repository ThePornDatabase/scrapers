import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

class SiteSpermCocktailSpider(BaseSceneScraper):
    name = 'SpermCocktail'
    network = 'Sperm Cocktail'
    parent = 'Sperm Cocktail'
    site = 'Sperm Cocktail'

    start_urls = [
        'https://www.spermcocktail.com',
    ]

    selector_map = {
        'title': '//div[@id="boxVidTitle"]/text()',
        'description': '//p[@id="boxVidDescription"]/text()',
        'date': '//div[@id="boxVidDetail"]/b[contains(text(), "UPDATED")]/following-sibling::text()',
        'date_formats': ['%b %d, %Y'],
        'image': '',
        'performers': '//div[@id="boxVidDetail"]/a[contains(@onclick, "Actor")]/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/home.php?page=%s'
    }


    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="boxVideo"]/table/tr[1]/td[1]/img/@src').getall()
        for scene in scenes:
            sceneid = re.search(r'images/(V\d+)/', scene).group(1)
            image = scene
            image_blob = self.get_image_blob_from_link(image)
            scene = f"https://www.spermcocktail.com/psnUpdatesFocus.php?vnum={sceneid}"
            if sceneid:
                meta['id'] = sceneid
                meta['image'] = image
                meta['image_blob'] = image_blob
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        return ['Facial', 'Cumshot', 'Cum Swallowing', 'Blowjob']
