import re
import string
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteZlatexaSpider(BaseSceneScraper):
    name = 'Zlatexa'
    network = 'Zlatexa'
    parent = 'Zlatexa'
    site = 'Zlatexa'

    start_urls = [
        'https://zlatexa.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/free_updates.php?we_lv_start_video-update=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 12)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="entry clearfix"][.//i[@class="icon-video"]]')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = string.capwords(scene.xpath('.//h2//text()').get())

            scenedate = scene.xpath('.//i[contains(@class, "calendar")]/following-sibling::text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get(), date_formats=['%d.%b.%Y']).strftime('%Y-%m-%d')

            desc = scene.xpath('.//div[@class="entry-content"]/p//text()')
            if desc:
                desc = desc.getall()
                item['description'] = " ".join(desc)

            image = scene.xpath('.//div[@class="slide"]/a[1]/img/@src')
            if image:
                image = self.format_link(response, image.get())
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
                item['id'] = re.search(r'content/(\d+)', image).group(1)

            duration = scene.xpath('.//i[@class="icon-video"]/following-sibling::text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'(?:\d+:)?\d{1,2}:\d{1,2}', duration)
                if duration:
                    duration = duration.group(0)
                    item['duration'] = self.duration_to_seconds(duration)

            item['performers'] = ['Zlatexa']
            item['tags'] = ['Fetish', 'Latex']

            item['url'] = response.url
            item['site'] = "Zlatexa"
            item['parent'] = "Zlatexa"
            item['network'] = "Zlatexa"

            yield self.check_item(item, self.days)

