import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteTeenPornStorageSpider(BaseSceneScraper):
    name = 'TeenPornStorage'
    network = 'Teen Porn Storage'
    parent = 'Teen Porn Storage'
    site = 'Teen Porn Storage'

    start_urls = [
        'https://teenpornstorage.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/videos_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//td[@class="bgr_030"]/table')
        for scene in scenes:
            item = SceneItem()
            image = scene.xpath('.//td[@class="bgr_032"]//td[@class="img_rated"]//img[contains(@src, "/cover")]/@src')
            if image:
                image = image.get()
                item['image'] = self.format_link(response, image)
                if "4v" in item['image']:
                    item['image'] = item['image'].replace('4v', '1v')
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'_(\d+)\.', image).group(1)
            item['title'] = self.cleanup_title(scene.xpath('.//a[contains(@class, "view_all none")]/text()').get())
            scenedate = scene.xpath('.//a[contains(@class, "view_all none")]/following-sibling::text()[contains(., "Added")]')
            if scenedate:
                scenedate = re.search(r'(\d{4}-\d{2}-\d{2})', scenedate.get()).group(1)
                item['date'] = scenedate
            duration = scene.xpath('.//a[contains(@class, "view_all none")]/following-sibling::text()[contains(., "min")]')
            if duration:
                duration = re.search(r'(\d{1,2}\:\d{2}) [mM]in', duration.get()).group(1)
                item['duration'] = self.duration_to_seconds(duration)
            item['description'] = ''
            item['trailer'] = ''
            item['performers'] = scene.xpath('.//a[contains(@href, "/model")]/text()').getall()
            item['tags'] = ['Teen']
            item['url'] = response.url
            item['site'] = 'Teen Porn Storage'
            item['parent'] = 'Teen Porn Storage'
            item['network'] = 'Teen Porn Storage'
            yield self.check_item(item, self.days)

    def get_next_page_url(self, base, page):
        if int(page) == 1:
            return 'https://teenpornstorage.com/videos.html'
        else:
            return self.format_url(base, self.get_selector_map('pagination') % page)
