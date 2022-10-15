import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMetalBondageSpider(BaseSceneScraper):
    name = 'MetalBondage'
    network = 'Metal Bondage'
    parent = 'Metal Bondage'
    site = 'Metal Bondage'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://www.metalbondage.com',
    ]

    selector_map = {
        'external_id': r'.*/(.*?)/',
        'pagination': '/updatespage/page/%s/'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "postwrap")]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.cleanup_title(scene.xpath('.//h2/a/text()').get()).strip()
            item['description'] = scene.xpath('.//div[@class="textcontent"]/p/text()').get().strip()
            item['id'] = re.search(r'^(\w+)', item['title']).group(1)
            item['url'] = scene.xpath('.//h2/a/@href').get()
            item['image'] = scene.xpath('.//center/a[1]/img/@src').get().replace(" ", "%20").replace("[", "%5B").replace("]", "%5D")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = scene.xpath('.//a[contains(@href, "/tag/")]/text()').getall()
            item['tags'] = scene.xpath('.//a[contains(@href, "/category/")]/text()').getall()
            scenedate = scene.xpath('.//div[@class="metabar"]/em/text()').get()
            scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate).group(1)
            item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).isoformat()
            item['trailer'] = ''
            item['site'] = "Metal Bondage"
            item['parent'] = "Metal Bondage"
            item['network'] = "Metal Bondage"
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
