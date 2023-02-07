from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class MoviesR18PerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/videos/vod/movies/actress/?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'R18MoviesPerformer'
    network = 'R18'

    start_urls = [
        'https://www.r18.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//ul[contains(@class,"cmn-list")]/li')
        for performer in performers:
            item = PerformerItem()

            name = performer.xpath('./a/div/div/text()').getall()
            name = " ".join(name)
            item['name'] = self.cleanup_title(name)
            item['image'] = self.format_link(response, performer.xpath('.//img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['bio'] = ''
            item['gender'] = 'Female'
            item['astrology'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = 'Asian'
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''
            item['network'] = 'R18'
            item['url'] = self.format_link(response, performer.xpath('./a/@href').get())

            yield item
