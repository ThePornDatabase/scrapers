import html
import re
import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteFightingDollsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="update_details"]/a[1]/text()',
        'image': "//img/@src",
        'pagination': '/models/models_%s_d.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'FightingDollsPerformer'
    network = "Fighting Dolls"

    start_urls = [
        'https://www.fighting-dolls.com/all-our-girls/',
        'https://www.trib-dolls.com/all-our-girls/',
    ]

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(link,
                                 callback=self.get_performers,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="cell text-center"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//h4/a/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('.//img/@src').get()
            if image:
                if "fighting-dolls" in response.url:
                    item['image'] = "https://www.fighting-dolls.com" + image.strip()
                if "trib-dolls" in response.url:
                    item['image'] = "https://www.trib-dolls.com" + image.strip()
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./div[@class="photo"]/a/@href').get()
            if url:
                if "fighting-dolls" in response.url:
                    item['url'] = "https://www.fighting-dolls.com" + url.strip()
                if "trib-dolls" in response.url:
                    item['url'] = "https://www.trib-dolls.com" + url.strip()

            item['network'] = 'Fighting Dolls'

            height = performer.xpath('.//li[contains(text(),"Height")]/text()')
            if height:
                height = height.get()
                height = re.search(r'(\d+ cm)', height)
                if height:
                    height = height.group(1)
                    item['height'] = height.replace(" ", "")
                else:
                    item['height'] = ''

            weight = performer.xpath('.//li[contains(text(),"Weight")]/text()')
            if weight:
                weight = weight.get()
                weight = re.search(r'(\d+ kg)', weight)
                if weight:
                    weight = weight.group(1)
                    item['weight'] = weight.replace(" ", "")
                else:
                    item['weight'] = ''

            item['astrology'] = ''
            item['bio'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['gender'] = 'Female'
            item['haircolor'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''

            yield item
