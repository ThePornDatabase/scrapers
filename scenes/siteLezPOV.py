import re
import html
import json
import requests
import unidecode
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLezPOVSpider(BaseSceneScraper):
    name = 'LezPOV'
    network = "Lez POV"
    parent = "Lez POV"
    site = "Lez POV"

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://www.lezpov.com',
    ]

    headers = {
        'age_gate': '18',
        'wpml_browser_redirect_test': '0',
    }

    selector_map = {
        'performers': '//span[@itemprop="actors"]/a/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/wp-json/wp/v2/posts?page=%s&per_page=10'
    }

    def get_scenes(self, response):

        reqheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()
            item['id'] = scene['id']
            item['url'] = scene['link']
            item['date'] = scene['date']
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).replace("\n", " ").strip())

            item['image'] = ''
            item['image_blob'] = ''
            link = f"https://www.lezpov.com/wp-json/wp/v2/media?parent={item['id']}"
            req = requests.get(link, headers=reqheaders, timeout=10)
            if req and len(req.text) > 5:
                imagelist = json.loads(req.text)
                item['image'] = imagelist[0]['guid']['rendered']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['description'] = scene['excerpt']['rendered']
            if item['description']:
                item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', item['description'])).replace("\n", " ").strip())

            item['performers'] = []
            for performer in scene['tags']:
                link = f"https://www.lezpov.com/wp-json/wp/v2/tags/{performer}"
                req = requests.get(link, headers=reqheaders, timeout=10)
                if req and len(req.text) > 5:
                    performerlist = json.loads(req.text)
                    if "name" in performerlist:
                        item['performers'].append(performerlist['name'])

            item['tags'] = []

            item['trailer'] = ""
            item['site'] = "Lez POV"
            item['parent'] = "Lez POV"
            item['network'] = "Lez POV"

            yield self.check_item(item, self.days)
