from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SitePPPTVPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/en/actress?sort=a.position&direction=asc&page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'PPPTVPerformer'

    start_urls = [
        'https://p-p-p.tv',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[contains(@class, "model-card") and contains(@class, "mt-4")]')
        for performer in performers:
            item = PerformerItem()

            perf_name = performer.xpath('.//div[contains(@class, "model-card-title")]/text()').get()
            item['name'] = self.cleanup_title(perf_name.strip())
            if "/" in item['name']:
                names = item['name'].split("/")
                item['name'] = self.cleanup_title(names[-1])
            image = performer.xpath('.//a/img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['bio'] = ''
            if "Ts " in item['name']:
                item['gender'] = 'Trans Female'
            else:
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
            item['network'] = 'P-P-P TV'
            item['url'] = self.format_link(response, performer.xpath('.//a[contains(@class, "profile-link")]/@href').get())

            yield item
