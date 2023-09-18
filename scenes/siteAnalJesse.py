import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAnalJesseSpider(BaseSceneScraper):
    name = 'AnalJesse'
    network = 'Anal Jesse'

    start_urls = [
        'https://analjesse.com',
    ]

    selector_map = {
        'external_id': r'trailers/(.*?)-',
        'pagination': '/_next/data/uE37ifF-lDeh5oQM044w6/tags/main.json?slug=main&page=%s&per_page=12'
    }

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        if jsondata:
            jsondata = jsondata['pageProps']['contents']
            for scene in jsondata['data']:
                item = SceneItem()
                item['site'] = "Anal Jesse"
                item['parent'] = "Anal Jesse"
                item['network'] = "Anal Jesse"
                item['title'] = self.cleanup_title(scene['title'])
                item['description'] = self.cleanup_text(scene['description'])
                item['performers'] = []
                if "models_slugs" in scene:
                    for performer in scene['models_slugs']:
                        item['performers'].append(performer['name'])
                item['date'] = self.parse_date(scene['publish_date']).isoformat()
                item['id'] = scene['id']
                if scene['videos_duration']:
                    item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['image'] = scene['thumb'].replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['tags'] = []
                item['trailer'] = scene['poster_url'].replace(" ", "%20")
                item['url'] = f"https://analjesse.com/trailers/{scene['slug']}"

                yield self.check_item(item, self.days)
