import scrapy
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta
import dateparser
from tpdb.BasePerformerScraper import BasePerformerScraper


class siteSapphixPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h3[@class="mg-md"]/text()',
        'image': '//div[contains(@class,"bigmodelpic")]/img/@src',
        'haircolor': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Hair")]/following-sibling::text()[1]',
        'ethnicity': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Race")]/following-sibling::text()[1]',
        'nationality': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Country")]/following-sibling::text()[1]',
        'height': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Height")]/following-sibling::text()[1]',
        'weight': '//div[contains(@class,"modeldetail")]/strong[contains(text(),"Weight")]/following-sibling::text()[1]',
        'pagination': '/models/page-%s/?tag=&sort=recent&pussy=all&',
        'external_id': 'models\/(.*).html'
    }

    name = 'SapphixPerformer'
    network = "Sapphix"
    parent = "Sapphix"

    start_urls = [
        'https://www.sapphix.com'
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="modelitem"]/a/@href').getall()
        for performer in performers:
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer)

    def get_gender(self, response):
        return "Female"
        

    def get_url(self, response):
        url = re.search('(.*)\?nats', response.url)
        if url:
            url = url.group(1)
            return url.strip()
        return response.url        
