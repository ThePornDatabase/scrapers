import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class PenthousePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"bio-pornstar")]/h1/text()',
        'image': '//div[contains(@class,"img-pornstar")]/a/picture/source[1]/@srcset',
        'bio': '//ul[@class="model-facts"]/li[@class="model-facts-long"]//text()',
        'measurements': '//ul[@class="model-facts"]/li/em[contains(text(), "Measurements")]/following-sibling::text()',
        'height': '//ul[@class="model-facts"]/li/em[contains(text(), "Height")]/following-sibling::text()',
        'pagination': '/models/models_%s_p.html',
        'external_id': 'models\/(.*).html'
    }

    name = 'PenthousePerformer'
    network = "Penthouse"
    parent = "Penthouse"

    start_urls = [
        'https://penthousegold.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//a[@data-track="PORNSTAR_IMAGE"]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'site':'Penthouse Gold'}
            )


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

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).getall()
            for bio_entry in bio:
                bio_entry = bio_entry.strip()
            bio = "\n".join(bio)
            if bio:
                return bio.strip()
        return ''

    def get_measurements(self, response):
        if 'measurements' in self.selector_map:
            measurements = self.process_xpath(response, self.get_selector_map('measurements')).get()
            if measurements and re.search('\d{2}[a-zA-Z]?-\d{2}-\d{2}', measurements):
                return measurements.strip()
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if " " in image:
                image = re.search('(.*) ', image).group(1)
            if image:
                return image.strip()
        return ''
