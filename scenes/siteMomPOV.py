# Historical scraper only.  No new scenes, pulling from Archive.org
import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
import scrapy


class Spider(BaseSceneScraper):
    name = 'MomPov'
    network = 'MomPov'
    parent = 'MomPov'
    site = 'MomPov'

    custom_settings = {'DOWNLOADER_MIDDLEWARES': {'scrapy_wayback_machine.WaybackMachineMiddleware': 5}}

    start_urls = [
        'https://www.mompov.com',
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
        'pagination': '/tour/page/%s/'
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse, meta={'page': meta['page']})

    def get_scenes(self, response):
        print(F"Using Wayback URL: {response.meta['wayback_machine_url']}")
        scenes = response.xpath('//div[contains(@class,"entry") and contains(@id, "post")]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene.xpath('.//a[@class="title"]/text()').get())
            description = scene.xpath('.//div[contains(@class,"entry_content")]/p//text()').getall()
            description = " ".join(description).strip().replace("  ", " ")
            item['description'] = description
            item['description'] = item['description'].replace("\\n-", "")
            scenemonth = scene.xpath('.//span[@class="month"]/text()').get()
            sceneday = scene.xpath('.//span[@class="day"]/text()').get()
            sceneyear = scene.xpath('.//span[@class="year"]/text()').get()
            if scenemonth and sceneday and sceneyear:
                item['date'] = self.parse_date(f'{sceneyear}-{scenemonth}-{sceneday}').isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()
            imagepath = re.search(r'(.*id_/)', response.meta['wayback_machine_url']).group(1)
            imagepath = imagepath.replace("id_", "im_")
            imagelink = scene.xpath('./a/img/@src')
            if not imagelink:
                imagelink = scene.xpath('.//div[@class="entry_content"]/p/img/@src')

            if imagelink:
                image = imagepath + imagelink.get()
                item['image_blob'] = self.get_image_blob_from_link(image)
                if re.search(r'src=(.*?\.jpg)', image):
                    item['image'] = re.search(r'src=(.*?\.jpg)', image).group(1)
                else:
                    item['image'] = image
            else:
                item['image'] = ''
                item['image_blob'] = ''
            item['performers'] = []
            item['tags'] = ['Amateur']
            item['trailer'] = ''
            item['url'] = scene.xpath('./a/@href|.//div[@class="title_holder"]/h1/a/@href').get()
            try:
                item['id'] = re.search(r'.*/(.*?)/', item['url']).group(1)
            except Exception:
                print(f"Item URL: {item['url']}")
                print(f"Scene Xpath: {scene.xpath('.//*').getall()}")
                print(f"Item Loaded: {item}")
                item['id'] = None
            item['network'] = "MomPov"
            item['parent'] = "MomPov"
            item['site'] = "MomPov"
            if item['id']:
                yield item

    def format_url(self, base, path):
        return 'https://www.mompov.com' + path

    def get_next_page_url(self, base, page):
        if page == 1:
            return base + "/tour"
        pageurl = self.format_url(base, self.get_selector_map('pagination') % page)
        return pageurl
