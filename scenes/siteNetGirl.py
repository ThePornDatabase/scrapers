import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteNetGirlSpider(BaseSceneScraper):
    name = 'NetGirl'
    network = 'NetVideoGirls'
    parent = 'NetGirl'
    site = 'NetGirl'

    start_urls = [
        'https://www.netgirl.com/',
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

        url = "https://www.netgirl.com"
        yield scrapy.Request(url, callback=self.get_scenes)

    def get_scenes(self, response):
        jsondata = response.xpath('//script[contains(text(), "pageProps")]/text()').get()
        jsondata = json.loads(jsondata)
        jsondata = jsondata['props']['pageProps']
        for key in jsondata:
            jsongroup = jsondata[key]
            if "year" not in key:
                for scene in jsongroup:
                    item = SceneItem()

                    if "id" in scene and "omg the latest" not in scene['short_title'].lower():
                        item['network'] = 'NetVideoGirls'
                        item['parent'] = 'NetGirl'
                        item['site'] = 'NetGirl'

                        item['date'] = None
                        if "release_date" in scene:
                            if scene['release_date']:
                                item['date'] = self.parse_date(scene['release_date']).isoformat()
                        item['title'] = scene['short_title']
                        item['id'] = scene['id']
                        item['url'] = 'https://www.netgirl.com/'
                        item['duration'] = scene['video_duration']
                        item['image'] = None
                        item['image_blob'] = None
                        if "pinned_thumb" in scene:
                            if not scene['pinned_thumb']:
                                item['image'] = f"https://cdn2.netgirl.com/images/web/{item['id']}-1-med.jpg"
                            elif "thumb" in scene['pinned_thumb']:
                                if "loading" in scene['pinned_thumb']['thumb'] or not scene['pinned_thumb']:
                                    item['image'] = f"https://cdn2.netgirl.com/images/web/{item['id']}-1-med.jpg"
                                else:
                                    item['image'] = f"https://cdn2.netgirl.com/images/web/{scene['pinned_thumb']['thumb']['thumb_name']}"
                                item['image_blob'] = self.get_image_blob_from_link(item['image'])

                        item['description'] = ''
                        item['performers'] = []
                        for model in scene['models']:
                            model_name = f"{model['model_name']}-ID{model['id']}"
                            item['performers'].append(model_name)
                        item['tags'] = ['Amateur', 'Audition']
                        item['trailer'] = ''
                        yield item
