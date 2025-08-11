import string
import scrapy
import json
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
true = True
false = False


class SitePornboxSpider(BaseSceneScraper):
    name = 'Pornbox'
    network = 'Legal Porno'

    start_urls = [
        'https://pornbox.com',
    ]

    headers = {
        'X-Requested-With': 'XMLHttpRequest',
    }

    cookies = [
        {"name": "agree18", "value": "1"},
        {"name": "version_website_id", "value": "j:[25,1013,1401,1402]"},
    ]

    selector_map = {
        'title': "//h1[@class='watchpage-title']//text()",
        'description': '//div[@class="scene-description__row" and contains(., "Description")]//following-sibling::dd/text()',
        'date': "//span[@class='scene-description__detail']//a[1]/text()",
        'performers': "//h1[@class='watchpage-title']/a[contains(@href, '/model/')]/text()|//div[@class='scene-description__row']//dd//a[contains(@href, '/model/') and not(contains(@href, 'forum'))]/text()",
        'tags': "//div[@class='scene-description__row']//dd//a[contains(@href, '/niche/')]/text()",
        'duration': "//i[@class='fa fa-clock-o']/following-sibling::text()",
        'external_id': '\\/watch\\/(\\d+)',
        'trailer': '',
        'pagination': '/store/new-scenes/%s'
        # ~ 'pagination': '/niche/234/?skip=%s&sort=latest&_=1731108446109'
        # ~ 'pagination': '/studio/1275/?skip=%s&sort=recent&_=1688689939'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        if self.limit_pages == 1:
            self.limit_pages = 100

        countries = requests.get("https://pornbox.com/model/country", verify=False).content
        meta['countries'] = json.loads(countries)
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['contents']
        for scene in jsondata:
            url = f"https://pornbox.com/contents/{scene['id']}"
            yield scrapy.Request(url, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        scene = response.json()
        item = SceneItem()
        item['title'] = string.capwords(scene['scene_name'])
        if scene['small_description']:
            item['description'] = scene['small_description']
        else:
            item['description'] = ""
        item['site'] = scene['studio']
        if item['site'].lower().replace(" ", "") == "familysinners":
            item['site'] = "FAMILY Sinners (Pornbox)"
        item['date'] = self.parse_date(scene['publish_date']).strftime('%Y-%m-%d')
        item['image'] = scene['player_poster']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        # ~ item['image_blob'] = ""
        item['performers'] = []
        item['performers_data'] = []
        for model in scene['models']:
            item['performers'].append(string.capwords(model['model_name']))
            performer_extra = {}
            performer_extra['name'] = string.capwords(model['model_name'])
            performer_extra['site'] = "Legal Porno"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = string.capwords(model['sex'])
            for country in meta['countries']:
                if model['country_id'] == country['country_id']:
                    performer_extra['extra']['nationality'] = string.capwords(country['nationality'])
                    performer_extra['extra']['birthplace'] = string.capwords(country['name'])
                    performer_extra['extra']['birthplace_code'] = country['code']
            item['performers_data'].append(performer_extra)

        if scene['male_models']:
            for model in scene['male_models']:
                item['performers'].append(string.capwords(model['model_name']))
                performer_extra = {}
                performer_extra['name'] = string.capwords(model['model_name'])
                performer_extra['site'] = "Legal Porno"
                performer_extra['extra'] = {}
                performer_extra['extra']['gender'] = string.capwords(model['sex'])
                for country in meta['countries']:
                    if model['country_id'] == country['country_id']:
                        performer_extra['extra']['nationality'] = string.capwords(country['nationality'])
                        performer_extra['extra']['birthplace'] = string.capwords(country['name'])
                        performer_extra['extra']['birthplace_code'] = country['code']
                item['performers_data'].append(performer_extra)

        item['tags'] = []
        if scene['niches']:
            for tag in scene['niches']:
                item['tags'].append(string.capwords(tag['alias']))
        item['id'] = scene['id']
        item['duration'] = self.duration_to_seconds(scene['runtime'])
        if 'video_preview' in scene:
            item['trailer'] = scene['video_preview']
        else:
            item['trailer'] = ""
        item['url'] = f"https://pornbox.com/application/watch-page/{scene['id']}"
        item['network'] = item['site']
        item['parent'] = item['site']

        matches = ['bangbros', 'jeffsmodels', 'private', 'exposedlatinas', 'antoniosuleiman', 'bradmontana', 'richardmannsworld', 'only3xnetwork', 'privateblack', 'pornforce', 'immorallive', 'girlfriendsfilms',
                   'hentaied', 'vipissy', 'justanal', 'hussiepass', 'filthykings', 'puffynetwork', 'fit18', 'cuckhunter', 'bruceandmorgan', 'privateclassics', 'seehimfuck', 'filthyfamily', 'ukpornparty', 'jayspov', 'joibabes',
                   'only3xgirls', 'parasited', 'hazeher', 'collegerules', 'abuseme', 'only3xvr', 'justpov', 'girlsgonewild', 'plumperpassstudio', 'only3xlost', 'onlygolddigger', 'wetandpuffy', 'mypervyfamily', 'mykebrazil', 'mylifeinmiami',
                   'claudiamarie', 'rawwhitemeat', 'industryinvaders', 'cockyboys', 'touchmywife', 'blackbullchallenge', 'topwebmodels', 'realsexpass', 'riggsfilms', 'pervfect', 'mollyredwolf', 'bluepillmen', 'blacksonmoms', 'peter\'skingdom',
                   'pornmuschimovie', 'chickpass', 'grooby', 'pornpros', 'lubed', 'povd', 'facials4k', 'girlcum', 'exotic4k', 'nannyspy', 'castingcouchx', 'mom4k', 'bluebirdfilms', 'dreamtranny', 'pornworld', 'randyblue', 'plantsvscunts',
                   'mugurporn', 'bradmontanastudio', 'interracialvision', 'melinamay', 'primalfetish', 'sexmex', 'gotfilled', 'alexlegend', 'aglaeaproductions', 'mrlucky', 'mrluckypov', 'povmasters', 'dripdrop', 'dripdropprod', 'artemixxx', 'theartemixxx']
        if not any(x in item['site'].lower().replace(" ", "").replace("-", "").replace("_", "") for x in matches):
            yield self.check_item(item, self.days)
