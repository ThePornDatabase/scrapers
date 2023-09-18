import re
import json
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class PerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/rpc/browse?type=models&page=%s&limit=200&filters%5Bactive%5D=1&filters%5Baccess%5D%5B%5D=guest&filters%5Bsite_tags_exclude%5D%5B%5D=mezzanine&filters%5Bpublishdate%5D%5B%5D=2000-01-01+00%3A00%3A00&filters%5Bpublishdate%5D%5B%5D=2023-06-12+20%3A15%3A00&sort=publishdate&order=desc&tagModerationThreshold=10&accessControl%5Busername%5D=Guest',
        'external_id': r'model/(.*)/'
    }

    name = 'AbbyWintersPerformer'
    network = 'Abby Winters'

    start_urls = [
        'https://www.abbywinters.com',
    ]

    def get_next_page_url(self, base, page):
        pagination = f'/rpc/browse?type=models&page={str(page)}&limit=200&filters%5Bactive%5D=1&filters%5Baccess%5D%5B%5D=guest&filters%5Bsite_tags_exclude%5D%5B%5D=mezzanine&filters%5Bpublishdate%5D%5B%5D=2000-01-01+00%3A00%3A00&filters%5Bpublishdate%5D%5B%5D=2023-06-12+20%3A15%3A00&sort=publishdate&order=desc&tagModerationThreshold=10&accessControl%5Busername%5D=Guest'
        return self.format_url(base, pagination)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = json.loads(response.text)
        performers = performers['data']['results']
        for performer in performers:
            item = PerformerItem()
            item['name'] = performer['name']
            if performer['height']:
                item['height'] = performer['height'] + "cm"
            else:
                item['height'] = None
            item['url'] = performer['link']['url']
            item['image'] = performer['thumb']['src'].replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            # ~ item['image_blob'] = ''
            item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
            item['gender'] = "Female"
            item['network'] = "Abby Winters"
            item['nationality'] = None
            item['ethnicity'] = None
            item['haircolor'] = None
            item['eyecolor'] = None
            item['astrology'] = None
            item['birthplace'] = None
            item['birthday'] = None
            item['cupsize'] = None
            item['measurements'] = None
            item['ethnicity'] = None
            item['piercings'] = None
            item['tattoos'] = None
            item['fakeboobs'] = None
            item['weight'] = None
            item['bio'] = None

            yield(item)
