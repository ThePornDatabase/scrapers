import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'funsizeboys': 'Fun-Size Boys',
        'gaycest': 'Gaycest',
        'scoutboys': 'Scoutboys',
        'staghomme': 'Staghomme',
        'masonicboys': 'MasonicBoys',
        'boyforsale': 'Boys For Sale',
        'twinktop': 'Twink Top',
        'catholicboys': 'Catholic Boys',
        'americanmusclehunks': 'American Muscle Hunks',
        'bangbangboys': 'Bang Bang Boys',
        'jalifstudio': 'Jalif Studio',
        'edwardjames': 'Edward James',
        'growlboys': 'Growlboys',
        'twinks': 'Twinks',
        'teensandtwinks': 'Teens and Twinks',
    }
    return match.get(argument.lower(), argument)

class NetworkCarnalPlusSpider(BaseSceneScraper):
    name = 'CarnalPlus'
    network = 'CarnalPlus'

    start_urls = [
        'https://www.carnalplus.com'
    ]

    selector_map = {
        'description': '//div[@class="textDescription"]/p/text()',
        'date': '//div[@class="releasedate"]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//script[contains(text(), "player.poster")]/text()',
        're_image': r'player.poster.*?(http.*?)[\'\"]',
        'performers': '//div[contains(@class, "update-models")]/div/a/text()',
        'tags': '//div[@class="update_tags"]/a/span/text()',
        'duration': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/videos?page=%s',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="grid-vid-item"]')
        for scene in scenes:
            site = scene.xpath('.//div[@class="update-sitename"]/text()').get()
            site = match_site(site)
            meta['site'] = site
            meta['parent'] = site
            scene = scene.xpath('./div[1]/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = response.xpath('//h2[@class="video-detail-h2"]//text()').getall()
        title = " - ".join(title)
        return string.capwords(title)

    def get_image(self, response):
        image = super().get_image(response)
        image = re.sub(r'-\dx\.', '-full.', image)
        return image
