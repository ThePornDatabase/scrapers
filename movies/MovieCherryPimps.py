import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MovieCherryPimpsSpider(BaseSceneScraper):
    name = 'MovieCherryPimps'
    network = 'Cherry Pimps'
    parent = 'NSFW Films'
    site = 'NSFW Films'

    start_urls = [
        'https://cherrypimps.com',
    ]

    selector_map = {
        'title': '//div[contains(@class, "update-info")]/h1/text()',
        'description': '',
        'date': '//div[contains(@class, "update-info")]//strong[contains(text(), "Release")]/following-sibling::text()',
        'image': '//img[contains(@class, "dvd_cover")]/@src',
        'performers': '//div[contains(@class, "update-info")]//strong[contains(text(), "Cast")]/following-sibling::a/text()',
        'tags': '//div[contains(@class, "update-info")]//ul[@class="tags"]/li/a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/dvds/dvds_page_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item-title"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        item = SceneItem()
        scenelist = response.xpath('//div[contains(@class, "item-video")]')
        item['id'] = self.get_id(response)
        item['site'] = self.site
        item['title'] = self.get_title(response)
        item['date'] = self.get_date(response)
        item['url'] = self.get_url(response)

        submitmovie = self.check_movie_cache(item['id'], item['site'], item['title'], item['date'], item['url'], None)

        if len(scenelist) > 1 and submitmovie:
            item['description'] = self.get_description(response)
            item['image'] = self.get_image(response)
            item['image_blob'] = self.get_image_blob(response)
            if "?" in item['image'] and ("token" in item['image'].lower() or "expire" in item['image'].lower()):
                item['image'] = re.search(r'(.*?)\?', item['image']).group(1)
            item['performers'] = self.get_performers(response)
            item['tags'] = self.get_tags(response)
            item['markers'] = self.get_markers(response)
            item['merge_id'] = self.get_merge_id(response)
            item['trailer'] = self.get_trailer(response)
            item['duration'] = self.get_duration(response)
            item['network'] = self.network
            item['parent'] = self.parent

            item['scenes'] = []
            for scene in scenelist:
                sceneid = scene.xpath('.//div[contains(@class, "item-title")]/a/@href').get()
                sceneid = re.search(r'.*/(.*?)\.htm', sceneid).group(1)

                sitename = scene.xpath('.//div[@class="item-sitename"]/a/text()').get()

                item['scenes'].append({'site': sitename, 'external_id': sceneid})

            back_image = response.xpath('//div[contains(@class, "card-back")]//img/@src')
            if back_image:
                item['back'] = self.format_link(response, back_image.get())
                item['back_blob'] = item['back']
            else:
                item['back'] = None
                item['back_blob'] = None

            item['type'] = 'Movie'

            yield self.check_item(item, self.days)
