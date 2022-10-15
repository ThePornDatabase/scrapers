from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteLaceyStarrPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/granny/models.php?letter=&search=&p=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'LaceyStarrPerformer'
    network = 'Lacey Starr'

    start_urls = [
        'https://www.laceystarr.com',
    ]

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="vPic"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('./a/following-sibling::p/a/text()').get())
            image = performer.xpath('.//img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''
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
            item['network'] = 'Lacey Starr'
            item['url'] = "https://www.laceystarr.com/granny/" + performer.xpath('./a/@href').get().strip()

            yield item
