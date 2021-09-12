import html
import re
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ChastityBabesFullImportSpider(BaseSceneScraper):
    name = 'ChastityBabesFullUpdate'
    network = 'Chastity Babes'
    parent = 'Chastity Babes'

    custom_settings = {
        'CONCURRENT_REQUESTS': '1',
        'ITEM_PIPELINES': {
            'tpdb.pipelines.TpdbApiScenePipeline': 400,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'tpdb.middlewares.TpdbSceneDownloaderMiddleware': 543,
        }
    }

    start_urls = [
        'https://www.chastitybabes.com/'
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

    def start_requests(self):

        yield scrapy.Request(url='https://www.chastitybabes.com/babes',
                             callback=self.parse_model_page,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def parse_model_page(self, response, **kwargs):
        models = response.xpath('//td[@align="center"]')
        for model in models:
            modelurl = model.xpath('./a/@href').get()
            modelname = model.xpath('./a/img/@alt').get()
            if modelurl and modelname:
                yield scrapy.Request(url=modelurl,
                                     callback=self.parse_model_scenes,
                                     meta={'name': modelname},
                                     headers=self.headers,
                                     cookies=self.cookies)

    def parse_model_scenes(self, response):
        name = response.meta['name']
        scenes = response.xpath('//h2[@class="title"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene,
                                 callback=self.parse_scenes,
                                 meta={'name': name},
                                 headers=self.headers,
                                 cookies=self.cookies)

        nextpage = response.xpath('//div[@class="pagination"]/div/a/@href')
        if nextpage:
            nextpage = nextpage.get()
            nextpage = nextpage.strip()
            yield scrapy.Request(url=nextpage,
                                 callback=self.parse_model_scenes,
                                 meta={'name': name},
                                 headers=self.headers,
                                 cookies=self.cookies)

        return None

    def parse_scenes(self, response):
        item = SceneItem()
        name = response.meta['name']
        item['performers'] = [name]
        title = response.xpath('//h1[@id="post-title"]/text()').get()
        if title:
            item['title'] = title.strip().title()
            item['title'] = html.unescape(item['title'])

        description = response.xpath('//div[@class="postcontent"]//p/text()').get()
        if description:
            item['description'] = description.strip()
            item['description'] = html.unescape(item['description'])

        item['site'] = "Chastity Babes"
        item['parent'] = "Chastity Babes"
        item['network'] = "Chastity Babes"

        postinfo = response.xpath('//div[@class="post_info"]/text()').get()
        if postinfo:
            postinfo = postinfo.replace("\r\n", " ")
            postinfo = postinfo.replace("\n", " ")
            date = re.search(r'Posted\s+on\s?(.*)\s?in', postinfo)
            if date:
                date = date.group(1)
                date = dateparser.parse(date.strip()).isoformat()
                item['date'] = date

            externalid = re.search(r'Update\s?(.*)\ ?\|', postinfo)
            if externalid:
                externalid = externalid.group(1)
                externalid = re.sub(r'\s+', '', externalid)
                item['id'] = externalid
            else:
                item['id'] = ''
        else:
            item['id'] = ''

        image = response.xpath('//div[@class="postcontent"]/a[1]/img/@src').get()
        if image:
            item['image'] = image.strip()

        tags = response.xpath('//a[@rel="category tag"]/text()').getall()
        if tags:
            item['tags'] = list(map(lambda x: x.strip().title(), tags))
            if "Featured" in item['tags']:
                item['tags'].remove('Featured')
        else:
            item['tags'] = []

        item['url'] = response.url

        item['trailer'] = ''

        if item['id'] and item['title'] and item['date']:
            yield item

        return None
