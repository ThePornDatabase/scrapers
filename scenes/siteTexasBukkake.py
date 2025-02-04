import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTexasBukkakeSpider(BaseSceneScraper):
    name = 'TexasBukkake'
    network = 'Texas Bukkake'

    start_urls = [
        'https://api.fundorado.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"title")]/h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '',
        'image': '//div[contains(@class,"video-cover")]/@style',
        're_image': r'url\((.*\.(?:jpeg|png|jpg))',
        'performers': '//div[@class="flex flex-wrap-reverse"]/div/span/a/text()',
        'tags': '//div[contains(@class,"categories-icon")]/following-sibling::a/text()',
        'external_id': r'video/(\d+)?/',
        'trailer': '',
        'pagination': '/api/videos/browse/labels/622?page=%s&sg=false&sort=release&video_type=scene&lang=en&site_id=12'
    }

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        jsondata = jsondata['videos']['data']
        for scene in jsondata:
            if ("id" in scene and scene['id']) and ("slug" in scene and scene['slug']):
                link = f"https://api.fundorado.com/api/videodetail/{str(scene['id'])}?s=12"
                yield scrapy.Request(link, callback=self.parse_scene, meta=meta, dont_filter=True)

    def parse_scene(self, response):
        scene = response.json()
        item = self.init_scene()
        if "video" in scene and scene["video"]:
            scene = scene['video']
            item['title'] = self.cleanup_title(scene['title']['en'])

            item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['publication_date']).group(1)

            if item['date'] > '2022-04-01':
                if "description" in scene and scene['description']['en']:
                    item['description'] = self.cleanup_description(scene['description']['en'])
                else:
                    item['description'] = ""

                item['image'] = scene['artwork']['large']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['trailer'] = scene['preview']['url']
                item['id'] = scene['id']

                item['url'] = f"https://texasbukkake.com/video/{item['id']}/{scene['slug']}"

                if "tags" in scene['meta'] and scene['meta']['tags']:
                    item['tags'] = scene['meta']['tags']

                item['duration'] = self.duration_to_seconds(scene['meta']['duration'])

                item['site'] = "Texas Bukkake"
                item['parent'] = "Texas Bukkake"
                item['network'] = "Fundorado"
                item['performers'] = []
                for model in scene['actors']:
                    item['performers'].append(model['name'])

                yield self.check_item(item, self.days)
