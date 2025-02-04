import re
from requests import get
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBelamiSpider(BaseSceneScraper):
    name = 'Belami'
    site = 'Belami'
    parent = 'Belami'
    network = 'Belami'

    start_urls = [
        'https://newtour.belamionline.com/latestsexscenes.aspx',
        'https://newtour.belamionline.com/latestsolos.aspx'
    ]

    selector_map = {
        'title': '//span[contains(@id, "LabelTitle")]/text()',
        'description': '//div[@class="left"]/div[@class="bottom"]/p[2]/text()',
        'date': '//span[contains(@id, "LabelReleased")]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@name="og:image" and not(contains(@content, "svg"))]/@content',
        'performers': '//div[@class="actors_list"]/div/a/h3/text()',
        'tags': '//div[@class="tags"]/div/span/a/text()',
        'duration': '',
        'trailer': '',
        'type': 'Scene',
        'external_id': r'.*=(\d+)',
        'pagination': '',
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="content"]')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = self.cleanup_title(scene.xpath('.//span[@class="label"]/text()').get())
            if "solo" in response.url:
                item['title'] = "Solo: " + item['title']
                item['tags'] = ['Solo']
            item['description'] = self.cleanup_title(scene.xpath('.//video/@alt').get())
            item['description'] = re.sub(r'<[^<]+?>', '', item['description'])
            item['date'] = self.parse_date(scene.xpath('.//div[@class="date"]/text()').get(), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            item['image'] = scene.xpath('.//video/@poster').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['site'] = 'Belami'
            item['parent'] = 'Belami'
            item['network'] = 'Belami'

            item['url'] = self.format_link(response, scene.xpath('./div[1]/div[1]/a/@href').get())
            item['id'] = re.search(r'.*=(\d+)', item['url']).group(1)

            yield item
