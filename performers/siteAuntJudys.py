import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper

class siteAuntJudysPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="title_bar"]/span/text()',
        'image': '//div[@class="cell_top cell_thumb"]/img/@src0_2x',
        'height': '//comment()[contains(.,"Bio Extra Fields")]/following-sibling::text()[contains(.,"Height")]',
        'cupsize': '//comment()[contains(.,"Bio Extra Fields")]/following-sibling::text()[contains(.,"Bust")]',
        'measurements': '//comment()[contains(.,"Bio Extra Fields")]/following-sibling::text()[contains(.,"Measurements")]',
        'pagination': '/tour/models/models_%s.html',
        'external_id': 'models\/(.*)\/'
    }

    name = 'AuntJudysPerformer'
    network = "Aunt Judys"

    start_urls = [
        'https://www.auntjudys.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).getall()
            if height:
                height = " ".join(height)
                if "Height:" in height:
                    height = height.replace("&nbsp;", "").replace("\n", "").replace("\t", " ").replace("\r", " ").strip()
                    height = re.sub("\s\s+", " ", height).strip()
                    height = re.search('Height:\s+(\d+.*)', height).group(1)
                    if height:
                        height = height.replace(" ","")
                        return height.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).getall()
            if measurements:
                measurements = " ".join(measurements)
                if "Measurements:" in measurements and re.search('(\d+\w+-\d+\d+)', measurements):
                    measurements = measurements.replace("&nbsp;", "").replace("\n", "").replace("\t", " ").replace("\r", " ").strip()
                    measurements = re.sub("\s\s+", " ", measurements).strip()
                    measurements = re.search('Measurements:\s+(\d+.*)', measurements).group(1)
                    if measurements:
                        measurements = re.sub('[^a-zA-Z0-9-]', '', measurements)
                        return measurements.strip()
        return ''

    def get_cupsize(self, response):
        if 'cupsize' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('cupsize')).getall()
            if cupsize:
                cupsize = " ".join(cupsize)
                if "Bust:" in cupsize:
                    cupsize = cupsize.replace("&nbsp;", "").replace("\n", "").replace("\t", " ").replace("\r", " ").strip()
                    cupsize = re.sub("\s\s+", " ", cupsize).strip()
                    cupsize = re.search('Bust:\s+(\d+.*)', cupsize).group(1)
                    if cupsize:
                        cupsize = cupsize.replace(" ","")
                        return cupsize.strip()
        return ''
        
    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if not image:
                image = response.xpath('//div[@class="cell_top cell_thumb"]/img/@src0_2x').get()
            if not image:
                image = response.xpath('//div[@class="cell_top cell_thumb"]/img/@src').get()
            if image:
                image = "https://www.auntjudys.com" + image
                return image.strip()
        return ''        
