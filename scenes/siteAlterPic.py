import string
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAlterPicSpider(BaseSceneScraper):
    name = 'AlterPic'
    network = 'AlterPic'

    start_urls = [
        # ~ 'https://alterpic.adultmembersites.com',
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
        item['title'] = jsonrow['title']
        item['description'] = jsonrow['description']
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

        item['date'] = dateparser.parse(jsonrow['publish_date']).isoformat()
        item['trailer'] = ''
        item['tags'] = []
        for tag in jsonrow['tags']:
            item['tags'].append(string.capwords(tag['name']))

        item['image'] = jsonrow['poster_src']
        item['image_blob'] = None

        if item['id'] and item['title']:
            yield item
