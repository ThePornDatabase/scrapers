import re
import html
import json
import unidecode
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteStripzVRSpider(BaseSceneScraper):
    name = 'StripzVR'

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://www.stripzvr.com',
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
        'pagination': '/index.php/wp-json/wp/v2/pages?page=%s&per_page=10'
    }

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()

            item['id'] = str(scene['id'])
            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['date']).group(1)
            item['performers'] = []
            title = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).strip())
            if "@" in title:
                title = re.search(r'(.*)@', title).group(1)
                title = title.strip()
                if "Featuring" in title:
                    item['performers'] = [re.search(r'Featuring (.*)', title).group(1)]
                    title = re.search(r'(.*?) Featuring', title).group(1)
                if "featuring" in title:
                    item['performers'] = [re.search(r'featuring (.*)', title).group(1)]
                    title = re.search(r'(.*?) featuring', title).group(1)
            item['title'] = title
            item['image'] = scene['yoast_head_json']['og_image'][0]['url']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['trailer'] = None
            if "description" in scene['yoast_head_json'] and scene['yoast_head_json']['description']:
                item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['yoast_head_json']['description'])).strip())
            else:
                item['description'] = ''
            item['tags'] = []
            item['site'] = 'StripzVR'
            item['parent'] = 'StripzVR'
            item['network'] = 'StripzVR'
            item['url'] = scene['link']

            if not re.search(r'(https://www.stripzvr.com/p\d+/)', item['url']) and re.search(r'https://www.stripzvr.com/(.*)', item['url']):
                yield self.check_item(item, self.days)
