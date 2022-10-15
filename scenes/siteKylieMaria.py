#  Historical site only.  Not being updated
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteKylieMariaSpider(BaseSceneScraper):
    name = 'KylieMaria'
    network = 'Kylie Maria'
    parent = 'Kylie Maria'
    site = 'Kylie Maria'

    selector_map = {
        'external_id': r'',
        'pagination': ''
    }

    def start_requests(self):
        url = 'https://kyliemaria.xxx/api/content.load?_method=content.load&tz=0&fields[0]=generatedContentLink&[fields][0]=id&fields[1]=title&fields[2]=_resources.primary.url&fields[4]=sites.publishDate&fields[5]=description&fields[6]=length&fields[7]=tags&fields[8]=_tags._last&fields[9]=_tags.alias&fields[10]=_resources.base.url&metaFields[resources][thumb]=baseline.sprite.w225i&transitParameters[showOnHome]=true&transitParameters[v1]=ykYa8ALmUD&transitParameters[v2]=ykYa8ALmUD&transitParameters[preset]=scene&limit=300'
        yield scrapy.Request(url, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['response']['collection']
        for scene in jsondata:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene['title'])
            item['duration'] = scene['length']
            item['description'] = scene['description']
            item['id'] = scene['id']
            item['tags'] = []
            if "collection" in scene['tags']:
                for tag in scene['tags']['collection']:
                    item['tags'].append(self.cleanup_title(scene['tags']['collection'][tag]['alias']))
            item['tags'] = list(filter(None, item['tags']))
            if scene['sites']['collection']:
                for dateid in scene['sites']['collection']:
                    item['date'] = self.parse_date(scene['sites']['collection'][dateid]['publishDate']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            item['performers'] = ["Kylie Maria"]
            item['type'] = "Scene"
            item['image'] = scene['_resources']['primary'][0]['url']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['url'] = "https://kyliemaria.xxx/"
            item['site'] = "Kylie Maria"
            item['parent'] = "Kylie Maria"
            item['network'] = "Kylie Maria"
            item['trailer'] = ''
            yield item
