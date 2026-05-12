import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class OnlyGrandpaSpider(BaseSceneScraper):
    name = 'OnlyGrandpa'
    network = 'Only Grandpa'
    parent = 'Only Grandpa'
    site = 'Only Grandpa'
    start_urls = [
        'https://onlygrandpa.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/categories/movies_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "item item-video")]')
        for scene in scenes:
            item = self.init_scene()
            scenedate = scene.xpath('.//div[contains(@class, "date")]/text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = self.parse_date(scenedate).strftime('%Y-%m-%d')
                item['date'] = scenedate

            if self.check_item(item, self.days):

                title = scene.xpath('.//h3/a/text()')
                if title:
                    item['title'] = self.cleanup_title(title.get().strip())

                duration = scene.xpath('.//div[contains(@class, "duration")]/text()')
                if duration:
                    duration = duration.getall()
                    duration = "".join(duration).strip()
                    item['duration'] = self.duration_to_seconds(duration)

                performers = scene.xpath('.//div[contains(@class, "item-models")]/a/text()')
                if performers:
                    performers = performers.getall()
                    item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))

                sceneid = scene.xpath('.//div[contains(@class, "video-thumb")]/@data-videoid')
                if sceneid:
                    sceneid = sceneid.get()
                    item['id'] = sceneid.strip().lower()

                trailer = scene.xpath('.//div[contains(@class, "video-thumb")]/@data-videosrc')
                if trailer:
                    trailer = trailer.get()
                    item['trailer'] = self.format_link(response, trailer.strip())

                image = scene.xpath('.//img/@src0_webp_1x')
                if image:
                    item['image'] = self.format_link(response, image.get().strip())
                    item['image'] = item['image'].replace('-1x', '-3x')
                    item['image_blob'] = self.get_image_blob(item['image'])

                item['site'] = "OnlyGrandpa"
                item['parent'] = "OnlyGrandpa"
                item['network'] = "OnlyGrandpa"

                yield item            
