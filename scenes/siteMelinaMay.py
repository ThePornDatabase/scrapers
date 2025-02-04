import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMelinaMaySpider(BaseSceneScraper):
    name = 'MelinaMay'

    start_urls = [
        'https://melina-may.com'
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/videos?page=%s&order_by=publish_date&sort_by=desc',
    }

    cookies = {"close-warning": "1"}

    def get_scenes(self, response):
        scenes = response.xpath('//h4[@class="content-title-wrap"]/a/@href|//h2[@class="content-title-wrap"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, cookies=self.cookies, headers=self.headers)

    def parse_scene(self, response):
        jsondata = response.xpath('//script[@id="__NEXT_DATA__"]/text()')
        if jsondata:
            jsondata = json.loads(jsondata.get())
            jsondata = jsondata['props']['pageProps']['content']
            item = SceneItem()
            item['site'] = "Melina May"
            item['parent'] = "Melina May"
            item['network'] = "Melina May"
            item['title'] = self.cleanup_title(jsondata['title'])
            item['description'] = self.cleanup_text(jsondata['description'])
            item['performers'] = jsondata['models']
            item['date'] = self.parse_date(jsondata['publish_date']).strftime('%Y-%m-%d')
            if "videos_duration" in jsondata and jsondata['videos_duration']:
                item['duration'] = self.duration_to_seconds(jsondata['videos_duration'])
            else:
                item['duration'] = ""
            item['id'] = jsondata['id']
            item['image'] = jsondata['thumb']
            if "http" not in item['image']:
                item['image'] = "https:" + item['image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['tags'] = jsondata['tags']
            if "trailer_url" in jsondata and jsondata['trailer_url']:
                item['trailer'] = jsondata['trailer_url']
            else:
                item['trailer'] = ""
            item['url'] = f"https://melina-may.com/videos/{jsondata['slug']}"
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
