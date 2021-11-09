import html
import string
import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteLoveWettingPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//div[@class="update_details"]/a[1]/text()',
        'image': "//div[contains(@class,'image_area')]/img[@class='img-responsive']/@src",
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'LoveWettingPerformer'

    start_urls = [
        'https://www.lovewetting.com',
    ]

    def start_requests(self):
        url = "https://www.lovewetting.com/wetting-czech-models.html"
        yield scrapy.Request(url, callback=self.get_performers, meta={'page': self.page}, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[@class="item"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('.//h3/text()').get()
            if name:
                item['name'] = string.capwords(html.unescape(name.strip()))

            image = performer.xpath('./div/img/@src').get()
            if image:
                item['image'] = self.format_link(response, image).replace(" ", "%20")
            else:
                item['image'] = None
            item['image_blob'] = None

            url = performer.xpath('./div[@class="box-info"]/a/@href').get()
            if url:
                item['url'] = self.format_link(response, url.strip()).replace(" ", "%20")

            item['network'] = 'Love Wetting'

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
