import re
from slugify import slugify
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteStraponHellSpider(BaseSceneScraper):
    name = 'StraponHell'

    start_urls = [
        'http://strapon-hell.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/last_update_sample.php?sta=%s&page=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        pagination = self.get_selector_map('pagination')
        start = str((int(page) - 1) * 20)
        return self.format_url(base, pagination % (start, page))

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(text(), "Clips:")]/../..')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('.//strong/text()')
            item['title'] = None
            if title:
                title = title.get()
                item['title'] = self.cleanup_title(title)
                item['performers'] = [self.cleanup_title(title)]

            if item['title']:
                performer = self.cleanup_title(scene.xpath('.//strong/text()').get())
                item['performers'] = [performer.replace("Mistress ", "")]

                scenedate = scene.xpath('.//text()[contains(., "Updated:")]')
                item['date'] = ''
                if scenedate:
                    scenedate = scenedate.get()
                    scenedate = re.search(r'(\d+ \w+ \d{4})', scenedate)
                    if scenedate:
                        item['date'] = self.parse_date(scenedate.group(1), date_formats=['%d %B %Y']).strftime('%Y-%m-%d')
                item['description'] = self.cleanup_description(scene.xpath('.//div[contains(text(), "Clips:")]/text()').get()).replace("Clips: ", "")
                image = scene.xpath('.//img/@src')
                if image:
                    item['image'] = image.get()
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                else:
                    item['image'] = ''
                    item['image_blob'] = ''
                item['id'] = slugify(re.sub('[^a-z0-9- ]', '', item['title'].lower().strip())) + item['date']
                item['trailer'] = ''
                item['tags'] = ['Strapon', 'Anal', 'Pegging', 'FemDom']
                item['url'] = "https://strapon-hell.com/" + item['id']
                item['site'] = "Strapon Hell"
                item['parent'] = "Strapon Hell"
                item['network'] = "Kennard Limited"

                yield self.check_item(item, self.days)
