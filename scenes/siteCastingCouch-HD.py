import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteCastingCouchHDSpider(BaseSceneScraper):
    name = 'CastingCouchHD'
    network = 'NetVideoGirls'
    parent = 'CastingCouch-HD'
    site = 'CastingCouch-HD'

    start_urls = [
        'https://www.castingcouch-hd.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': ''
    }

    def start_requests(self):

        url = "https://www.castingcouch-hd.com/"
        yield scrapy.Request(url, callback=self.get_scenes)

    def get_scenes(self, response):
        jsondata = response.xpath('//script[contains(text(), "pageProps")]/text()').get()
        jsondata = json.loads(jsondata)
        jsondata1 = jsondata['props']['pageProps']['videos']
        jsondata2 = jsondata['props']['pageProps']['popular']
        jsondata = jsondata1 + jsondata2
        for scene in jsondata:
            # ~ json_formatted_str = json.dumps(scene, indent=2)
            # ~ print(json_formatted_str)

            item = SceneItem()

            item['network'] = 'NetVideoGirls'
            item['parent'] = 'CastingCouch-HD'
            item['site'] = 'CastingCouch-HD'

            item['date'] = scene['release_date']
            item['title'] = scene['short_title']
            item['id'] = scene['id']
            item['url'] = 'https://www.castingcouch-hd.com/'

            if scene['pinned_thumb'] and scene['pinned_thumb']['thumb']['thumb_name']:
                item['image'] = "https://media.castingcouch-hd.com/web-images/" + scene['pinned_thumb']['thumb']['thumb_name']
            else:
                item['image'] = "https://media.castingcouch-hd.com/web-images/%s-1-med.jpg" % item['id']
            item['image_blob'] = False

            item['description'] = ''
            performers = []
            for model in scene['models']:
                performers.append(model['model_name'])
            item['performers'] = performers
            item['tags'] = ['Amateur', 'Audition']
            item['trailer'] = "https://media.castingcouch-hd.com/video-thumbs/%s-video.mp4" % item['id']
            if item['date'] > "2020-10-01":
                yield item
