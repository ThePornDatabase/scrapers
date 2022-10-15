import scrapy
from slugify import slugify
from scrapy.utils.project import get_project_settings
from tpdb.items import SceneItem
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteThaineeSpider(BaseSceneScraper):
    name = 'Thainee'
    network = 'Thainee'
    parent = 'Thainee'
    site = 'Thainee'

    start_urls = [
        'https://thainee.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php'
    }

    def start_requests(self):
        settings = get_project_settings()

        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

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

        link = "https://thainee.com/index.php"
        yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="showgirls"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('.//span[@class="pink"]/following-sibling::text()').get())
            item['description'] = scene.xpath('.//div[@class="agogodetails"]/p/text()').get().strip()
            scenedate = scene.xpath('.//span[@class="green"]/following-sibling::text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%b %d, %Y']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            item['performers'] = ['Thainee']
            item['tags'] = ['Asian']
            image = scene.xpath('.//div[@class="smallthumb clear"]/div[@class="thumb"][1]/div[@class="modelthumb"]//img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            item['id'] = slugify(item['title'])
            item['trailer'] = ""
            item['url'] = response.url
            item['network'] = "Thainee"
            item['parent'] = "Thainee"
            item['site'] = "Thainee"

            if item['id'] and item['title']:
                yield self.check_item(item, self.days)
