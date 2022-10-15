import re
import scrapy
from scrapy.utils.project import get_project_settings
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteDeepInSexSpider(BaseSceneScraper):
    name = 'DeepInSex'
    network = 'Deep In Sex'
    parent = 'Deep In Sex'
    site = 'Deep In Sex'

    start_url = 'https://www.deepinsex.com'

    paginations = [
        '/3d-videos/',
        '/2d-videos/'
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': ''
    }

    def start_requests(self):
        settings = get_project_settings()

        meta = {}
        meta['page'] = self.page
        if 'USE_PROXY' in settings.attributes.keys():
            use_proxy = settings.get('USE_PROXY')
        else:
            use_proxy = None

        if use_proxy:
            print(f"Using Settings Defined Proxy: True ({settings.get('PROXY_ADDRESS')})")
        else:
            try:
                if self.proxy_address:
                    meta['proxy'] = self.proxy_address
                    print(f"Using Scraper Defined Proxy: True ({meta['proxy']})")
            except Exception:
                print("Using Proxy: False")

        for link in self.paginations:
            url = self.start_url + link
            yield scrapy.Request(url, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="card video"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = scene.xpath('.//h3/text()').get()
            item['description'] = ''
            item['date'] = self.parse_date('today').isoformat()
            item['image'] = self.format_link(response, scene.xpath('.//img/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = scene.xpath('.//div[@class="pornstars"]/a/span/text()').getall()
            if "3d" in response.url:
                item['tags'] = ['VR']
            else:
                item['tags'] = []
            item['trailer'] = ''
            item['url'] = self.format_link(response, scene.xpath('./a/@href').get())
            item['id'] = re.search(r'/(\d+)$', item['url']).group(1)
            item['site'] = "Deep In Sex"
            item['parent'] = "Deep In Sex"
            item['network'] = "Deep In Sex"

            yield item
