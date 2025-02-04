import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper

# Note: Age is listed on the website, but is as of being put on the site.
# Compared to bio text in a few they were off by several years

class ExposedWhoresPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="updatesBlock"]/div[@class="title clear"]/h2/text()',
        'image': '//img[contains(@class,"model_bio")]/@src0_1x',
        'bio': '//comment()[contains(.,"Bio Extra Field") and not(contains(.,"Accompanying"))]/following-sibling::text()',
        'height': '//span[@class="model_bio_heading"]/following-sibling::text()',
        'pagination': '/new-tour/models/models_%s.html',
        'external_id': r'models/(.*)/'
    }

    name = 'ExposedWhoresPerformer'
    network = "Exposed Whores Media"
    parent = "Exposed Whores"

    start_urls = [
        'https://exposedwhores.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class,"updateItem")]/div/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer, meta={'site':'Exposed Whores'}
            )


    def get_name(self, response):
        name = self.process_xpath(response, self.get_selector_map('name')).get().replace("/","").strip()
        return name

    def get_height(self, response):
        if 'height' in self.selector_map:
            height = self.process_xpath(response, self.get_selector_map('height')).getall()
            if height:
                height = " ".join(height)
                if "Height:" in height:
                    height = height.replace("\r\n", " ").strip()
                    height = height.replace("\n", " ").strip()
                    height = height.replace("\t", " ").strip()
                    height = re.sub("\s\s+", " ", height).strip()
                    height = re.search('Height:\s+(\d+.*\")', height).group(1)
                    height = height.replace("\\", "").strip()
                    if height:
                        height = height.replace(" ","")
                        return height.strip()
        return ''

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                image = "https://exposedwhores.com" + image
                return image.strip()
        return ''
