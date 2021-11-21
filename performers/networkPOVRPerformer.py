import json
import scrapy
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class POVRPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h1[contains(@class,"title")]/text()',
        'image': '//div[contains(@class,"profile") and contains(@class,"logo")]/img/@src',
        'bio': '//div[contains(@class,"profile") and contains(@class,"text")]/p/text()',
        'birthplace': '//div[contains(@class,"profile") and contains(@class,"text")]/div/ul/li/div[contains(text(),"Birth place")]/following-sibling::div/text()',
        'birthday': '//div[contains(@class,"profile") and contains(@class,"text")]/div/ul/li/div[contains(text(),"Birthday")]/following-sibling::div/text()',
        'height': '//div[contains(@class,"profile") and contains(@class,"text")]/div/ul/li/div[contains(text(),"Height")]/following-sibling::div/text()',
        'pagination': '/pornstars?o=d&p=%s',
        'external_id': r'.+/(.*)$'
    }

    name = 'POVRPerformer'
    network = "POVR"
    parent = "POVR"

    start_urls = [
        'https://povr.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="thumbnail"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def parse_performer(self, response):
        item = PerformerItem()
        jsondata = response.xpath('//script[@type="application/ld+json"]/text()').get()
        jsondata = jsondata.replace("\r\n", "")
        data = json.loads(jsondata.strip())
        item['name'] = data['name']
        item['network'] = 'POVR'
        item['url'] = data['mainEntityOfPage']
        item['image'] = data['image']
        item['image_blob'] = None
        bio = response.xpath('//div[contains(@class, "player__description")]/p/text()')
        if bio:
            item['bio'] = bio.get().strip()
        else:
            item['bio'] = None

        if 'gender' in data:
            item['gender'] = data['gender'].title()
        else:
            item['gender'] = None

        item['birthday'] = None
        if 'birthDate' in data:
            if data['birthDate'] and data['birthDate'] > '1950-01-01':
                item['birthday'] = dateparser.parse(data['birthDate'], date_formats=['%Y-%m-%d'], settings={'TIMEZONE': 'UTC'}).isoformat()

        item['astrology'] = None
        item['ethnicity'] = None
        if 'birthPlace' in data:
            item['birthplace'] = data['birthPlace']
        else:
            item['birthplace'] = None

        if 'height' in data:
            item['height'] = data['height']
        else:
            item['height'] = None

        item['nationality'] = None
        item['haircolor'] = None
        item['eyecolor'] = None
        item['weight'] = None
        item['measurements'] = None
        item['cupsize'] = None
        item['tattoos'] = None
        item['piercings'] = None
        item['fakeboobs'] = None

        yield item
