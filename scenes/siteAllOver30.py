import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAllOver30JSONSpider(BaseSceneScraper):
    name = 'AllOver30JSON'
    network = 'AllOver30'
    parent = 'AllOver30'
    site = 'AllOver30'

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        start_url = 'https://new.allover30.com/GetRecent'
        yield scrapy.Request(start_url, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        jsondata = response.json()
        for group in jsondata:
            for scene in jsondata[group]:
                if "vid" in scene['type'].lower():
                    item = self.init_scene()
                    item['id'] = scene['id']
                    item['performers'] = scene['models']
                    item['performers_data'] = self.get_performers_data(item['performers'], scene['pmodel'])
                    item['title'] = ", ".join(item['performers']) + ": " + scene['type_name']
                    item['date'] = self.parse_date(scene['niceDate'], date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
                    image = f"https://static.allover30.com/{scene['pmodel'][0].lower()}/{scene['pmodel'].lower()}/{item['id']}/cover-large.jpg"
                    item['image'] = image
                    item['image_blob'] = self.get_image_blob_from_link(image)
                    item['tags'] = ['MILF', scene['type_name']]
                    item['site'] = "All Over 30"
                    item['parent'] = "All Over 30"
                    item['network'] = "All Over 30"
                    item['url'] = f"https://members.allover30.com/Movie/{item['id']}"
                    yield item

    def get_performers_data(self, performer_list, pmodel):
        performers_data = []
        if len(performer_list):
            for performer in performer_list:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "All Over 30"
                perf['site'] = "All Over 30"
                if len(performer_list) == 1:
                    perf['image'] = f"https://static.allover30.com/{pmodel[0].lower()}/{pmodel.lower()}/model-thumb.jpg"
                    perf['image_blob'] = self.get_image_blob_from_link(perf['image'])
                performers_data.append(perf)
        return performers_data
