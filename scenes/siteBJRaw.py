import re
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class BJRawSpider(BaseSceneScraper):
    name = 'BJRaw'

    start_urls = [
        'https://www.bjraw.com',
        'https://www.gotfilled.com',
        'https://sexymodernbull.com'
    ]

    selector_map = {
        'title': "",
        'description': "",
        'date': "",
        'performers': "",
        'tags': "",
        'external_id': '',
        'image': '',
        'trailer': '',
        'pagination': '/tour/videos?page=%s'
    }

    def get_next_page_url(self, base, page):
        if "sexymodernbull" in base:
            pagination = '/videos?page=%s&order_by=publish_date&sort_by=desc'
        else:
            pagination = '/tour/videos?page=%s'
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            scenes = jsondata['props']['pageProps']['contents']['data']
            for scene in scenes:
                item = SceneItem()
                item['title'] = scene['title']
                item['description'] = scene['description']
                item['date'] = self.parse_date(re.search(r'(\d{4}/\d{2}/\d{2})', scene['publish_date']).group(1), date_formats=['%Y/%m/%d']).isoformat()
                item['performers'] = scene['models']
                item['tags'] = scene['tags']
                item['id'] = scene['id']
                item['duration'] = self.duration_to_seconds(scene['videos_duration'])
                item['url'] = self.format_link(response, f"/videos/{scene['slug']}").replace(" ", "%20")
                item['trailer'] = scene['trailer_url'].replace(" ", "%20")
                if 'bjraw' in response.url:
                    if "Blowjob" not in item['tags']:
                        item['tags'].append('Blowjob')
                    item['site'] = "BJ Raw"
                    item['parent'] = "BJ Raw"
                    item['network'] = "BJ Raw"
                if 'gotfilled' in response.url:
                    if "Creampie" not in item['tags']:
                        item['tags'].append('Creampie')
                    item['site'] = "Got Filled"
                    item['parent'] = "Got Filled"
                    item['network'] = "Got Filled"
                if 'sexymodernbull' in response.url:
                    if "Interracial" not in item['tags']:
                        item['tags'].append('Interracial')
                    if "BBC" not in item['tags']:
                        item['tags'].append('BBC')
                    item['site'] = "Sexy Modern Bull"
                    item['parent'] = "Sexy Modern Bull"
                    item['network'] = "Sexy Modern Bull"
                if scene['trailer_screencap']:
                    item['image'] = scene['trailer_screencap'].replace(" ", "%20")
                else:
                    item['image'] = scene['thumb'].replace(" ", "%20")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

                yield self.check_item(item, self.days)
