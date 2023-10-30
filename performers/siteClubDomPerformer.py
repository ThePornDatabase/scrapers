import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteClubDomPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="title_bar"]/span/text()',
        'image': '//div[@class="table"]//img[contains(@class, "model_bio_thumb")]/@src0|//div[@class="table"]//img[contains(@class, "model_bio_thumb")]/@src0_3x|//div[@class="table"]//img[contains(@class, "model_bio_thumb")]/@src0_2x|//div[@class="table"]//img[contains(@class, "model_bio_thumb")]/@src',
        'image_blob': True,

        'pagination': '/vod/models/models_%s_d.html',
        'external_id': r'model/(.*)/'
    }

    name = 'ClubDomPerformer'
    network = 'Club Dom'

    start_urls = [
        'https://www.clubdom.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, cookies=self.cookies, headers=self.headers)

    def get_image(self, response):
        image = super().get_image(response)
        if "/content/" not in image:
            image = ""
        return image
