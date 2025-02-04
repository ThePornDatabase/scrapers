from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteTrans4TheFansPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/pornstars/page/%s/?sort=latest',
        'external_id': r'model/(.*)/'
    }

    name = 'Trans4TheFansPerformer'

    start_urls = [
        'https://trans4thefans.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//ul[@class="model-listing"]/li')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./h2/a/text()').get())
            image = performer.xpath('.//img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['bio'] = ''
            item['gender'] = 'Transgender Female'
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
            item['network'] = 'Trans4TheFans'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
