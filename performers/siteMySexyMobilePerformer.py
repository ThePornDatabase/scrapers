import re
import html
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteMySexyMobilePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'MySexyMobilePerformer'

    start_urls = [
        'https://mysexmobile.com',
    ]

    def start_requests(self):
        url = "https://mysexmobile.com/girls"
        yield scrapy.Request(url, callback=self.get_performers, meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="row"]/a[contains(@href, "/girls")]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./div/p/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('./div/div[@class="img"]/@style').get()
            image = re.search(r'\'(http.*)\'', image)
            if image:
                item['image'] = image.group(1)
            else:
                item['image'] = ''

            item['url'] = performer.xpath('./@href').get()
            item['network'] = 'My Sexy Mobile'
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
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''

            yield item
