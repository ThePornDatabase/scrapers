import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteAdultAuditionsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"profile-details")]/h3[1]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'bio': '//div[@class="profile-about"]/p/text()',
        'height': '//strong[contains(text(), "Height")]/following-sibling::text()',
        'measurements': '//strong[contains(text(), "Measurements")]/following-sibling::text()',
        'pagination': '/tour/models/%s/latest/?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'BlackBullChallengePerformer'
    network = 'Black Bull Challenge'

    start_urls = [
        'https://www.blackbullchallenge.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-portrait"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_name(self, response):
        name = super().get_name(response)
        name = name.replace("About", "").strip()
        return name

    def get_height(self, response):
        height = super().get_height(response)
        if height:
            heighttext = re.search(r'\((\d{3}.*?)\)', height)
            if heighttext:
                return heighttext.group(1).replace(" ", "").lower().strip()
        return height

    def get_cupsize(self, response):
        if 'measurements' in self.selector_map:
            cupsize = self.process_xpath(response, self.get_selector_map('measurements'))
            if cupsize:
                cupsize = cupsize.get()
                if re.search(r'(\d+\w+)-\d+-\d+', cupsize):
                    cupsize = re.search(r'(\d+\w+)-\d+-\d+', cupsize).group(1)
                    if cupsize:
                        return cupsize.strip().upper()
        return ''

    def get_bio(self, response):
        bio_xpath = self.process_xpath(response, self.get_selector_map('bio'))
        if bio_xpath:
            if len(bio_xpath) > 1:
                bio = list(map(lambda x: x.strip(), bio_xpath.getall()))
                bio = ' '.join(bio)
            else:
                bio = bio_xpath.get()
            return bio

        return ''
