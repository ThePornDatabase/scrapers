import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from scrapy import Selector


class SiteSugarcookieSpider(BaseSceneScraper):
    name = 'Sugarcookie'
    network = 'Sugarcookie'
    parent = 'Sugarcookie'
    site = 'Sugarcookie'

    start_urls = [
        'https://sugarcookie.xxx',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"][1]/@content',
        'description': '//meta[@property="og:description"][1]/@content',
        'date': '//meta[@property="article:published_time"][1]/@content',
        'image': '//meta[@property="og:image"][1]/@content',
        'performers': '',
        'tags': '//p[contains(@class,"cb-tags")]/a/text()',
        'external_id': r'',
        'trailer': '',
        'pagination': '/porn/page/%s/'
    }

    def start_requests(self):
        model_list = []
        for x in range(1, 50):
            link = 'https://sugarcookie.xxx/models/page/%s/' % x
            modelpage = requests.get(link)
            if modelpage:
                sel = Selector(text=modelpage.content)
                models = sel.xpath('//article//h2[@class="cb-post-title"]/a/text()')
                if models:
                    for model in models:
                        model_list.append(string.capwords(model.get()))
                else:
                    break
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page, 'model_list': model_list},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        # ~ scenes = response.xpath('//article/div[@class="cb-meta"]/h2/a/@href').getall()
        scenes = response.xpath('//article[contains(@id, "post")]')
        for scene in scenes:
            scene_id = scene.xpath('./@id')
            if scene_id:
                scene_id = re.search(r'-(\d+)', scene_id.get())
                if scene_id:
                    meta['id'] = scene_id.group(1)
            scene = scene.xpath('./div[@class="cb-meta"]/h2/a/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        models = response.meta['model_list']
        tags = []
        tag_list = super().get_tags(response)
        tag_list = list(map(lambda x: string.capwords(x.strip()), tag_list))
        for tag in tag_list:
            if tag not in models and "Dean Van Damme" not in tag and tag.replace(" Porn", "") not in models:
                tags.append(tag)
        return tags

    def get_performers(self, response):
        models = response.meta['model_list']
        performers = []
        tag_list = super().get_tags(response)
        tag_list = list(map(lambda x: string.capwords(x.strip()), tag_list))
        for tag in tag_list:
            if tag in models:
                performers.append(tag)
        return performers
