import scrapy
import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class LegalPornoSpider(BaseSceneScraper):
    name = 'LegalPorno'
    network = 'Legal Porno'

    start_urls = [
        'https://www.analvids.com',
        # ~ 'https://pornworld.com'  # Located in networkLegalPornoPornworld.py
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]//text()',
        'description': '//div[contains(@class, "text-light") and contains(text(), "Description")]/following-sibling::div[1]/text()',
        'date': '//i[contains(@class, "calendar")]/text()',
        'image': '//video/@data-poster',
        # ~ 'performers': '//span[contains(@class, "featuring_models")]/a/text()',
        'performers': '//div[@class="container-fluid"]/h1//a[contains(@href, "/model/")]/text()',
        'tags': '//div[contains(@class, "genres-list")]/a[contains(@href, "genre/")]/text()',
        'duration': '//i[contains(@class, "clock")]/text()',
        'external_id': r'/watch/(\d+)',
        'trailer': '',
        'pagination': '/new-videos/%s'
    }

    def start_requests(self):
        meta = {}
        meta['page'] = self.page
        if self.limit_pages == 1:
            self.limit_pages = 10
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_site(self, response):
        return response.xpath('//span[contains(text(), "Studio")]/following-sibling::a/text()').get().strip()

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="card-scene"]/div[1]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene, callback=self.parse_scene, meta=meta)

    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title'))
        if title:
            title = " ".join(title.getall()).lower()
            titlesearch = re.search(r'(.*) featuring', title)
            if titlesearch:
                title = titlesearch.group(1).strip()
                return string.capwords(title.replace("  ", " ").replace(" ,", ",").strip())
            return string.capwords(title.replace("  ", " ").replace(" ,", ",").strip())
        return ''

    def parse_scene(self, response):
        item = SceneItem()
        item['title'] = self.get_title(response).replace("\r", "").replace("\n", "").replace("\t", "").strip()
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        if item['image']:
            item['image_blob'] = self.get_image_blob(response)
            item['image'] = re.search(r'(.*)\?', item['image']).group(1)
        else:
            item['image'] = ''
            item['image_blob'] = ''
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['markers'] = self.get_markers(response)
        item['id'] = self.get_id(response)
        item['duration'] = self.get_duration(response)
        item['trailer'] = self.get_trailer(response)
        item['url'] = self.get_url(response)
        item['network'] = self.get_network(response)
        item['parent'] = 'Legal Porno'

        matches = ['bangbros', 'jeffsmodels', 'private', 'antoniosuleiman', 'richardmannsworld', 'only3xnetwork', 'privateblack', 'pornforce', 'immorallive', 'girlfriendsfilms',
                   'hentaied', 'vipissy', 'justanal', 'hussiepass', 'filthykings', 'puffynetwork', 'fit18', 'cuckhunter', 'bruceandmorgan', 'privateclassics', 'seehimfuck', 'filthyfamily', 'ukpornparty', 'jayspov',
                   'only3xgirls', 'parasited', 'hazeher', 'collegerules', 'abuseme', 'only3xvr', 'justpov', 'girlsgonewild', 'plumperpassstudio', 'only3xlost', 'onlygolddigger', 'wetandpuffy', 'mypervyfamily', 'mykebrazil', 'mylifeinmiami',
                   'claudiamarie', 'rawwhitemeat', 'industryinvaders', 'cockyboys', 'touchmywife', 'blackbullchallenge', 'topwebmodels', 'realsexpass', 'riggsfilms', 'pervfect', 'mollyredwolf', 'bluepillmen', 'blacksonmoms', 'peter\'skingdom',
                   'pornmuschimovie', 'chickpass', 'grooby', 'pornpros', 'lubed', 'povd', 'facials4k', 'girlcum', 'exotic4k', 'nannyspy', 'castingcouch-x', 'mom4k', 'bluebirdfilms', 'dreamtranny', 'pornworld', 'randyblue']
        if not any(x in item['site'].lower().replace(" ", "") for x in matches):
            yield self.check_item(item, self.days)
