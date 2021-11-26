import string
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAlterPicSpider(BaseSceneScraper):
    name = 'AlterPic'
    network = 'AlterPic'

    start_urls = [
        'https://alterpic.adultmembersites.com',
        'https://kinkyponygirl.adultmembersites.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/api/videos?count=20&page=%s'
    }

    def get_scenes(self, response):
        jsondata = response.json()['data']
        for scene in jsondata:
            if "alterpic" in response.url:
                url = "https://alterpic.adultmembersites.com/api/videos/" + str(scene['id'])
            if "kinkyponygirl" in response.url:
                url = "https://kinkyponygirl.adultmembersites.com/api/videos/" + str(scene['id'])
            yield scrapy.Request(url, callback=self.get_json_scene)

    def get_json_scene(self, response):
        jsonrow = response.json()
        item = SceneItem()
        item['id'] = str(jsonrow['id'])
        item['title'] = self.cleanup_title(jsonrow['title'])
        item['description'] = self.cleanup_description(jsonrow['description'])
        item['performers'] = []
        for performer in jsonrow['casts']:
            item['performers'].append(string.capwords(performer['screen_name']))

        item['network'] = "AlterPic"

        if "alterpic" in response.url:
            item['site'] = "Fetish Clinic"
            item['parent'] = "Fetish Clinic"
            item['url'] = "https://alterpic.com/videos/" + item['id']
        if "kinkyponygirl" in response.url:
            item['site'] = "Kinky Pony Girl"
            item['parent'] = "Kinky Pony Girl"
            item['url'] = "https://kinkyponygirl.com/videos/" + item['id']

        item['date'] = self.parse_date(jsonrow['publish_date']).isoformat()
        item['trailer'] = ''
        item['tags'] = []
        for tag in jsonrow['tags']:
            item['tags'].append(string.capwords(tag['name']))

        item['image'] = jsonrow['poster_src']
        item['image_blob'] = None

        if item['id'] and item['title']:
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
