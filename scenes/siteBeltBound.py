import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBeltBoundSpider(BaseSceneScraper):
    name = 'BeltBound'
    network = 'Belt Bound'
    parent = 'Belt Bound'
    site = 'Belt Bound'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://www.beltbound.com',
    ]

    selector_map = {
        'external_id': r'.*/(.*?)/',
        'pagination': '/updates-2/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="post"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('./h2/a/text()').get()).strip()
            item['description'] = scene.xpath('./p[2]/text()').get().strip()
            item['url'] = scene.xpath('./h2/a/@href').get()
            item['id'] = re.search(r'.*/(.*?)/', item['url']).group(1)
            item['image'] = scene.xpath('./a[1]/img/@src').get().replace(" ", "%20").replace("[", "%5B").replace("]", "%5D")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = scene.xpath('.//a[contains(@href, "/tag/")]/text()').getall()
            item['tags'] = scene.xpath('.//a[contains(@href, "/category/")]/text()').getall()
            item['tags'].append('Bondage')
            scenedate = scene.xpath('./h3/text()').get()
            scenedate = re.search(r'(\w+ \d{1,2}\w{2}?, \d{4})', scenedate).group(1)
            item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).isoformat()
            item['trailer'] = ''
            item['site'] = "Belt Bound"
            item['parent'] = "Belt Bound"
            item['network'] = "Belt Bound"
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
