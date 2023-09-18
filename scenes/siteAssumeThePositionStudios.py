import datetime
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAssumeThePositionStudiosSpider(BaseSceneScraper):
    name = 'AssumeThePositionStudios'
    network = 'Spanking Online'

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
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        meta['days'] = self.days
        tod = datetime.datetime.now()
        d = datetime.timedelta(days=int(meta['days']))
        a = tod - d
        meta['check_date'] = a.strftime('%Y-%m-%d')
        # Spanking Online: 3, Spanking Online: 8, Strictly English Online: 9, Good Spanking: 11, Assume The Position Studios: 13, Spanking Online: 14, Spanking Online: 15, Universal Spanking: 22

        for x in range(100):
            link = f"https://www.assumethepositionstudios.com/api/site/{x}/updates/0"
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['data']
        for scene in jsondata:
            item = SceneItem()
            item['id'] = scene['id']
            item['date'] = scene['live_date']
            item['site'] = scene['producer']['name']
            item['parent'] = scene['producer']['name']
            item['network'] = "Spanking Online"
            if "Spanking Online" in item['site']:
                item['url'] = f"{scene['producer']['url'].replace('http://', 'https://')}/trailer/{item['id']}"
            else:
                item['url'] = f"{scene['producer']['url'].replace('http://', 'https://')}/trailer?updateId={item['id']}"

            meta['site_url'] = scene['producer']['url'].replace('http://', 'https://')
            scene_link = f"{scene['producer']['url'].replace('http://', 'https://')}/api/update/{item['id']}/trailer/"
            if item['date'] >= meta['check_date']:
                meta['item'] = item.copy()
                meta['scene'] = scene.copy()
                yield scrapy.Request(scene_link, callback=self.parse_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        meta = response.meta
        item = meta['item']
        jsondata = response.json()
        jsondata = jsondata['data']
        try:
            item['title'] = jsondata['scene']['title']
            item['description'] = jsondata['scene']['description']
            item['tags'] = ['Spanking']
            item['performers'] = []
            for model in jsondata['models']:
                item['performers'].append(model['name'].replace("\r", "").replace("\n", ""))
            if "trailer" in jsondata and jsondata['trailer']:
                item['trailer'] = meta['site_url'] + "/" + jsondata['trailer']['link']
            else:
                item['trailer'] = ''
            item['trailer'] = item['trailer'].replace(" ", "%20")
            if "image" in jsondata and jsondata['image']:
                item['image'] = meta['site_url'] + "/" + jsondata['image']
                item['image'] = item['image'].replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            if "Best of the Brits - Remastered - Vol 5" not in item['title']:
                yield item
        except:
            print(f"API Not pulling for scene:  ID: {meta['scene']['id']}   Title: {meta['scene']['scene']['title']}   Site: {meta['scene']['producer']['name']}   Date: {meta['scene']['live_date']}")
