import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePornDudeCastingSpider(BaseSceneScraper):
    name = 'PornDudeCasting'
    network = 'Porn Dude Casting'
    parent = 'Porn Dude Casting'
    site = 'Porn Dude Casting'

    start_urls = [
        'https://porndudecasting.com',
    ]

    selector_map = {
        'external_id': r'.*/(\d+)/',
        'trailer': '',
        'pagination': '/latest-updates/%s/?sort_by=post_date&sort_by=post_date&sort_by=post_date'
    }


    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "content-block__item")]')
        for scene in scenes:
            item = self.init_scene()
            item['title'] = string.capwords(self.cleanup_title(scene.xpath('.//a[contains(@class, "info-name")]/span/text()').get().strip()))
            item['description'] = self.cleanup_description(scene.xpath('.//div[contains(@class, "info-descr")]/p/text()').get().strip())
            image = scene.xpath('.//div[contains(@class, "img-holder")]/img[contains(@src, "screenshots")]/@src').get()
            if not image:
                image = scene.xpath('.//div[contains(@class, "img-holder")]/img/@data-src').get()

            if image:
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
                item['id'] = re.search(r'screenshots/.*?/(\d+)/', image).group(1)

            sceneurl = scene.xpath('.//a[contains(@class, "card__holder")]/@href')
            if sceneurl:
                item['url'] = self.format_link(response, sceneurl.get().strip())

            performer = re.search(r'.*/(.*?)/$', item['url'].strip()).group(1).replace("-", " ")
            if performer:
                item['performers'] = [string.capwords(performer)]

            duration = scene.xpath('.//div[contains(@class, "video-time")]/text()')
            if duration:
                item['duration'] = self.duration_to_seconds(duration.get().strip())
            item['site'] = "PornDudeCasting"
            item['parent'] = "PornDudeCasting"
            item['network'] = "PornDudeCasting"
            item['tags'] = ['Casting']
            if item['id']:
                yield item


    # JSON version, left just in case it comes back
    # def get_scenes(self, response):
    #     scenes = response.xpath('//script[contains(@type, "json") and contains(text(), "VideoObject")]/text()').getall()
    #     for scene in scenes:
    #         print(scene)
    #         item = self.init_scene()

    #         scene = json.loads(scene)

    #         item['title'] = string.capwords(scene['name'])
    #         item['description'] = scene['description']
    #         image = scene['thumbnailUrl']
    #         if image:
    #             item['image'] = image
    #             item['image_blob'] = self.get_image_blob_from_link(image)

    #         item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['uploadDate']).group(1)
    #         item['duration'] = self.duration_to_seconds(scene['duration'])

    #         for tag in scene['genre']:
    #             if tag.lower().strip() not in ['porn', 'casting']:
    #                 item['tags'].append(string.capwords(tag))

    #         item['url'] = scene['potentialAction']['target']['urlTemplate']

    #         item['site'] = "PornDudeCasting"
    #         item['parent'] = "PornDudeCasting"
    #         item['network'] = "PornDudeCasting"

    #         urlname = item['url'].strip("/")
    #         urlname = re.search(r'.*/([a-z-]+)', urlname.lower()).group(1)
    #         urlname = urlname.replace("-", " ")
    #         if urlname in item['title'].lower():
    #             item['performers'].append(string.capwords(urlname))

    #         item['id'] = re.search(r'screenshots/.*?/(\d+)/', item['image']).group(1)

    #         yield item
