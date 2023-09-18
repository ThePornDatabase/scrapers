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
        # ~ responseresult = response.xpath('//script[contains(text(),"window.__DATA__")]/text()').get()
        responseresult = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        # ~ responsedata = re.search(r'__DATA__\ =\ (.*)', responseresult).group(1)
        jsondata = json.loads(responseresult)
        data = jsondata['props']['pageProps']['contents']['data']
        for jsonentry in data:
            item = SceneItem()
            item['title'] = jsonentry['title']
            # ~ item['description'] = jsonentry['description']
            item['description'] = ""
            # ~ item['description'] = re.sub('<[^<]+?>', '', item['description']).strip()
            item['image'] = jsonentry['thumb']
            if not isinstance(item['image'], str):
                item['image'] = None
            else:
                item['image'] = item['image'].replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['id'] = jsonentry['id']
            item['duration'] = jsonentry['seconds_duration']
            item['trailer'] = ''
            item['url'] = "https://tour.topwebmodels.com/scenes/" + jsonentry['slug']
            item['date'] = re.search(r'(\d{4}/\d{2}/\d{2})', jsonentry['publish_date']).group(1)
            item['date'] = self.parse_date(item['date'], date_formats=['%Y/%m/%d']).isoformat()
            item['site'] = match_site(jsonentry['site'])
            item['network'] = 'TopWebModels'
            item['parent'] = 'TopWebModels'

            item['performers'] = []
            for model in jsonentry['models']:
                if " and " in model.lower():
                    modellist = model.split(" and ")
                    if modellist:
                        for model in modellist:
                            item['performers'].append(model.title())
                if " & " in model.lower():
                    modellist = model.split(" & ")
                    if modellist:
                        for model in modellist:
                            item['performers'].append(model.title())
                if "\\u0026" in model.lower():
                    modellist = model.split("\\u0026")
                    if modellist:
                        for model in modellist:
                            item['performers'].append(model.title())
                else:
                    item['performers'].append(model)

            item['tags'] = []
            for tags in jsonentry['tags']:
                if "scott's picks" not in tags.lower():
                    item['tags'].append(string.capwords(tags))

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
