import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteTheLisaAnnSpider(BaseSceneScraper):
    name = 'TheLisaAnn'

    start_urls = [
        'https://www.thelisaann.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/updates/page_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updates clear"]')
        for scene in scenes:
            item = SceneItem()
            item['site'] = "The Lisa Ann"
            item['parent'] = "The Lisa Ann"
            item['network'] = "The Lisa Ann"
            item['date'] = ""

            item['title'] = self.cleanup_title(scene.xpath('.//h3/a/text()').get())
            item['image'] = self.format_link(response, scene.xpath('.//img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['description'] = scene.xpath('./div/p/text()').get().strip()
            item['tags'] = []
            item['performers'] = ['Lisa Ann']
            sceneid = re.search(r'/content/(.*)/', item['image']).group(1)
            item['url'] = f"https://www.thelisaann.com/content/{sceneid}"
            item['id'] = sceneid
            trailer = scene.xpath('./div/a[contains(@onclick, "content")]/@onclick')
            if trailer:
                trailer = re.search(r'(/content.*?\.mp4)', trailer.get()).group(1)
                trailer = self.format_link(response, trailer)
            else:
                trailer = ""
            item['trailer'] = trailer

            yield item
