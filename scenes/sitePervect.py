import json
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePervectSpider(BaseSceneScraper):
    name = 'Pervect'
    site = 'Pervect'

    start_urls = [
        'https://pervect.com',
    ]

    selector_map = {
        'title': '//div[@class="container"]/h1/text()',
        'description': '//div[@class="container"]//div[contains(@class, "player-text")]//text()',
        'date': '//meta[@property="video:release_date"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(text(), "Starring:")]/following-sibling::a/text()',
        'tags': '//ul[contains(@class,"player-tag-list")]/li/a/text()',
        'duration': '//meta[@property="video:duration"]/@content',
        'trailer': '//script[contains(text(), "contentUrl")]/text()',
        're_trailer': r'contentUrl.*?(http.*?\.mp4)',
        'external_id': r'.*/(.*?)/',
        'pagination': '/scenes?order_by=publish_date&sort_by=desc&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        jsondata = response.xpath('//script[contains(text(), "site_domain")]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']['contents']['data']
            for scene in jsondata:
                item = self.init_scene()
                item['site'] = scene['site']
                item['parent'] = scene['site']
                item['network'] = "Pervect"
                item['title'] = self.cleanup_title(scene['title'])
                item['description'] = self.cleanup_text(scene['description'])
                item['performers'], item['performers_data'] = self.get_performers_data(scene)
                item['date'] = self.parse_date(scene['publish_date'], date_formats=['%Y/%m/%d']).strftime('%Y-%m-%d')
                if item['date'] < "2024-12-28":
                    item['id'] = scene['slug']
                else:
                    item['id'] = scene['id']

                item['image'] = scene['thumb']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

                item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['tags'] = scene['tags']
                item['trailer'] = scene['trailer_url'].replace(" ", "%20")
                item['url'] = f"https://www.pervect.com/scenes/{scene['slug']}"

                yield self.check_item(item, self.days)

    def get_performers_data(self, jsondata):
        performers = []
        performers_data = []
        if "models_thumbs" in jsondata and jsondata['models_thumbs']:
            for model in jsondata['models_thumbs']:
                perf = {}
                performers.append(model['name'])
                perf['name'] = model['name']
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Pervect"
                perf['site'] = "Pervect"
                perf['image'] = model['thumb']
                perf['image_blob'] = self.get_image_blob_from_link(model['thumb'])
                performers_data.append(perf)
        if "models_slugs" in jsondata and jsondata['models_slugs']:
            for model in jsondata['models_slugs']:
                if model['name'] not in performers:
                    performers.append(model['name'])
        return performers, performers_data
