import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteIndustryInvadersSpider(BaseSceneScraper):
    name = 'IndustryInvaders'
    network = 'Industry Invaders'
    parent = 'Industry Invaders'
    site = 'Industry Invaders'

    start_urls = [
        'https://www.industryinvaders.com',
    ]

    custom_settings = {
        'USE_PROXY': True,
    }

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/videos/page:%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        jsondata = response.xpath('//script[contains(text(), "siteData")]/text()').get()
        jsondata = jsondata.replace("\r", "").replace("\n", "").replace("\t", "").replace("  ", " ").replace("  ", " ").replace("  ", " ")
        jsondata = re.search(r'siteData\s?=\s?(\{.*?\})\s+?let', jsondata)
        if jsondata:
            jsondata = jsondata.group(1)
            jsondata = re.sub(r'\s+\}', '}', jsondata)
            jsondata = re.sub(r'\{\s+', '{', jsondata)
            jsondata = re.sub(r'\s+\]', ']', jsondata)
            jsondata = re.sub(r'\[\s+', '[', jsondata)
            jsondata = re.sub(r',\s+', ',', jsondata)
            jsondata = jsondata.replace(",]", "]")
            jsondata = jsondata.replace("\\x27", "'")
            jsondata = json.loads(jsondata)
            for scene in jsondata['posts']:
                item = SceneItem()

                item['title'] = scene['title']
                item['id'] = scene['id']
                item['performers'] = [scene['model_name']]
                image = ''
                for img in scene['slides']:
                    if "img" in img:
                        if ".jpg" in img['img'] and "logo" not in img['img'] and "subscribe" not in img['img']:
                            image = img['img']
                if not image:
                    image = scene['img']
                item['image_blob'] = self.get_image_blob_from_link(image)
                if "?" in image:
                    item['image'] = re.search(r'(.*)\?', image).group(1)
                else:
                    item['image'] = image
                item['description'] = scene['description']
                item['date'] = self.parse_date('today').isoformat()
                item['url'] = f"https://www.industryinvaders.com/{scene['slug']}"
                item['tags'] = []
                item['trailer'] = ''
                item['site'] = "Industry Invaders"
                item['parent'] = "Industry Invaders"
                item['network'] = "Industry Invaders"
                item['type'] = 'Scene'
                yield item
