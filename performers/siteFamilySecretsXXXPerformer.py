import html

from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteFamilySecretsXXXPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/tour/models/models_%s_d.html',
        'external_id': 'girls/(.+)/?$'
    }

    name = 'FamilySecretsXXXPerformer'

    start_urls = [
        'https://familysecretsxxx.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model"]')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./p/a[1]/text()').get()
            if name:
                item['name'] = html.unescape(name.strip().title())

            image = performer.xpath('.//a/img/@src0_2x').get()
            if image:
                item['image'] = "https://familysecretsxxx.com" + image.replace(" ", "%20")
            else:
                item['image'] = None

            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            url = performer.xpath('./div[1]/a[1]/@href').get()
            if url:
                item['url'] = self.format_link(response, url.strip()).replace(" ", "%20")

            item['network'] = 'Exposed Whores Media'

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
