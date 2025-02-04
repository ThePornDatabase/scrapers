from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteBoysHalfwayHousePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/models?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'BoysHalfwayHousePerformer'

    start_urls = [
        'https://www.boyshalfwayhouse.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="model_container"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./div[contains(@class, "model_title")]//a/text()').get())
            image = performer.xpath('./figure/a/img/@src')
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
            item['network'] = 'BoysHalfwayHouse'
            item['url'] = self.format_link(response, performer.xpath('./figure/a/@href').get())

            yield item
