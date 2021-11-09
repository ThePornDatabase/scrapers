import warnings
import json
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


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

            item['title'] = jsonentry['title']
            item['description'] = jsonentry['long_description']
            if not item['description']:
                item['description'] = ''

            item['image'] = jsonentry['thumb']['image']
            if not item['image']:
                item['image'] = None
            item['image_blob'] = None
            item['id'] = jsonentry['id']
            item['trailer'] = ''
            item['url'] = "https://femjoy.com" + jsonentry['url']
            item['date'] = dateparser.parse(jsonentry['release_date'].strip()).isoformat()
            item['site'] = "FemJoy"
            item['parent'] = "FemJoy"
            item['network'] = "FemJoy"

            item['tags'] = []

            itemlist.append(item.copy())

            item.clear()
        return itemlist

    def get_next_page_url(self, base, page):
        url = self.format_url(base, self.get_selector_map('pagination').format(page))
        return url
