import scrapy
import re

from tpdb.BasePerformerScraper import BasePerformerScraper


class sitePAWGEDPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//meta[@name="description"]/@content',
        'image': '//div[contains(@class,"model_picture")]/img/@src0_1x',
        'measurements': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Measurements")]',
        'height': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Height")]',
        'astrology': '//span[@class="model_bio_heading"]/following-sibling::text()[contains(.,"Astrological")]',
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'PAWGEDPerformer'
    network = "PAWGED"

    start_urls = [
        'https://PAWGED.com/',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelPic"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).get().strip().replace("-","")
            return cupsize
        return ''


    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return "https://pawged.com/" + image.strip()
        return ''

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                height = height.replace("\n","").replace("\r","")
                height = re.search('Height:(.*)', height).group(1)
                return height.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements:
                measurements = measurements.replace("\n","").replace("\r","")
                measurements = re.search('Measurements:(.*)', measurements).group(1)
                return measurements.strip()
        return ''

    def get_astrology(self, response):
        if 'astrology' in self.selector_map:
            astrology = self.process_xpath(response, self.get_selector_map('astrology')).get()
            if astrology:
                astrology = astrology.replace("\n","").replace("\r","")
                astrology = re.search('Sign:(.*)', astrology).group(1)
                return astrology.strip()
        return ''
