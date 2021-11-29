import re
from urllib.parse import urlparse
from datetime import date, timedelta
import string
import tldextract
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'ukpornparty': "UK Porn Party",
        'splatbukkake': "Splat Bukkake",
        'sexyukpornstars': "Sexy UK Pornstars",
        'realasianexposed': "Real Asian Exposed",
    }
    return match.get(argument, argument)


class NetworkUKXXXPassSpider(BaseSceneScraper):
    name = 'UKXXXPass'
    network = 'UK XXX Pass'

    start_urls = [
        'https://ukpornparty.xxx',
        'https://sexyukpornstars.xxx',
        'https://splatbukkake.xxx',
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
        scenes = response.xpath('//div[@class="model"]/div/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def parse_scene(self, response):
        scenes = response.xpath('//div[@class="update_block"]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('.//span[contains(@class,"title")]/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())
            else:
                item['title'] = ''

            scenedate = scene.xpath('.//span[contains(@class,"update_date")]/text()').get()
            if date:
                item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).isoformat()
            else:
                item['date'] = ''

            description = scene.xpath('.//span[contains(@class,"update_description")]/text()')
            if description:
                item['description'] = self.cleanup_description(description.get())
            else:
                item['description'] = ''

            performers = scene.xpath('.//span[contains(@class,"update_models")]/a/text()').getall()
            if performers:
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            else:
                item['performers'] = []

            tags = scene.xpath('.//span[contains(@class,"update_tags")]/a/text()').getall()
            if tags:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))
            else:
                item['tags'] = []

            image = scene.xpath('.//div[@class="update_image"]/a/img/@src0_4x').get()
            if not image:
                image = scene.xpath('.//div[@class="update_image"]/a/img/@src0_3x').get()
            if not image:
                image = scene.xpath('.//div[@class="update_image"]/a/img/@src0_2x').get()
            if not image:
                image = scene.xpath('.//div[@class="update_image"]/a/img/@src0_1x').get()
            if image:
                uri = urlparse(response.url)
                base = uri.scheme + "://" + uri.netloc
                item['image'] = base + image.strip().replace(" ", "").replace("\t", "")
            else:
                item['image'] = None

            item['image_blob'] = None

            trailer = scene.xpath('.//div[@class="update_image"]/a/@onclick').get()
            if trailer:
                trailer = re.search(r'tload\(\'(.*\.mp4|.*\.m4v)', trailer)
                if trailer:
                    trailer = trailer.group(1)
                    if "http" not in trailer:
                        uri = urlparse(response.url)
                        base = uri.scheme + "://" + uri.netloc
                    else:
                        base = ''
                    item['trailer'] = base + trailer.strip().replace(" ", "").replace("\t", "")
            else:
                item['trailer'] = ''

            if item['title']:
                externalid = re.sub(r'[^a-zA-Z0-9-]', '', item['title'])
                item['id'] = externalid.lower().strip().replace(" ", "-")

            item['url'] = response.url

            item['site'] = match_site(tldextract.extract(response.url).domain)
            item['parent'] = match_site(tldextract.extract(response.url).domain)
            item['network'] = "UK XXX Pass"

            if item['id'] and item['date']:
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

        next_page = response.xpath('//comment()[contains(.,"Next Page Link")]/following-sibling::a[1]/@href').get()
        if next_page:
            uri = urlparse(response.url)
            base = uri.scheme + "://" + uri.netloc
            next_page_url = base + "/" + next_page
            yield scrapy.Request(next_page_url, callback=self.parse_scene)
