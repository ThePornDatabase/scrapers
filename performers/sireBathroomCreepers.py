import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteBathroomCreepersPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[contains(@class,"profile-details")]/h3[1]/text()',
        'image': '//div[@class="profile-pic"]/img/@src0_1x',
        'bio': '//strong[contains(text(), "Fun Fact")]/following-sibling::text()',
        'height': '//strong[contains(text(), "Height")]/following-sibling::text()',
        'pagination': '/creeper/models/%s/latest/?g=f',
        'external_id': r'model/(.*)/'
    }

    name = 'BathroomCreepersPerformer'
    network = 'Bathroom Creepers'

    start_urls = [
        'https://www.bathroomcreepers.com',
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

    def get_bio(self, response):
        bio = super().get_bio(response)
        bio = re.sub(r"(\A\w)|(?<!\.\w)([\.?!] )\w|\w(?:\.\w)|(?<=\w\.)\w", lambda x: x.group().upper(), bio.lower())
        return bio
