import re
import html
import string
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteAmericanPornstarSpider(BaseSceneScraper):
    name = 'AmericanPornstar'
    network = 'American Pornstar'
    parent = 'American Pornstar'

    start_urls = [
        'http://american-pornstar.com',
    ]

    selector_map = {
        'title': '//div[@class="title clear"]/h2/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates/(.*).html',
        'trailer': '',
        'pagination': '/models/models_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_details"]/a[1]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def parse_scene(self, response):
        scenes = response.xpath('//div[@class="update_block"]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('.//span[contains(@class,"title")]/text()').get()
            if title:
                item['title'] = html.unescape(string.capwords(title.strip()))
            else:
                item['title'] = ''

            date = scene.xpath('.//span[contains(@class,"update_date")]/text()').get()
            if date:
                item['date'] = dateparser.parse(date, date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = ''

            title = scene.xpath('.//span[contains(@class,"title")]/text()').get()
            if title:
                item['title'] = html.unescape(string.capwords(title.strip()))
            else:
                item['title'] = ''

            description = scene.xpath('.//span[contains(@class,"update_description")]/text()').get()
            if description:
                item['description'] = html.unescape(description.strip())
            else:
                item['description'] = ''

            performers = scene.xpath('.//span[contains(@class,"update_models")]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: x.strip().title(), performers))
            else:
                item['performers'] = []

            tags = scene.xpath('.//span[contains(@class,"update_tags")]/a/text()').getall()
            if tags:
                item['tags'] = list(map(lambda x: x.strip().title(), tags))
            else:
                item['tags'] = []

            image = scene.xpath('.//div[@class="update_image"]/a/img/@src').get()
            if image:
                item['image'] = "http://american-pornstar.com/" + image.strip().replace(" ", "%20")
            else:
                item['image'] = []

            trailer = scene.xpath('.//div[@class="update_image"]/a/@onclick').get()
            if trailer:
                trailer = re.search(r'tload\(\'(.*\.mp4|.*\.m4v)', trailer)
                if trailer:
                    trailer = trailer.group(1)
                    item['trailer'] = "http://american-pornstar.com" + trailer.strip().replace(" ", "%20")
            else:
                item['trailer'] = ''

            if title:
                externalid = re.sub('[^a-zA-Z0-9-]', '', title)
                item['id'] = externalid.lower().strip().replace(" ", "-")

            item['url'] = response.url

            item['site'] = "American Pornstar"
            item['parent'] = "American Pornstar"
            item['network'] = "American Pornstar"

            if item['id'] and item['date']:
                yield item

        next_page = response.xpath('//comment()[contains(.,"Next Page Link")]/following-sibling::a[1]/@href').get()
        if next_page:
            next_page_url = "http://american-pornstar.com/" + next_page
            yield scrapy.Request(next_page_url, callback=self.parse_scene)
