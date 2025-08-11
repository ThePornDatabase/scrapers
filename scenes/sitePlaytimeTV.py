import re
import requests
import scrapy
import json
import string
from scrapy import Selector
from tpdb.BaseSceneScraper import BaseSceneScraper


class SitePlaytimeTVSpider(BaseSceneScraper):
    name = 'PlayTimePOV'
    network = 'PlayTimePOV'
    parent = 'PlayTimePOV'
    site = 'PlayTimePOV'

    url = "https://playtimepov.tv/ajax.php"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://playtimepov.tv",
        "Referer": "https://playtimepov.tv/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0",
        "X-Requested-With": "XMLHttpRequest"
    }
    formdata = {
        "module": "channel",
        "act": "channel_media",
        "ref_id": "20"
    }

    selector_map = {
        'description': '//div[contains(@class, "text14 media-description")]/text()[1]',
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))
        meta = {}
        meta['page'] = self.page

        page = str((int(meta['page']) - 1) * 12)
        self.formdata['ref_id'] = page
        yield scrapy.FormRequest(self.url, method="POST", headers=self.headers, formdata=self.formdata, callback=self.parse)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                page = str((int(meta['page']) - 1) * 12)
                self.formdata['ref_id'] = page
                yield scrapy.FormRequest(self.url, method="POST", headers=self.headers, formdata=self.formdata, callback=self.parse)

    def get_scenes(self, response):
        meta = response.meta
        data = data = json.loads(response.text)
        media_list = [data[key] for key in data.keys() if key.isdigit()]

        for entry in media_list:
            scene_data = Selector(text=entry['html'])
            meta['url'] = scene_data.xpath('//div[contains(@class, "media-item")]/a[1]/@href').get()
            meta['title'] = scene_data.xpath('//div[contains(@class, "media-item")]/a[1]/@data-aname').get()
            if " - " in meta['title']:
                meta['performers'] = [re.search(r'.* - (.*)', meta['title']).group(1)]

            duration = scene_data.xpath('//div[contains(@class, "media-item")]//div[contains(@class, "video-card-time")]/text()')
            if duration:
                meta['duration'] = self.duration_to_seconds(duration.get())

            image = scene_data.xpath('//div[contains(@class, "media-item")]//img/@src')
            if image:
                image = image.get()
                meta['image'] = re.search(r'(.*)\?', image).group(1)
                meta['image_blob'] = self.get_image_blob_from_link(image)

            title_strip = re.sub(r'[^a-z0-9-]+', '', meta['title'].lower())
            tags = scene_data.xpath('//div[contains(@class, "media-item")]//a[contains(@href, "hashtags")]/@href')
            if tags:
                tags = tags.getall()
                meta['tags'] = []
                for tag in tags:
                    if tag.lower() not in title_strip:
                        meta['tags'].append(string.capwords(re.search(r'.*/(.*?)$', tag).group(1)))

            meta['id'] = scene_data.xpath('//div[contains(@class, "media-item")]/a[1]/@data-media_id').get()
            meta['site'] = "PlayTimeTV"
            meta['parent'] = "PlayTimeTV"
            meta['network'] = "PlayTimeTV"

            bare_html = entry['html'].replace("\r", "").replace("\n", "").replace("\t", "")
            scenedate = re.search(r'stats.*?(\w+ \d{1,2}, \d{4})', bare_html)
            if scenedate:
                meta['date'] = self.parse_date(scenedate.group(1), date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

            # ~ print(meta)
            if meta['id']:
                yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)
