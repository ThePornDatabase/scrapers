import re
import json
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteBlakeMasonSpider(BaseSceneScraper):
    name = 'BlakeMason'

    start_urls = [
        'https://blakemason.com'
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
            item['site'] = "Blake Mason"
            item['parent'] = "Blake Mason"
            item['network'] = "Blake Mason"
            item['title'] = self.cleanup_title(jsondata['title'])
            item['description'] = self.cleanup_text(jsondata['description'])
            item['performers'] = jsondata['models']
            item['date'] = self.parse_date(jsondata['publish_date']).strftime('%Y-%m-%d')
            duration = re.search(r'^(\d+)', jsondata['videos_duration'])
            if duration:
                duration = int(duration.group(1))
                if duration:
                    item['duration'] = str(duration)
                else:
                    item['duration'] = ""
            item['id'] = jsondata['id']
            item['image'] = jsondata['thumbnail']
            if "http" not in item['image']:
                item['image'] = "https:" + item['image']
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['tags'] = jsondata['tags']
            item['trailer'] = ""
            item['url'] = f"https://blakemason.com/videos/{jsondata['slug']}"
            item['type'] = 'Scene'

            yield self.check_item(item, self.days)
