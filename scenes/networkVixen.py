import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class VixenScraper(BaseSceneScraper):
    name = 'Vixen'
    network = 'vixen'

    start_urls = [
        'https://vixen.com',
        'https://www.blacked.com/',
        'https://www.tushy.com',
        'https://www.blackedraw.com/',
        'https://www.tushyraw.com',
        'https://deeper.com',
    ]

    selector_map = {
        'external_id': 'api\\/(.+)',
        'pagination': '/api/videos?size=20&page=%s'
    }

    max_pages = 10

    def get_scenes(self, response):
        for scene in response.json()['data']['videos']:
            yield scrapy.Request(url=self.format_link(response, '/api' + scene['targetUrl']), callback=self.parse_scene)

    def parse_scene(self, response):
        data = response.json()['data']['video']
        scene = SceneItem()

        largest = 0
        for image in data['images']['poster']:
            if image['width'] > largest:
                scene['image'] = image['src']
            largest = image['width']

        largest = 0
        for trailer in data['previews']['poster']:
            if trailer['width'] > largest:
                scene['trailer'] = trailer['src']
            largest = trailer['width']

        scene['title'] = data['title']
        scene['description'] = data['description']
        scene['site'] = data['primarySite']
        scene['date'] = dateparser.parse(data['releaseDate']).isoformat()
        scene['url'] = self.format_link(response, data['targetUrl'])

        scene['performers'] = []
        for model in data['models']:
            scene['performers'].append(model)

        scene['tags'] = []
        for tag in data['categories']:
            scene['tags'].append(tag['name'])

        scene['id'] = data['id']
        scene['network'] = self.network
        scene['parent'] = self.parent

        yield scene
