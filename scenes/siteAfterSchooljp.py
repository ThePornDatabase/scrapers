import re
from datetime import date, timedelta
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAfterSchooljpSpider(BaseSceneScraper):
    name = 'AfterSchooljp'
    network = 'Digital J Media'
    parent = 'After School.jp'

    start_urls = [
        'https://www.afterschool.jp'
    ]

    selector_map = {
        'title': '//div[contains(@class,"module-video-details")]//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': "//meta[@itemprop='uploadDate']/@content",
        'image': '//meta[@itemprop="thumbnailUrl"]/@content',
        'performers': '//div[@class="actors"]/h2/span/a/strong/text()',
        'tags': "//a[contains(@href,'/tags/') or contains(@href,'/categories/')]/text()",
        'external_id': '\\/watch\\/(.*)\\/',
        'trailer': '//meta[@itemprop="contentURL"]/@content',
        'pagination': '/videos.en.html?order=-recent&page=%s'
    }

    def start_requests(self):
        url = "https://www.afterschool.jp/en/samples"
        yield scrapy.Request(url, callback=self.get_scenes,
                             meta={'page': self.page},
                             headers=self.headers,
                             cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="setscene-row"][1]/div[@class="setscene-info"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_set_scenes)

    def parse_set_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"sample-scene")]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./div[@class="sample-title"]/text()')
            if title:
                item['title'] = self.cleanup_title(re.sub(r'^\d{1,2}\.', '', title.get()))
            else:
                item['title'] = ''

            description = scene.xpath('./div[@class="sample-description"]/text()')
            if description:
                item['description'] = self.cleanup_description(description.get())
            else:
                item['description'] = ''

            performers = response.xpath('//div[@class="sample-girl center"]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                item['performers'] = []

            tags = scene.xpath('./div[@class="sample-tags"]/a/text()').getall()
            if tags:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))
            else:
                item['tags'] = []

            scenedate = scene.xpath('./div[@class="sample-stats"]/text()').get()
            if scenedate:
                scenedate = re.search('released on (.*)', scenedate.lower())
                if scenedate:
                    item['date'] = self.parse_date(scenedate.group(1), date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = self.parse('today').isoformat()

            image = scene.xpath('./a[contains(@href,"/scenes/")][3]/@href').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = []

            item['image_blob'] = ''

            if item['image']:
                extern_id = re.search(r'\.jp/.*?/(.*?)/', item['image']).group(1)
                if extern_id:
                    item['id'] = extern_id.strip()

            trailer = response.xpath('//video/source/@src').get()
            if trailer:
                item['trailer'] = trailer.strip()
            else:
                item['trailer'] = ''

            item['site'] = "After School.jp"
            item['parent'] = "After School.jp"
            item['network'] = "Digital J Media"

            item['url'] = response.url

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

    def get_site(self, response):
        return "After School.jp"
