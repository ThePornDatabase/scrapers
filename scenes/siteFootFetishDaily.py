import re
from datetime import date, timedelta
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteFootFetishDailySpider(BaseSceneScraper):
    name = 'FootFetishDaily'
    network = 'Foot Fetish Daily'
    parent = 'Foot Fetish Daily'
    site = 'Foot Fetish Daily'

    start_urls = [
        'https://footfetishdaily.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '//div[@class="main_column"]/div/a/img[@class="sample_thumbs"]',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'(.*)',
        'pagination': '/guest/scenes/page/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="main_column"]/div[@class="sample_spacings"]')
        for scene in scenes:
            item = SceneItem()
            title = scene.xpath('./p/a/text()')
            if title:
                title = title.get()
            if title and "photos" not in title.lower():
                item['title'] = string.capwords(title.strip())
            else:
                item['title'] = ''

            image = scene.xpath('./a/img/@src')
            if image:
                image = image.get().strip()
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'update_thumbs/(\d+)_t', item['image']).group(1)
            else:
                item['image'] = None
                item['image_blob'] = None
                item['id'] = None

            item['url'] = response.url
            item['description'] = None
            item['trailer'] = None
            item['performers'] = []
            item['tags'] = ['Foot Fetish', 'Feet']
            item['site'] = "Foot Fetish Daily"
            item['parent'] = "Foot Fetish Daily"
            item['network'] = "Foot Fetish Daily"

            scenedate = scene.xpath('./p/a/following-sibling::text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get()).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            if item['title'] and item['id']:
                days = int(self.days)
                if days > 27375:
                    filterdate = "0000-00-00"
                else:
                    filterdate = date.today() - timedelta(days)
                    filterdate = filterdate.strftime('%Y-%m-%d')

                if self.debug:
                    if not item['date'] > filterdate:
                        item['filtered'] = "Scene filtered due to date restraint"
                    print(item)
                else:
                    if filterdate:
                        if item['date'] > filterdate:
                            yield item
                    else:
                        yield item
