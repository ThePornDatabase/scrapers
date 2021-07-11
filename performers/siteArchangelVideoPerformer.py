import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class ArchangelVideoPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile-details"]/h3[@class="larger"]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x|//div[@class="profile-pic"]/img/@src0',
        'measurements': '//strong[contains(text(),"Measurements")]/following-sibling::text()',
        'height': '//strong[contains(text(),"Height")]/following-sibling::text()',
        'birthday': '//strong[contains(text(),"Age")]/following-sibling::text()',
        'bio': '//div[@class="profile-about"]/p/text()',
        'pagination': '/tour/models/%s/popular/?gender=female',
        'external_id': 'models\/(.*).html'
    }

    name = 'ArchangelVideoPerformer'
    network = "Arch Angel"
    parent = "Arch Angel"

    start_urls = [
        'https://www.archangelvideo.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/div/a/@href').getall()
        for performer in performers:
            if "archangelvideo" not in performer:
                performer = "https://www.archangelvideo.com/tour/" + performer
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'site':'Arch Angel'}
            )

    def get_gender(self, response):
        return "Female"

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search('(.*-\d{2}-\d{2})', measurements):
                measurements = measurements.replace(" ","").strip()
                measurements = re.search('(.*-\d{2}-\d{2})', measurements).group(1)
                if measurements:
                    cupsize = re.search('(.*?)-.*', measurements).group(1)
                    if cupsize:
                        return cupsize.upper().strip()
        return ''   

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search('\d{2}(?:[a-zA-Z]+)?-\d{2}-\d{2}', measurements):
                return measurements.strip()
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                if " " in image:
                    image = re.search('(.*) ', image).group(1)
                if image:
                    image = image.replace('//','/')
                    image = 'https://www.archangelvideo.com/' + image
                    return image.strip()
        return ''
        
    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).get()
            if height:
                if "cms" in height.lower():
                    height = re.search('(\d+)\s+?cms',height.lower()).group(1)
                    if height:
                        height = height+"cm"
                        return height.strip()
        return ''

    def get_birthday(self, response):
        date = self.process_xpath(response, self.get_selector_map('birthday')).get()
        if date:
            return dateparser.parse(date.strip()).isoformat()
        else:
            return ''
