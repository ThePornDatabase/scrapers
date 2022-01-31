import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteAdultAuditionsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="model-detail__bio"]/h1/text()',
        'image': '//div[contains(@class, "model-detail__image")]/img/@data-src',
        'image_blob': True,
        'bio': '//p[contains(@class, "model-description")]/text()',
        'gender': '//div[contains(@class, "model-detail__bio")]/table//th[contains(text(), "Sex")]/following-sibling::td/text()',
        'height': '//div[contains(@class, "model-detail__bio")]/table//th[contains(text(), "Height")]/following-sibling::td/text()',
        'weight': '//div[contains(@class, "model-detail__bio")]/table//th[contains(text(), "Weight")]/following-sibling::td/text()',
        'cupsize': '//div[contains(@class, "model-detail__bio")]/table//th[contains(text(), "Bust")]/following-sibling::td/text()',
        'pagination': '/member/actor/list/index.html?page=%s&is_paginate=1',
        'external_id': r'model/(.*)/'
    }

    name = 'TripForFuckPerformer'
    network = 'Trip For Fuck'

    start_urls = [
        'https://www.tripforfuck.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="movie-list__item"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_gender(self, response):
        gender = response.xpath(self.get_selector_map('gender'))
        if gender:
            gender = "".join(gender.getall())
            gender = gender.replace("\n", "").replace("\r", "").replace(" ", "").strip()
        if not gender:
            gender = "Female"
        return gender.strip().title()

    def get_bio(self, response):
        bio = response.xpath(self.get_selector_map('bio'))
        if bio:
            bio = " ".join(bio.getall())
            bio = bio.replace("\n", "").replace("\r", "").replace("\t", "").strip()
            return bio
        return ''

    def get_height(self, response):
        height = response.xpath(self.get_selector_map('height'))
        if height:
            height = "".join(height.getall())
            height = height.replace("\n", "").replace("\r", "").replace(" ", "").strip()
            return height
        return ''

    def get_weight(self, response):
        weight = response.xpath(self.get_selector_map('weight'))
        if weight:
            weight = "".join(weight.getall())
            weight = weight.replace("\n", "").replace("\r", "").replace(" ", "").strip()
            return weight
        return ''
