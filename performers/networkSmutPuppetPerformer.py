import re
import dateparser
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper


class NetworkSmutPuppetPerformerSpider(BasePerformerScraper):
    name = 'SmutPuppetPerformer'
    network = 'Smut Puppet'

    start_urls = ['https://smutpuppet.com']

    selector_map = {
        'name': '//div[@class="model-content"]/h1/text()',
        'image': '//div[@class="model-img"]/a/img/@src',
        'nationality': '//div[@class="model-content"]/p/span[@class="que" and contains(text(), "NATIONALITY")]/following-sibling::span[@class="ans"][1]/text()',
        'birthday': '//div[@class="model-content"]/p/span[@class="que" and contains(text(), "BIRTH")]/following-sibling::span[@class="ans"][1]/text()',
        'pagination': '/models/?page_num=%s',
        'external_id': r'girls/(.+)/?$'
    }

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item-wrapper"]/a[contains(@href, "/models/")]/@href').getall()
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

    def get_url(self, response):
        sceneurl = super().get_url(response)
        if "?&nats" in sceneurl:
            sceneurl = re.search(r'(.*)\?&nats', sceneurl).group(1)
        return sceneurl
