import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class siteWaitressPOVSpider(BaseSceneScraper):
    name = 'WaitressPOV'
    network = 'Waitress POV'
    parent = 'Waitress POV'

    start_urls = [
        'http://www.waitresspov.com',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//div[@class="scene-desc"]/text()',
        'date': '//div[@class="date-views"]/span[1]/text()',
        'image': '//video/@poster',
        'performers': '//div[contains(@class,"details-list starring")]/div[contains(text(),"Starring")]/following-sibling::div/text()',
        'tags': '//div[contains(@class,"details-list categories")]/div[contains(text(),"Categories")]/following-sibling::div/text()',
        'external_id': '.*\/(.*?)\/.*?$',
        'trailer': '',
        'pagination': '/t2/show.php?a=2213_%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="date-img-wrapper"]/a/@href').getall()
        for scene in scenes:
            scene = "/t2/" + scene
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        return "Waitress POV"

    def get_parent(self, response):
        return "Waitress POV"
        

    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.get_from_regex(image.get(), 're_image')

            if image:
                image = "/t2/" + image
                image = self.format_link(response, image)
                return image.replace(" ", "%20")

        return None
