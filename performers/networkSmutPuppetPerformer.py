import dateparser
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkSmutPuppetPerformerSpider(BasePerformerScraper):
    name = 'SmutPuppetPerformer'
    network = 'Smut Puppet'

    start_urls = ['https://smutpuppet.com']

    selector_map = {
        'name': '//div[@class="modelInfo"]/h2/text()',
        'image': '//figure[@class="modelPreview"]/img/@src',
        'nationality': '//div[@class="modelNationality"]/strong/text()',
        'birthday': '//div[@class="modelDOB"]/strong/text()',
        'pagination': '/models/?page_num=%s',
        'external_id': r'girls/(.+)/?$'
    }

    def get_performers(self, response):
        performers = response.xpath('//div[@class="blockItem"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"

    def get_birthday(self, response):
        birthday = super().get_birthday(response)
        if birthday:
            birthday = dateparser.parse(birthday).isoformat()
            return birthday
        return ''
