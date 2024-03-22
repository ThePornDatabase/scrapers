import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteTSRawSpider(BaseSceneScraper):
    name = 'TSRaw'
    site = 'TSRaw'
    parent = 'TSRaw'
    network = 'TSRaw'

    start_urls = [
        'https://www.tsraw.com',
    ]

    selector_map = {
        'title': './/span[contains(@class, "video-title")]/text()',
        'description': './/p[contains(@class, "setTRT")]/text()',
        'date': './/span[contains(@class, "videoDate")]/text()',
        'image': '',
        'performers': '',
        'tags': './/span[contains(@class, "tags-style")]/following-sibling::a/text()',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        link = 'https://www.tsraw.com/index.php?section=1647'
        yield scrapy.Request(link, callback=self.get_scenes, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="videoThumb"]/..')
        for scene in scenes:
            item = SceneItem()
            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = self.get_date(scene)
            image = self.format_link(response, scene.xpath('.//img/@src').get())
            if "&width" in image:
                image = re.search(r'(.*?)\&width', image).group(1)
            if image:
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ''
                item['image_blob'] = ''

            item['performers'] = []
            performers = scene.xpath('.//span[contains(@class, "ts-video-desc")]/text()')
            if performers:
                performers = performers.get()
                performers = performers.split(",")
                if performers:
                    item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))

            item['tags'] = self.get_tags(scene)
            item['id'] = re.search(r'gal=(\d+)', item['image']).group(1)

            item['trailer'] = ""
            item['duration'] = ''
            duration = scene.xpath('.//span[contains(@class, "videoTRT")]/text()')
            if duration:
                duration = duration.getall()
                duration = "".join(duration)
                duration = re.sub('[^a-zA-Z0-9]', '', duration.lower())
                duration = re.search(r'(\d+)min', duration)
                if duration:
                    item['duration'] = str(int(duration.group(1)) * 60)

            item['url'] = f"https://www.tsraw.com/index.php?vid={item['id']}"
            item['network'] = self.network
            item['parent'] = self.parent
            item['site'] = self.site
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
