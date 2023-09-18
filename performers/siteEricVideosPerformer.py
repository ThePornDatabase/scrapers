import scrapy
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteEricVideosPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/EN/acteurs/',
        'external_id': r'model/(.*)/'
    }

    cookies = {'warning': '1', 'lang': 'EN', 'locale': 'en_US'}

    name = 'EricVideosPerformer'
    network = 'Eric Videos'

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        url = "https://www.ericvideos.com/EN/acteurs/"
        yield scrapy.Request(url, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "acteur")]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = performer.xpath('.//div[@class="nom"]/text()').get()
            item['image'] = self.format_link(response, performer.xpath('.//img/@src').get()).replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = 'Male'
            item['astrology'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''
            item['network'] = 'Eric Videos'
            url = performer.xpath('.//a/@href').get()
            item['url'] = self.format_link(response, url).replace(" ", "%20")

            yield item
