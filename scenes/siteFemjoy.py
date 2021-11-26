from datetime import date, timedelta
import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteFemjoySpider(BaseSceneScraper):
    name = 'FemJoy'
    network = 'FemJoy'
    parent = 'FemJoy'

    start_urls = {
        'https://femjoy.com/',
    }

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': r'updates/(.*)\.html$',
        'trailer': '//video/source/@src',
        'pagination': '/api/v2/videos?include=actors%2Cdirectors&sorting=date&thumb_size=850x463&limit=24&page={}'
    }

    def get_scenes(self, response):
        itemlist = []
        jsondata = json.loads(response.text)
        data = jsondata['results']
        for jsonentry in data:
            item = SceneItem()

            item['performers'] = []
            for model in jsonentry['actors']:
                item['performers'].append(model['name'].title())

            item['title'] = self.cleanup_title(jsonentry['title'])
            item['description'] = self.cleanup_description(jsonentry['long_description'])
            if not item['description']:
                item['description'] = ''

            item['image'] = jsonentry['thumb']['image']
            if not item['image']:
                item['image'] = None
            item['image_blob'] = None
            item['id'] = jsonentry['id']
            item['trailer'] = ''
            item['url'] = "https://femjoy.com" + jsonentry['url']
            item['date'] = self.parse_date(jsonentry['release_date'].strip()).isoformat()
            item['site'] = "FemJoy"
            item['parent'] = "FemJoy"
            item['network'] = "FemJoy"

            item['tags'] = []

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
                        itemlist.append(item.copy())
                else:
                    itemlist.append(item.copy())

            item.clear()
        return itemlist

    def get_next_page_url(self, base, page):
        url = self.format_url(base, self.get_selector_map('pagination').format(page))
        return url
