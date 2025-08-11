from datetime import date, timedelta, datetime
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class Watch4BeautyScraper(BaseSceneScraper):
    name = 'Watch4Beauty'
    network = 'Watch4Beauty'

    start_urls = [
        'https://watch4beauty.com',
    ]

    selector_map = {
        'external_id': '',
        'pagination': ''
    }

    def start_requests(self):

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.json()
        for scene in scenes['latest']:
            if ("issue_category" in scene and scene['issue_category'] == 6) or ("issue_video_present" in scene and scene['issue_video_present'] == 1):
                yield scrapy.Request(url=self.format_link(response, '/api/issues/' + scene['issue_simple_title']), callback=self.parse_scene)
            elif "magazine_category" in scene and scene['magazine_category'] == 3:
                yield scrapy.Request(url=self.format_link(response, '/api/magazines/' + scene['magazine_simple_title']), callback=self.parse_magazine)

    def parse_scene(self, response):
        data = response.json()
        item = SceneItem()

        if len(data):
            data = data[0]
            item['title'] = data['issue_title']
            if len(item['title']) < 3:
                item['title'] = item['title'] + "."
            if len(item['title']) < 3:
                item['title'] = item['title'] + "."
            item['date'] = data['issue_datetime']
            if "Z" in item['date']:
                item['date'] = item['date'][:-1]
            item['description'] = data['issue_text']
            item['tags'] = data['issue_tags'].split(",")
            item['tags'] = list(map(str.strip, item['tags']))
            item['tags'] = list(map(str.capitalize, item['tags']))
            item['tags'][:] = [x for x in item['tags'] if x]
            item['site'] = "Watch4Beauty"
            item['network'] = "Watch4Beauty"
            item['parent'] = "Watch4Beauty"
            if "issue_size" in data and data['issue_size']:
                item['duration'] = data['issue_size']
            item['url'] = "https://www.watch4beauty.com/updates/" + data['issue_simple_title']
            item['id'] = data['issue_id']
            item['trailer'] = ''
            item['image'] = "https://mh-c75c2d6726.watch4beauty.com/production/%s-issue-cover-wide-2560.jpg" % (datetime.fromisoformat(item['date']).strftime('%Y%m%d'))
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = []

            modelurl = response.url + "/models"
            yield scrapy.Request(modelurl, callback=self.parse_models, meta={'item': item})

    def parse_magazine(self, response):
        data = response.json()
        item = SceneItem()

        if len(data):
            data = data[0]
            if ("backstage" in data and data['backstage']) or ("fhgbackstage" in data and data['fhgbackstage']):
                item['title'] = data['magazine_title']
                if len(item['title']) < 3:
                    item['title'] = item['title'] + "."
                if len(item['title']) < 3:
                    item['title'] = item['title'] + "."
                item['date'] = data['magazine_datetime']
                if "Z" in item['date']:
                    item['date'] = item['date'][:-1]
                item['description'] = data['magazine_text']
                item['tags'] = data['magazine_tags'].split(",")
                item['tags'] = list(map(str.strip, item['tags']))
                item['tags'] = list(map(str.capitalize, item['tags']))
                item['tags'][:] = [x for x in item['tags'] if x]
                item['site'] = "Watch4Beauty"
                item['network'] = "Watch4Beauty"
                item['parent'] = "Watch4Beauty"
                item['url'] = f"https://www.watch4beauty.com/stories/{data['magazine_simple_title']}"
                item['id'] = data['magazine_id']
                item['trailer'] = ''
                item['image'] = f"https://mh-c75c2d6726.watch4beauty.com/production/{datetime.fromisoformat(item['date']).strftime('%Y%m%d')}-magazine-cover-wide-2560.jpg"
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['performers'] = []

                modelurl = response.url + "/models"
                yield scrapy.Request(modelurl, callback=self.parse_models, meta={'item': item})

    def parse_models(self, response):
        item = response.meta['item']
        data = response.json()
        performers = []

        if len(data):
            models = data[0]['Models']
            for model in models:
                performers.append(model['model_nickname'].strip())

        item['performers'] = performers

        yield self.check_item(item, self.days)

    def get_next_page_url(self, page):
        if int(page) == 1:
            return "https://www.watch4beauty.com/api/updates"
        else:
            return f"https://www.watch4beauty.com/api/updates?skip={str((int(page) - 1) * 50)}"
