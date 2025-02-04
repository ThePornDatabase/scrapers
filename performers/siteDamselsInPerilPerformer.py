from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/show.php?a=246_%s',
        'external_id': r'model/(.*)/'
    }

    name = 'DamselsInPerilPerformer'

    start_urls = [
        'https://damselsinperil.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="itemm"]')
        for performer in performers:
            item = PerformerItem()

            item['name'] = self.cleanup_title(performer.xpath('.//div[@class="nm-name"]/p/text()').get())
            image = performer.xpath('.//img/@src')
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
            item['network'] = 'Damsels In Peril'
            item['url'] = self.format_link(response, performer.xpath('./a[1]/@href').get())

            yield item
