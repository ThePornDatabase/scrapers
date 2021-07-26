import scrapy
import re
from urllib.parse import urlparse
from tpdb.BasePerformerScraper import BasePerformerScraper

class networkPureCFNMPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="title_bar"]/span/text()',
        'image': '//img[contains(@class,"model_bio_thumb")]/@data-src0_3x',
        'bio': '//comment()[contains(.,"Bio Extra Field") and not(contains(.,"Fields"))]/following-sibling::text()',
        'haircolor': '//strong[contains(text(),"Hair")]/following-sibling::text()[1]',
        'ethnicity': '//strong[contains(text(),"Ethnicity")]/following-sibling::text()[1]',
        'pagination': '/models/%s/latest/',
        'external_id': 'models\/(.*)\/'
    }

    name = 'PureCFNMPerformer'
    network = "Pure CFNM"

    start_urls = [
        'https://www.purecfnm.com',
        'https://www.ladyvoyeurs.com',
        'https://www.amateurcfnm.com',
        'https://www.cfnmgames.com',
        'https://www.girlsabuseguys.com',
        'https://littledick.club',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )
        
    def get_image(self, response):
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if not image:
                image = response.xpath('//img[contains(@class,"model_bio_thumb")]/@data-src0_2x').get()
            if not image:
                image = response.xpath('//img[contains(@class,"model_bio_thumb")]/@data-src0_1x').get()
            if not image:
                image = response.xpath('//img[contains(@class,"model_bio_thumb")]/@src').get()
                
            if image:
                uri = urlparse(response.url)
                base = uri.scheme + "://" + uri.netloc
                image = base + image.strip()
                return image

        return ''        


    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).getall()
            if bio:
                bio = " ".join(bio)
                return bio.strip()
        return ''

        
    def get_haircolor(self, response):
        if 'haircolor' in self.selector_map:
            haircolor = self.process_xpath(response, self.get_selector_map('haircolor')).get()
            if haircolor:
                haircolor = haircolor.replace("&nbsp;","").replace(":","").strip()
                return haircolor
        return ''
        
    def get_ethnicity(self, response):
        if 'ethnicity' in self.selector_map:
            ethnicity = self.process_xpath(response, self.get_selector_map('ethnicity')).get()
            if ethnicity:
                ethnicity = ethnicity.replace("&nbsp;","").replace(":","").strip()
                return ethnicity
        return ''
