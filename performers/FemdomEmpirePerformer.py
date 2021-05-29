import scrapy
import re

from tpdb.BasePerformerScraper import BasePerformerScraper


class FemdomEmpirePerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="profile-details"]/h3/text()',
        'image': '//img[contains(@class,"model_bio_thumb") and contains(@id,"set-target")][1]/@src0_1x',
        'bio': '//div[@class="profile-about"]/p/text()',
        'pagination': '/tour/models/%s/name/?g=',
        'external_id': 'models\/(.+).html$'
    }

    name = 'FemdomEmpirePerformer'
    network = "Femdom Empire"
    parent = "Femdom Empire"

    start_urls = [
        # ~ 'https://femdomempire.com',
        'http://feminized.com',
    ]

    def get_gender(self, response):
        return 'Female'
        
    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-info clear"]/h4/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )


    def get_image(self, response):
        if "femdom" in response.url:
            prefix = "https://femdomempire.com"
        if "feminized" in response.url:
            prefix = "https://feminized.com"
        
        if 'image' in self.selector_map:
            image = self.process_xpath(response, self.get_selector_map('image')).get()
            if image:
                return prefix + image.strip()
        return ''

    def get_bio(self, response):
        if 'bio' in self.selector_map:
            bio = self.process_xpath(response, self.get_selector_map('bio')).get()
            if bio:
                return bio.strip()
        return ''
