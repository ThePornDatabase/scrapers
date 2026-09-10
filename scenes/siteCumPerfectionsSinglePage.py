import re
import requests
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCumPerfectionSinglePageSpider(BaseSceneScraper):
    name = 'CumPerfectionSinglePage'
    network = 'CumPerfection'
    parent = 'CumPerfection'
    site = 'CumPerfection'

    start_urls = [
        'https://www.cumperfection.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/categories/movies_%s_d.html',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//div[@class="update_details"]')
        for scene in scenes:
            item = self.init_scene()
            item['id'] = scene.xpath('./@data-setid').get().strip()
            scenedate = scene.xpath('.//comment()[contains(., "Date")]/following-sibling::text()')
            item['date'] = "1970-01-01"
            if scenedate:
                scenedate = scenedate.get()
                scenedate = scenedate.strip()
                item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).strftime('%Y-%m-%d')
            
            if self.check_item(item, self.days) and item['date'] > "2025-12-18":
                title = scene.xpath('.//comment()[contains(., "Title")]/following-sibling::a/text()')
                if title:
                    title = title.get().strip()
                    item['title'] = title

                performers = scene.xpath('.//comment()[contains(., "Models")]/following-sibling::span/a/text()')
                if performers:
                    item['performers'] = [performer.strip() for performer in performers.getall()]

                duration = scene.xpath('.//comment()[contains(., "Movie Totals")]/following-sibling::div[1]/text()')   
                if duration:
                    duration = duration.get()
                    duration = duration.replace("&nbsp;", "").strip()
                    duration = re.sub(r'[^0-9:min]', '', duration.lower())
                    duration = re.search(r'(\d+)min', duration)
                    if duration:
                        duration = duration.group(1)
                        item['duration'] = str(int(duration) * 60)

                image = scene.xpath('.//comment()[contains(., "Thumbnail")]/following-sibling::a/img/@data-src0_3x')
                if image:
                    image = image.get()
                    item['image'] = self.format_link(response, image)
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                
                item['site'] = "CumPerfection"
                item['parent'] = "CumPerfection"
                item['network'] = "CumPerfection"
                item['url'] = response.url
                item['tags'] = ['Facial']

                yield item