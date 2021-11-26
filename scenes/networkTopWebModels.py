import re
from datetime import date, timedelta
import json
import string

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        '2girls1camera': "2 Girls, 1 Camera",
        'BigGulpGirls': "Big Gulp Girls",
        'CougarSeason': "Cougar Season",
        'DeepthroatSirens': "Deepthroat Sirens",
        'FacialsForever': "Facials Forever",
        'PoundedPetite': "Pounded Petite",
        'ShesBrandNew': "She's Brand New",
    }
    return match.get(argument, argument)


class TopWebModelsSpider(BaseSceneScraper):
    name = 'TopWebModels'
    network = 'TopWebModels'

    start_urls = [
        'https://tour.topwebmodels.com/'
        # 'https://www.2girls1camera.com',
        # 'https://www.biggulpgirls.com',
        # 'https://www.cougarseason.com',
        # 'https://www.deepthroatsirens.com',
        # 'https://www.facialsforever.com',
        # 'https://www.poundedpetite.com',
        # 'https://www.shesbrandnew.com'
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
        'pagination': '/scenes?type=new&page=%s'
    }

    def get_scenes(self, response):
        responseresult = response.xpath('//script[contains(text(),"window.__DATA__")]/text()').get()
        responsedata = re.search(r'__DATA__\ =\ (.*)', responseresult).group(1)
        jsondata = json.loads(responsedata)
        data = jsondata['data']['videos']['items']
        for jsonentry in data:
            item = SceneItem()
            item['title'] = jsonentry['title']
            item['description'] = jsonentry['description']
            item['description'] = re.sub('<[^<]+?>', '', item['description']).strip()
            item['image'] = jsonentry['thumb']
            if not isinstance(item['image'], str):
                item['image'] = None
            else:
                item['image'] = item['image'].replace(" ", "%20")
            item['image_blob'] = None
            item['id'] = jsonentry['id']
            item['trailer'] = ''
            urltext = re.sub(r'[^A-Za-z0-9 ]+', '', jsonentry['title']).lower()
            urltext = urltext.replace("  ", " ")
            urltext = urltext.replace(" ", "-")
            urltext = "https://tour.topwebmodels.com/scenes/" + str(jsonentry['id']) + "/" + urltext
            item['url'] = urltext
            item['date'] = jsonentry['release_date']
            item['site'] = match_site(jsonentry['sites'][0]['name'])
            item['network'] = 'TopWebModels'
            item['parent'] = 'TopWebModels'

            item['performers'] = []
            for model in jsonentry['models']:
                if " and " in model['name'].lower():
                    modellist = model['name'].split(" and ")
                    if modellist:
                        for model in modellist:
                            item['performers'].append(model.title())
                if " & " in model['name'].lower():
                    modellist = model['name'].split(" & ")
                    if modellist:
                        for model in modellist:
                            item['performers'].append(model.title())
                else:
                    item['performers'].append(model['name'])

            item['tags'] = []
            for tags in jsonentry['tags']:
                if "scott's picks" not in tags['name'].lower():
                    item['tags'].append(string.capwords(tags['name']))

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
