import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMyPreggoSpider(BaseSceneScraper):
    name = 'MyPreggo'
    network = 'MyPreggo'
    parent = 'MyPreggo'
    site = 'MyPreggo'

    selector_map = {
        'external_id': r'',
        'pagination': '',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        headers = self.headers
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        headers["Referer"] = "https://www.mypreggo.com/updates.php?id=&ref=bookmark"
        headers["X-Requested-With"] = "XMLHttpRequest"
        body = f"categ_id=0&order=0&page={meta['page']}&model_id=0&out=1"

        yield scrapy.Request(url="https://www.mypreggo.com/showvideosajax.php", callback=self.parse, method="POST", meta=meta, body=body, headers=headers)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))

                headers = self.headers
                headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8]"
                headers["X-Requested-With"] = "XMLHttpRequest"
                body = f"categ_id=0&order=0&page={meta['page']}&model_id=0&out=1"

                yield scrapy.Request(url="https://www.mypreggo.com/showvideosajax.php", callback=self.parse, method="POST", meta=meta, body=body, headers=headers)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['sets']
        for scene in jsondata:
            item = SceneItem()
            item['id'] = scene['id']
            item['title'] = self.cleanup_title(scene['longtitle'])
            item['date'] = self.parse_date(scene['vdate'].replace("\\/", "/"), date_formats=['%d/%m/%Y']).strftime('%Y-%m-%d')
            item['performers'] = [scene['model_name']]
            item['image'] = "https:" + scene['icon'].replace("\\/", "/")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['duration'] = self.duration_to_seconds(re.search(r'(\d{1,2}:\d{2})', scene['videos_counter']).group(1))
            item['site'] = "MyPreggo"
            item['network'] = "MyPreggo"
            item['parent'] = "MyPreggo"
            item['type'] = "Scene"
            item['tags'] = ['Pregnant']
            item['description'] = ''
            item['trailer'] = ''
            item['url'] = f"https://www.mypreggo.com/index.php?id={item['id']}&ref=bookmark"
            yield self.check_item(item, self.days)
