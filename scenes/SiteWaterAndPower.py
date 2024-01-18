import re
import json
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteWaterAndPowerSpider(BaseSceneScraper):
    name = 'WaterAndPower'
    network = 'Water And Power'
    parent = 'Water And Power'
    site = 'Water And Power'

    start_urls = [
        'https://water-and-power.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/page-data/videos/%s/page-data.json',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        if page == 1:
            return "https://water-and-power.com/page-data/index/page-data.json"
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['result']['data']
        if response.meta['page'] == 1:
            jsondata = jsondata['videos']['nodes']
        else:
            jsondata = jsondata['allMarkdownRemark']['nodes']
        for scene in jsondata:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene['frontmatter']['title'])
            item['description'] = re.sub(r'<[^<]+?>', '', self.cleanup_description(scene['summary']))
            item['date'] = ''
            item['performers'] = list(map(lambda x: string.capwords(x.strip()), scene['frontmatter']['girls']))
            item['tags'] = list(map(lambda x: string.capwords(x.strip()), scene['frontmatter']['tags']))
            item['url'] = f"https://water-and-power.com/videos{scene['fields']['slug']}"
            item['id'] = scene['frontmatter']['streamId']
            image = "https://images-wap.imgix.net" + scene['frontmatter']['hero']
            if image:
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
            else:
                item['image'] = ''
                item['image_blob'] = ''

            item['type'] = 'Scene'
            item['trailer'] = ''
            item['site'] = "Water And Power"
            item['parent'] = "Water And Power"
            item['network'] = "Water And Power"

            yield item
