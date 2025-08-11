import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJerkOffGamesSpider(BaseSceneScraper):
    name = 'TheJerkOffGames'

    start_urls = [
        'https://www.thejerkoffmembers.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "videothumb")]')
        for scene in scenes:
            item = self.init_scene()
            item['url'] = scene.xpath('./a[1]/@href').get()
            item['id'] = re.search(r'.*/(.*?)\.htm', item['url']).group(1).lower()

            trailer = scene.xpath('.//source/@src')
            if trailer:
                item['trailer'] = self.format_link(response, trailer.get())

            image = scene.xpath('.//video/@poster')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            title = scene.xpath('./following-sibling::div[contains(@class, "updateDetails")][1]//h4/a/text()').get()
            item['title'] = self.cleanup_title(title.replace("\r", "").replace("\n", "").replace("\t", ""))

            item['performers'] = scene.xpath('./following-sibling::div[contains(@class, "updateDetails")][1]//p/span[contains(@class, "models")]/a/text()').getall()
            item['performers'] = list(map(lambda x: string.capwords(x.strip()), item['performers']))
            item['performers_data'] = self.get_performers_data(item['performers'])

            scenedate = scene.xpath('./following-sibling::div[contains(@class, "updateDetails")][1]//p/span[@class="availdate" and contains(text(), "/")]/text()').get()
            item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            item['network'] = 'The Jerk Off Games'
            item['parent'] = 'The Jerk Off Games'
            item['site'] = 'The Jerk Off Games'

            yield self.check_item(item, self.days)

    def get_performers_data(self, performers):
        performers_data = []
        for performer in performers:
            performer_extra = {}
            performer_extra['name'] = performer
            performer_extra['network'] = "The Jerk Off Games"
            performer_extra['site'] = "The Jerk Off Games"
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            performers_data.append(performer_extra)
        return performers_data
