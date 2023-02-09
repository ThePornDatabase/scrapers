import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SmartMediaStarSpider(BaseSceneScraper):
    name = 'SmartMediaStar'
    network = 'Smart Media Star'
    parent = 'Smart Media Star'

    per_page = 15

    # Creates individual versions if multiple perspectives are found
    split_versions = True
    # Use perspective thumbnail instead of main thumbnail found on /videos page
    use_perspective_thumbnail = False
    # Always add (<perspective>) to video title regardless of whether perspective is main perspective
    always_label_perspective = False

    start_urls = [
        'https://realitylovers.com',
        'https://tsvirtuallovers.com'
    ]

    selector_map = {
        'description': '//p[@itemprop="description"]//text()',
        'performers': '//a[@itemprop="actor"]/text()',
        'tags': '//a[@itemprop="keyword"]/text()',
        're_scene_data': r'const sceneData = (\{[^;]+)\;',
        'external_id': r'\/vd\/([0-9]+)\/',
        'pagination': '',
        'type': 'Scene',
    }

    sites = {
        'realitylovers': "Reality Lovers",
        'tsvirtuallovers': "TS Virtual Lovers"
    }

    def start_requests(self):
        for link in self.start_urls:
            yield scrapy.Request(
                url=f"{link}/videos/search",
                callback=self.parse,
                method='POST',
                headers={'Content-Type': 'application/json', 'Referer': f"{link}/videos"},
                meta={'page': self.page},
                body=self.create_post_data(self.page, self.per_page)
            )

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield self.check_item(scene)

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=response.url,
                                     callback=self.parse,
                                     meta=meta,
                                     method="POST",
                                     body=self.create_post_data(meta['page'], self.per_page),
                                     headers={'Content-Type': 'application/json'},
                                     cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.json()['contents']
        for scene in scenes:
            meta['id'] = scene['id']
            meta['title'] = scene['title']
            meta['date'] = self.parse_date(scene['released']).isoformat()
            meta['image'] = self.get_main_image_from_srcset(scene['mainImageSrcset'])

            url = scene['videoUri']
            yield scrapy.Request(url=self.format_link(response, url), callback=self.parse_scene, meta=meta)

    def parse_scene(self, response, **kwargs):
        item = next(super().parse_scene(response, **kwargs))

        if self.split_versions:
            scenedata = self.get_scene_data(response)

            for scene in scenedata:
                localitem = item.copy()

                localitem['id'] = scene['id']

                if self.use_perspective_thumbnail:
                    localitem['image'] = self.get_main_image_from_srcset(scene['imgSrcSet'])

                localitem['duration'] = scene['durationSec']

                if not scene['main'] or self.always_label_perspective:
                    localitem['title'] += f" ({scene['perspective']})"

                yield localitem
        else:
            yield item

    def get_site(self, response):
        site = super().get_site(response)
        return self.sites[site]

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Virtual Reality" not in tags:
            tags.append("Virtual Reality")
        return tags

    def get_description(self, response):
        description = super().get_description(response)
        description = self.cleanup_description(description.replace(" … Read more", ""))
        return description

    def get_scene_data(self, response):
        script = response.xpath('//script[contains(text(),"const sceneData")]/text()').get()
        jsondata = self.get_from_regex(script, "re_scene_data")
        data = json.loads(jsondata.strip())

        perspectivedata = []
        for scene in data['povScenes']:
            scene['perspective'] = "POV"
            scene['main'] = scene['id'] == data['firstSceneId']
            perspectivedata.append(scene)

        for scene in data['voyeurScenes']:
            scene['perspective'] = "Voyeur"
            scene['main'] = scene['id'] == data['firstSceneId']
            perspectivedata.append(scene)

        return perspectivedata

    @staticmethod
    def create_post_data(page, per_page):
        return json.dumps({"searchQuery": "", "categoryId": None, "perspective": None, "actorId": None, "offset": (page-1) * per_page, "isInitialLoad": False, "sortBy": "NEWEST", "videoView": "MEDIUM", "device": "DESKTOP"})

    @staticmethod
    def get_main_image_from_srcset(srcset):
        images = dict(map(lambda image: (image.split(" ")[1], image.split(" ")[0]), srcset.split(",")))
        for size in ['2x', '1x']:
            if size in images:
                return images[size]

        return None
