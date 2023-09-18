import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSheReactsSpider(BaseSceneScraper):
    name = 'SheReacts'
    network = 'TugPass'
    parent = 'She Reacts'
    site = 'She Reacts'

    start_urls = [
        'https://www.shereacts.com',
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
        'pagination': '/videos/%s.php',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update-box"]')
        for scene in scenes:
            item = SceneItem()
            item['title'] = scene.xpath('.//h3/text()').get()
            item['description'] = scene.xpath('./div[@class="update-detail"]/p/text()').get()
            scenedate = scene.xpath('.//span[contains(text(), "Date")]/text()')
            item['date'] = None
            if scenedate:
                scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate.get()).group(1)
                item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).isoformat()
            duration = scene.xpath('.//span[contains(text(), "Video")]/text()')
            item['duration'] = None
            if duration:
                duration = re.search(r'(\d{2}\:\d{2})', duration.get())
                if duration:
                    duration = duration.group(1)
                    item['duration'] = self.duration_to_seconds(duration)
            item['image'] = scene.xpath('.//img/@src').get()
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['tags'] = ['Reaction Video']
            item['performers'] = []
            item['trailer'] = None
            item['site'] = "She Reacts"
            item['parent'] = "She Reacts"
            item['network'] = "TugPass"
            url = scene.xpath('./div[1]/a/@href').get()
            if "?nats" in url:
                url = re.search(r'(.*?)\?nats', url).group(1)
            item['url'] = self.format_link(response, url)
            item['id'] = re.search(r'videos/(.*?)\.htm', item['url']).group(1)

            yield self.check_item(item, self.days)
