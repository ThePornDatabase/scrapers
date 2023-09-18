import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteJawbreakerzSpider(BaseSceneScraper):
    name = 'Jawbreakerz'

    start_urls = [
        'https://www.jawbreakerz.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/videos/%s.php',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update-box"]')
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_text(scene.xpath('./div/h3/text()').get())
            scenedate = scene.xpath('.//span[contains(text(), "Date:")]/text()').get()
            scenedate = re.search(r'(\w+ \d{1,2}, \d{4})', scenedate).group(1)
            item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).isoformat()
            item['description'] = scene.xpath('./div/p/text()').get()
            performers = scene.xpath('./div/div/a[contains(@href, "/models/")]/text()').getall()
            item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers))
            item['trailer'] = ''
            item['tags'] = ['BBC', 'Big Dick', 'Interracial']
            image = scene.xpath('./div/a/img/@src').get()
            item['image'] = self.format_link(response, image).replace(" ", "%20")
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            duration = scene.xpath('.//span[contains(text(), "Video")]/text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'(\d{1,2}:\d{1,2})', duration)
                if duration:
                    duration = duration.group(1)
                    item['duration'] = self.duration_to_seconds(duration)

            item['url'] = self.format_link(response, scene.xpath('./div[contains(@class, "update-thumb")]/a/@href').get())
            if "?" in item['url']:
                item['url'] = re.search(r'(.*?)\?', item['url']).group(1)
            sceneid = re.search(r'videos/(.*?)\.htm', item['url'])
            if sceneid:
                item['id'] = sceneid.group(1)

            item['site'] = 'Jawbreakerz'
            item['parent'] = 'Jawbreakerz'
            item['network'] = 'Jawbreakerz'

            yield self.check_item(item, self.days)
