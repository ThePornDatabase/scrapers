import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class BAMVisionsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile-details"]/h3[@class="larger"]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'height': '//div[@class="stats"]/ul/li/strong[contains(text(),"Height")]/following-sibling::text()',
        'measurements': '//div[@class="stats"]/ul/li/strong[contains(text(),"Measurements")]/following-sibling::text()',
        'pagination': '/models/%s/popular/?gender=female',
        'external_id': 'models\/(.*).html'
    }

    name = 'BAMVisionsPerformer'
    network = 'BAM Visions'
    parent = 'BAM Visions'
    site = 'BAM Visions'

    start_urls = [
        'https://tour.bamvisions.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )


    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('(.*-.*-.*)', measurements):
                return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.match('(.*-.*-.*)', measurements):
                cupsize = re.search('(?:\s+)?(.*)-.*-',measurements).group(1)
                if cupsize:
                    return cupsize.strip()
        return ''


    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = "https://tour.bamvisions.com/" + image
            return self.format_link(response, image)
        return ''


    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "'" in height:
                    feet = int(re.search('(\d+)\'(\d+)',height.replace(" ","")).group(1))
                    inches = int(re.search('(\d+)\'(\d+)',height.replace(" ","")).group(2))
                    heightcm = str(round(((feet*12)+inches) * 2.54)) + "cm"
                    return heightcm
                    
                return height.strip()
        return ''
