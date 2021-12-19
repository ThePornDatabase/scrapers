import re
from datetime import date, timedelta
import json

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class BJRawSpider(BaseSceneScraper):
    name = 'BJRaw'

    start_urls = [
        'https://www.bjraw.com',
        'https://www.gotfilled.com'
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

    def get_scenes(self, response):
        responseresult = response.xpath('//script[contains(text(),"window.__DATA__")]/text()').get()
        responsedata = re.search(r'__DATA__\ =\ (.*)', responseresult).group(1)
        jsondata = json.loads(responsedata)
        data = jsondata['videos']['items']
        for jsonentry in data:
            item = SceneItem()
            item['title'] = jsonentry['title']
            item['description'] = jsonentry['description']
            item['description'] = re.sub('<[^<]+?>', '', item['description']).strip()
            item['image'] = jsonentry['trailer']['poster']
            if not isinstance(item['image'], str):
                item['image'] = None
            item['image_blob'] = None
            item['id'] = jsonentry['id']
            item['trailer'] = jsonentry['trailer']['src']
            if item['trailer'] == "https://c2d8j4g8.ssl.hwcdn.net/6/0/2/5/8/60258852ed44c/bjr0005_rachaelcavalli _trailer.mp4":  # For some reason shows this scene trailer as invalid
                item['trailer'] = ''
            item['date'] = jsonentry['release_date']
            urltext = re.sub(r'[^A-Za-z0-9 ]+', '', jsonentry['title']).lower()
            urltext = urltext.replace("  ", " ")
            urltext = urltext.replace(" ", "-")

            if 'bjraw' in response.url:
                urltext = "https://www.bjraw.com/tour/videos/" + str(jsonentry['id']) + "/" + urltext
                item['tags'] = ['Blowjob']
                item['site'] = "BJ Raw"
                item['parent'] = "BJ Raw"
                item['network'] = "BJ Raw"
            if 'gotfilled' in response.url:
                urltext = "https://www.gotfilled.com/tour/videos/" + str(jsonentry['id']) + "/" + urltext
                item['tags'] = ['Creampie']
                item['site'] = "Got Filled"
                item['parent'] = "Got Filled"
                item['network'] = "Got Filled"

            item['url'] = urltext

            item['performers'] = []
            for model in jsonentry['models']:
                item['performers'].append(model['name'])

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
                        yield item
                else:
                    yield item

            item.clear()
