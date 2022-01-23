import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteNewGirlPOVSpider(BaseSceneScraper):
    name = 'NewGirlPOV'
    network = 'New Girl POV'
    parent = 'New Girl POV'
    site = 'New Girl POV'

    start_urls = [
        'http://newgirlpov.com',
    ]

    selector_map = {
        'title': '//div[contains(@style, "font-size:24px")]/div[contains(@style, "float:left;")]//text()',
        'description': '//div[@id="profile_data"]/div/following-sibling::div/text()',
        'date': '//td[@class="date"]',
        're_date': r'(\d{2}/\d{2}/\d{4})',
        'date_formats': ['%m/%d/%Y'],
        'image': '//script[contains(text(), "player_1")]/text()',
        're_image': r'image: \"(.*?)\"',
        'performers': '//a[@class="model_category_link" and contains(@href, "sets")]/text()',
        'tags': '//a[@class="model_category_link" and contains(@href, "category")]/text()',
        'external_id': r'id=(\d+)',
        'trailer': '//script[contains(text(), "player_1")]/text()',
        're_trailer': r'file: \"(.*?)\"',
        'pagination': '/tour/index.php?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb320"]/div/a/@href').getall()
        for scene in scenes:
            scene = "/tour/" + re.search(r'(.*)\&nats', scene).group(1)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_title(self, response):
        title = response.xpath(self.get_selector_map('title'))
        if title:
            title = " ".join(title.getall())
            if title:
                title = self.cleanup_title(title)
                return string.capwords(title)
        return None

    def get_description(self, response):
        description = response.xpath(self.get_selector_map('description'))
        if description:
            description = '\n'.join(description.getall())
            return description
        return None

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map():
            if self.get_selector_map('trailer'):
                trailer = self.process_xpath(response, self.get_selector_map('trailer'))
                if trailer:
                    trailer = self.get_from_regex(trailer.get(), 're_trailer')
                    if trailer:
                        trailer = self.format_link(response, trailer)
                        return trailer.strip().replace(' ', '%20')
                else:
                    trailer = response.xpath('//video/source/@src')
                    if trailer:
                        trailer = trailer.get()
                        return self.format_link(response, trailer)
        return ''

    def get_image(self, response):
        if 'image' not in self.get_selector_map():
            return ''

        if self.get_selector_map('image'):
            image = self.process_xpath(response, self.get_selector_map('image'))
            if image:
                image = self.get_from_regex(image.get(), 're_image')
                if image:
                    image = self.format_link(response, image)
                    return image.strip().replace(' ', '%20')
            else:
                image = response.xpath('//div[@id="overallthumb"]/a/img/@src')
                if image:
                    image = image.get()
                    image = re.search(r'(.*)\&w', image).group(1)
                    image = '/tour/' + image + '&w=468&h=752'
                    return self.format_link(response, image)
        return None
