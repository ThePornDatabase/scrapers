import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteRestrainedEleganceSpider(BaseSceneScraper):
    name = 'RestrainedElegance'
    network = 'Restrained Elegance'
    parent = 'Restrained Elegance'
    site = 'Restrained Elegance'

    start_urls = [
        'https://www.restrainedelegance.com',
    ]

    selector_map = {
        'title': './/h1/text()',
        'description': './/h1/following-sibling::p[not(contains(text(), "ags:"))]/text()',
        'date': './/h3[contains(text(), "Added")]/text()',
        're_date': r'(\d{2}-\d{2}-\d{4})',
        'date_formats': ['%d-%m-%Y'],
        'image': '',
        'performers': './/h1/following-sibling::a/text()',
        'tags': '',
        'duration': './/h1/following-sibling::text()[contains(., "video")]',
        're_duration': r'((?:\d{1,2}\:)?\d{2}\:\d{2})',
        'trailer': '',
        'external_id': r'',
        'pagination': '/whatsnew.php?p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "boxrephoto") and contains(.//h1/following-sibling::text(), "video")]|//div[contains(@class, "boxrephoto") and contains(.//h2/following-sibling::text(), "video")]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = super().get_title(scene)
            item['description'] = super().get_description(scene)
            item['date'] = super().get_date(scene)
            tags = scene.xpath('.//h1/following-sibling::p[contains(text(), "ags:")]/text()')
            if tags:
                tags = tags.get()
                tags = tags.lower()
                tags = tags.replace("tags:", "").split(",")
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))
            item['duration'] = super().get_duration(scene)
            item['performers'] = super().get_performers(scene)
            item['site'] = "Restrained Elegance"
            item['parent'] = "Restrained Elegance"
            item['network'] = "Restrained Elegance"
            item['url'] = response.url
            item['trailer'] = ""

            image = scene.xpath('.//td[contains(@valign, "top")]/a/img/@src')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""

            if image:
                if re.search(r'/(.*?\d+)_', image):
                    item['id'] = re.search(r'.*/(.*?\d+)_', image).group(1)
                else:
                    item['id'] = re.search(r'.*/(.*?)\..*?$', image).group(1)
            else:
                item['id'] = None

            if item['id']:
                yield self.check_item(item, self.days)
