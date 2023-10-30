import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="col-md-10"]/h2/text()',
        'image': '//div[@class="profileImage"]/img/@src',
        'image_blob': True,
        'bio': '//div[@class="profileBio"]/text()',
        'gender': '',
        'astrology': '',
        'birthday': '',
        'birthplace': '',
        'cupsize': '',
        'ethnicity': '',
        'eyecolor': '',
        'fakeboobs': '',
        'haircolor': '',
        'height': '',
        'measurements': '',
        'nationality': '',
        'piercings': '',
        'tattoos': '',
        'weight': '',

        'pagination': '/models/?p=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'WaxinPhatAssesPerformer'
    network = 'SLP Adult Media'

    start_urls = [
        'http://40ddd.com',
        'http://doggystylebjs.com',
        'http://farrahfeet.com',
        'http://gearsofwhores.com',
        'http://jervonilee.com',
        'http://phuckfumasters.com',
        'http://sex-xxxtv.com',
        'http://waxinphatasses.com',
        'http://womenwithnuttinbuttass.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "video-box")]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)
