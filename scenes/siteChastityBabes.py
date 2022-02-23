import re
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class ChastityBabesFullImportSpider(BaseSceneScraper):
    name = 'ChastityBabesFullUpdate'
    network = 'Chastity Babes'
    parent = 'Chastity Babes'

    custom_settings = {'CONCURRENT_REQUESTS': '1', }

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
        modelname = response.meta['name']
        scenes = response.xpath('//h2[@class="title"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=scene,
                                 callback=self.parse_scenes,
                                 meta={'name': modelname},
                                 headers=self.headers,
                                 cookies=self.cookies)

        nextpage = response.xpath('//div[@class="pagination"]/div/a/@href')
        if nextpage:
            nextpage = nextpage.get()
            nextpage = nextpage.strip()
            yield scrapy.Request(url=nextpage,
                                 callback=self.parse_model_scenes,
                                 meta={'name': modelname},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse_scenes(self, response):
        item = SceneItem()
        modelname = response.meta['name']
        item['performers'] = [modelname]
        title = response.xpath('//h1[@id="post-title"]/text()').get()
        if title:
            item['title'] = self.cleanup_title(title)

        description = response.xpath('//div[@class="postcontent"]//p/text()').get()
        if description:
            item['description'] = self.cleanup_description(description)

        item['site'] = "Chastity Babes"
        item['parent'] = "Chastity Babes"
        item['network'] = "Chastity Babes"

        postinfo = response.xpath('//div[@class="post_info"]/text()').get()
        if postinfo:
            postinfo = postinfo.replace("\r\n", " ")
            postinfo = postinfo.replace("\n", " ")
            scenedate = re.search(r'Posted\s+on\s?(.*)\s?in', postinfo)
            if scenedate:
                scenedate = scenedate.group(1)
                scenedate = self.parse_date(scenedate.strip()).isoformat()
                item['date'] = scenedate

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
        else:
            item['image'] = None

        item['image_blob'] = None

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
