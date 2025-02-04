from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class NetworkBarebackPlusPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'BarebackPlusPerformer'
    network = 'BarebackPlus'

    start_urls = [
        'https://barebackplus.com',
    ]


    def get_performers(self, response):
        performers = response.xpath('//div[@class="grid-item-model"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//h4/text()').get())
            if "modelname" not in item['name']:
                image = performer.xpath('.//img/@data-src')
                if image:
                    item['image'] = self.format_link(response, image.get())
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                else:
                    item['image'] = ""
                    item['image_blob'] = ""
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
                item['network'] = 'BarebackPlus'
                item['url'] = self.format_link(response, performer.xpath('./div[1]/a/@href').get())


                yield item
