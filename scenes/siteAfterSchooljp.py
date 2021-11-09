import re
import string
import html
import dateparser
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

            title = scene.xpath('./div[@class="sample-title"]/text()').get()
            if title:
                title = title.strip()
                title = re.sub(r'^\d{1,2}\.', '', title)
                item['title'] = html.unescape(string.capwords(title.strip()))
            else:
                item['title'] = ''

            description = scene.xpath('./div[@class="sample-description"]/text()').get()
            if description:
                item['description'] = html.unescape(description.strip())
            else:
                item['description'] = ''

            performers = response.xpath('//div[@class="sample-girl center"]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: x.strip(), performers))
            else:
                item['performers'] = []

            tags = scene.xpath('./div[@class="sample-tags"]/a/text()').getall()
            if tags:
                item['tags'] = list(map(lambda x: x.strip().title(), tags))
            else:
                item['tags'] = []

            date = scene.xpath('./div[@class="sample-stats"]/text()').get()
            if date:
                date = re.search('released on (.*)', date.lower()).group(1)
                if date:
                    item['date'] = dateparser.parse(date, date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = []

            image = scene.xpath('./a[contains(@href,"/scenes/")][3]/@href').get()
            if image:
                item['image'] = image.strip()
            else:
                item['image'] = []

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

            yield item

    def get_site(self, response):
        return "After School.jp"
