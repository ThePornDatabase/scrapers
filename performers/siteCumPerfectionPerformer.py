import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class CumPerfectionPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//span[contains(@class,"title_bar")]/text()',
        'image': '//img[contains(@class,"model_bio")]/@data-src0_1x',
        'haircolor': '//strong[contains(text(),"hair") or contains(text(),"Hair")]/following-sibling::text()',
        'ethnicity': '//strong[contains(text(),"ethnicity") or contains(text(),"Ethnicity")]/following-sibling::text()',
        'bio': '//comment()[contains(.,"Bio Extra") and not(contains(.,"Fields"))]/following-sibling::text()',
        'pagination': '/models/%s/latest/',
        'external_id': 'models\/(.*).html'
    }

    name = 'CumPerfectionPerformer'
    network = "Cum Perfection"
    parent = "Cum Perfection"

    start_urls = [
        'https://www.cumperfection.com/'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                if " " in image:
                    image = re.search('(.*) ', image).group(1)
                if image:
                    image = image.replace('//','/')
                    image = 'https://www.cumperfection.com/' + image
                    return image.strip()
        return ''

        
    def get_haircolor(self, response):
        if 'haircolor' in self.selector_map:
            haircolor = self.process_xpath(response, self.get_selector_map('haircolor')).get()
            if haircolor:
                haircolor = haircolor.replace("&nbsp;","").replace(":","")
                return haircolor.strip()
        return ''
        
    def get_ethnicity(self, response):
        if 'ethnicity' in self.selector_map:
            ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity')).get()
            if ethnicity:
                ethnicity = ethnicity.replace("&nbsp;","").replace(":","")
                return ethnicity.strip()
        return ''

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).getall()
            if bio:
                bio = " ".join(bio)
                return bio.strip()
        return ''
