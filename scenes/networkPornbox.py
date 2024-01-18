import string
import scrapy
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
        # ~ 'pagination': '/studio/1275/?skip=%s&sort=recent&_=1688689939'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        if self.limit_pages == 1:
            self.limit_pages = 10
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['contents']
        for scene in jsondata:
            url = f"https://pornbox.com/contents/{scene['id']}"
            yield scrapy.Request(url, callback=self.parse_scene, headers=self.headers, cookies=self.cookies, meta=meta)

    def parse_scene(self, response):
        scene = response.json()
        item = SceneItem()
        item['title'] = string.capwords(scene['scene_name'])
        if scene['small_description']:
            item['description'] = scene['small_description']
        else:
            item['description'] = ""
        item['site'] = scene['studio']
        item['date'] = self.parse_date(scene['publish_date']).isoformat()
        item['image'] = scene['player_poster']
        item['image_blob'] = self.get_image_blob_from_link(item['image'])
        # ~ item['image_blob'] = ""
        item['performers'] = []
        for model in scene['models']:
            item['performers'].append(string.capwords(model['model_name']))
        if scene['male_models']:
            for model in scene['male_models']:
                item['performers'].append(string.capwords(model['model_name']))

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
        item['network'] = 'Legal Porno'
        item['parent'] = 'Legal Porno'

        matches = ['bangbros', 'jeffsmodels', 'private', 'antoniosuleiman', 'bradmontana', 'richardmannsworld', 'only3xnetwork', 'privateblack', 'pornforce', 'immorallive', 'girlfriendsfilms',
                   'hentaied', 'vipissy', 'justanal', 'hussiepass', 'filthykings', 'puffynetwork', 'fit18', 'cuckhunter', 'bruceandmorgan', 'privateclassics', 'seehimfuck', 'filthyfamily', 'ukpornparty', 'jayspov',
                   'only3xgirls', 'parasited', 'hazeher', 'collegerules', 'abuseme', 'only3xvr', 'justpov', 'girlsgonewild', 'plumperpassstudio', 'only3xlost', 'onlygolddigger', 'wetandpuffy', 'mypervyfamily', 'mykebrazil', 'mylifeinmiami',
                   'claudiamarie', 'rawwhitemeat', 'industryinvaders', 'cockyboys', 'touchmywife', 'blackbullchallenge', 'topwebmodels', 'realsexpass', 'riggsfilms', 'pervfect', 'mollyredwolf', 'bluepillmen', 'blacksonmoms', 'peter\'skingdom',
                   'pornmuschimovie', 'chickpass', 'grooby', 'pornpros', 'lubed', 'povd', 'facials4k', 'girlcum', 'exotic4k', 'nannyspy', 'castingcouch-x', 'mom4k', 'bluebirdfilms', 'dreamtranny', 'pornworld', 'randyblue']
        if not any(x in item['site'].lower().replace(" ", "") for x in matches):
            yield self.check_item(item, self.days)
