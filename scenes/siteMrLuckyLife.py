import re
import string
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMrLuckyLifeSpider(BaseSceneScraper):
    name = 'MrLuckyLife'
    network = 'Mr Lucky Life'
    parent = 'Mr Lucky Life'
    site = ''

    start_urls = [
        'https://www.mrluckylife.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/categories/Movies.html',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        link = 'https://www.mrluckylife.com/categories/Movies.html'
        yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        jsondata = re.search(r'var set = (\[\{.*\}\])', response.text)
        imagerow = re.search(r'var array_img_gallery.*?(\[.*?\]);', response.text)
        if imagerow:
            imagerow = imagerow.group(1)
            imagerow = imagerow.encode('ascii').decode('unicode-escape')
            imagerow = imagerow.replace('\\/', '/').replace('\\"', '"')
        if jsondata:
            jsondata = json.loads(jsondata.group(1))
            # ~ print(jsondata)
            for scene in jsondata:
                item = SceneItem()

                item['title'] = self.cleanup_title(scene['Title'])
                item['date'] = scene['AppearDate']
                item['description'] = scene['Description']
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), scene['SEOkey'].split(",")))
                if 'movie_length' in scene['info'] and scene['info']['movie_length']:
                    item['duration'] = str(int(scene['info']['movie_length']))
                else:
                    item['duration'] = ''
                item['trailer'] = self.format_link(response, scene['trailer_url'])
                item['id'] = scene['Id']
                item['url'] = f'https://www.mrluckylife.com/updates/{scene["SEOname"]}.html'
                item['image'] = re.search(f'.*[\'\"](https.*?{scene["Directory"]}.*?)[\'\"].*', imagerow).group(1)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['performers'] = []
                if "models" in scene['info'] and scene['info']['models']:
                    for model in scene['info']['models']:
                        item['performers'].append(model['name'])
                item['site'] = 'Mr Lucky Life'
                item['parent'] = 'Mr Lucky Life'
                item['network'] = 'Mr Lucky Life'
                yield self.check_item(item, self.days)
