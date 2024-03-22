import re
import scrapy
from tpdb.items import PerformerItem
from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteGapeMyPussyPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '',
        'external_id': r'model/(.*)/'
    }

    name = 'GapeMyPussyPerformer'
    network = 'Apollo Cash'

    start_urls = [
        'https://www.gapemypussy.com',
    ]

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        link = "https://www.gapemypussy.com/pussy-gaping-hd-download.php?pagem="
        yield scrapy.Request(link, callback=self.get_performers, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_performers(self, response):
        meta = response.meta
        performers = response.xpath('//a[@class="model_link_abc"]')
        for performer in performers:
            meta['name'] = performer.xpath('./text()[1]').get()
            performer = performer.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, performer), callback=self.parse_performer, meta=meta)

    def parse_performer(self, response):
        meta = response.meta
        item = PerformerItem()

        item['name'] = self.cleanup_title(meta['name'])
        image = response.xpath('//img[contains(@src, "1_2")]/@src')
        if image:
            item['image'] = self.format_link(response, image.get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image'] = ""
            item['image_blob'] = ""
        item['bio'] = ''
        item['gender'] = 'Female'
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
        item['network'] = 'Apollo Cash'
        item['url'] = response.url
        if "&nats" in item['url']:
            item['url'] = re.search(r'(.*)\&nats', item['url']).group(1)

        yield item
