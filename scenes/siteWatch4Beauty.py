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
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], response),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        for scene in response.json():
            if scene['issue_category'] == 6 or scene['issue_video_present'] == 1:
                yield scrapy.Request(url=self.format_link(response, '/api/issues/' + scene['issue_simple_title']), callback=self.parse_scene)

    def parse_scene(self, response):
        data = response.json()
        item = SceneItem()

        if len(data):
            data = data[0]

            item['title'] = data['issue_title']
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
            item['url'] = "https://www.watch4beauty.com/updates/" + data['issue_simple_title']
            item['id'] = data['issue_simple_title']
            item['trailer'] = ''
            item['image'] = "https://s5q3w2t8.ssl.hwcdn.net/production/%s-issue-cover-wide-2560.jpg" % (datetime.fromisoformat(item['date']).strftime('%Y%m%d'))
            item['image_blob'] = None
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

        days = int(self.days)
        if days > 27375:
            filterdate = "0000-00-00"
        else:
            filterdate = date.today() - timedelta(days)
            filterdate = filterdate.strftime('%Y-%m-%d')

        if self.debug:
            if not item['date'] > filterdate:
                item['filtered'] = "Scene filtered due to date restraint"
            print(item)
        else:
            if filterdate:
                if item['date'] > filterdate:
                    yield item
            else:
                yield item

    def get_next_page_url(self, base, page, response=""):
        if response:
            oldestscene = datetime.now().isoformat()
            for scene in response.json():
                date = scene['issue_datetime']
                if "Z" in date:
                    date = date[:-1]
                if date < oldestscene:
                    oldestscene = date
            date = (datetime.fromisoformat(date) - timedelta(days=1)).isoformat() + "Z"
            return "https://www.watch4beauty.com/api/issues?before=" + date
        return "https://www.watch4beauty.com/api/issues?before=" + datetime.now().isoformat()
