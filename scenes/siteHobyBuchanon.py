import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteHobyBuchanonSpider(BaseSceneScraper):
    name = 'HobyBuchanon'

    start_urls = [
        'https://hobybuchanon.com'
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/updates?page=%s&order_by=publish_date&sort_by=desc',
    }

    cookies = {"close-warning": "1"}

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="img-container"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, cookies=self.cookies, headers=self.headers)

    def parse_scene(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']['content']
            item = self.init_scene()
            item['site'] = "Hoby Buchanon"
            item['parent'] = "Hoby Buchanon"
            item['network'] = "Hoby Buchanon"
            item['title'] = self.cleanup_title(jsondata['title'])
            item['description'] = self.cleanup_text(jsondata['description'])
            performers = jsondata['models_thumbs']

            item['performers'] = []
            item['performers_data'] = []
            for performer in performers:
                performer_extra = {}
                performer_extra['name'] = performer['name']
                performer_extra['site'] = "Hoby Buchanon"
                performer_extra['extra'] = {}
                performer_extra['extra']['gender'] = "Female"
                perf_image = performer['thumb']
                if perf_image:
                    performer_extra['image'] = perf_image
                    performer_extra['image_blob'] = self.get_image_blob_from_link(performer_extra['image'])
                item['performers_data'].append(performer_extra)
                item['performers'].append(performer['name'])

            item['date'] = self.parse_date(jsondata['publish_date']).strftime('%Y-%m-%d')
            item['duration'] = self.duration_to_seconds(jsondata['videos_duration'])

            item['id'] = jsondata['id']
            item['image'] = jsondata['thumb']
            if "http" not in item['image']:
                item['image'] = "https:" + item['image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            if "tags" in jsondata and jsondata['tags']:
                item['tags'] = jsondata['tags']
            item['trailer'] = ""
            item['url'] = f"https://hobybuchanon.com/updates/{jsondata['slug']}"
            item['type'] = 'Scene'

            if item['date'] > "2022-08-17":
                yield self.check_item(item, self.days)
