import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteGotCuffsSpider(BaseSceneScraper):
    name = 'GotCuffs'
    network = 'GotCuffs'
    parent = 'GotCuffs'
    site = 'GotCuffs'

    start_urls = [
        'https://gotcuffs.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/vod/updates/page_%s.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//comment()[contains(., "Title")]/following-sibling::a/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())
            else:
                item['title'] = ""

            scenedate = scene.xpath('.//comment()[contains(., "Date")]/following-sibling::text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                item['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            item['id'] = scene.xpath('./@data-setid').get()

            image = scene.xpath('.//img[contains(@class, "update_thumb")]/@src0_1x')
            if image:
                image = self.format_link(response, image.get()).replace(" ", "%20")
                item['image'] = self.find_best_image(response, image)
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = None
                item['image_blob'] = None

            sceneurl = scene.xpath('./a[1]/@href')
            if sceneurl:
                item['url'] = self.format_link(response, sceneurl.get())
            else:
                item['url'] = None

            item['tags'] = ['Bondage']

            duration = scene.xpath('.//div[@class="update_counts"]/text()')
            if duration:
                duration = duration.get().strip()
                duration = re.search(r'(\d+)', duration)
                if duration:
                    item['duration'] = int(duration.group(1)) * 60

            item['site'] = 'GotCuffs'
            item['parent'] = 'GotCuffs'
            item['network'] = 'GotCuffs'

            performers = scene.xpath('.//span[@class="update_models"]/a/text()')
            if performers:
                item['performers'], item['performers_data'] = self.get_performers_data(performers.getall())

            yield self.check_item(item, self.days)


    def get_performers_data(self, models):
        performers = []
        performers_data = []
        for model in models:
            model_name = string.capwords(model.strip())
            performers.append(model_name)
            performers_data.append({
                "name": model_name,
                "site": "GotCuffs",
                "network": "GotCuffs",
                "extra": {"gender": "Female"}
            })
        return performers, performers_data

    def image_exists(self, url):
        try:
            r = requests.head(url, allow_redirects=True, timeout=5)
            return r.status_code == 200
        except requests.RequestException:
            return False
        
    def find_best_image(self, response, original_url):
        for suffix in ("-4x", "-3x", "-2x", "-1x"):
            candidate = original_url.replace("-1x", suffix)
            candidate = self.format_link(response, candidate).replace(" ", "%20")
            if self.image_exists(candidate):
                return candidate
        return None        