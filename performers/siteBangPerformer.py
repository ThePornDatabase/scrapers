import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteBangPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class, "items-start")]/h2/text()',
        'image': '',
        'image_blob': True,
        'bio': '',
        'gender': '',
        'astrology': '',
        'birthday': '//div[contains(text(), "Born")]/span[1]/text()',
        're_birthday': r'(\w+ \d{1,2}, \d{4})',
        'birthplace': '//div[contains(./following-sibling::text(), "From")]/following-sibling::span[contains(@class, "bold")]/text()',
        'cupsize': '',
        'ethnicity': '//div[contains(text(), "Ethnicity")]/span[1]/text()',
        'eyecolor': '//text()[contains(., "Eye Color:")]/following-sibling::span[1]/text()',
        'fakeboobs': '',
        'haircolor': '//text()[contains(., "Hair Color:")]/following-sibling::span[1]/text()',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/pornstars?by=views.weekly&page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'BangPerformer'
    network = 'Bang'

    start_urls = [
        'https://www.bang.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "rounded-xl")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_image(self, response):
        image = response.xpath('//section[contains(@class, "relative")]/div[contains(@class, "relative")]//picture/source/@srcset')
        if image:
            image = image.get()
            if "," in image:
                image = image.split(",")
            else:
                image = [image]
            for image_test in image:
                if "200" in image_test:
                    return re.search(r'(http.*?) ', image_test).group(1)
            for image_test in image:
                if "144" in image_test:
                    return re.search(r'(http.*?) ', image_test).group(1)
        return ""
