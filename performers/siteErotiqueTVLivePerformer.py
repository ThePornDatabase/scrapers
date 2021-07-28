import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from urllib.parse import urlparse

from tpdb.BasePerformerScraper import BasePerformerScraper


class siteErotiqueTVLivePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"container-default")]//h2/text()',
        'image': '//img[contains(@class,"model_bio_thumb")]/@src0',
        'birthplace': '//strong[contains(text(),"Birthplace")]/following-sibling::text()',
        'eyecolor': '//strong[contains(text(),"Eye")]/following-sibling::text()',
        'haircolor': '//strong[contains(text(),"Hair")]/following-sibling::text()',
        'height': '//strong[contains(text(),"Height")]/following-sibling::text()',
        'measurements': '//strong[contains(text(),"Measurements")]/following-sibling::text()',
        'tattoos': '//strong[contains(text(),"Tattoos")]/following-sibling::text()',
        'birthday': '//strong[contains(text(),"Date")]/following-sibling::text()',
        'bio': '//div[@class="detail-div"]/p[1]/text()[1]',
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': 'models/(.+).html$'
    }

    name = 'ErotiqueTVLivePerformer'
    network = 'ErotiqueTVLive'

    start_urls = [
        'https://erotiquetvlive.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"item-model")]/div/a/@href').getall()
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

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search('(\d+\w+-\d+-\d+)', measurements):
                    measurements = re.search('(\d+\w+-\d+-\d+)', measurements).group(1)
                    measurements = re.sub('[^a-zA-Z0-9-]', '', measurements)
                    return measurements.strip().upper()
        return ''

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if cupsize:
                cupsize = re.search('(\d+\w+)-\d+-\d+', cupsize)
                if cupsize:
                    cupsize = cupsize.group(1).upper()
                    return cupsize.strip().upper()
        return ''
 

    def get_birthday(self, response):
        if 'birthday' in self.selector_map:
            birthday = self.process_xpath(response, self.get_selector_map('birthday')).get()
            if birthday:
                try:
                    birthday = dateparser.parse(birthday).isoformat()
                    return birthday
                except:
                    return ''
        return ''
        

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return "https://erotiquetvlive.com/" + image.strip()
        return ''

