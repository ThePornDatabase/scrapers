import re
import os.path
from pathlib import Path
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteDungeonCorpv2Spider(BaseSceneScraper):
    name = 'DungeonCorpv2'
    network = 'DungeonCorp'

    start_urls = [
        'https://www.dungeoncorp.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//span[@class="shootid"]/..//text()',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/?page=updates&p=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "update_info")]/ancestor::div[1]')
        for scene in scenes:
            scenedate = scene.xpath('.//i[contains(@class, "clock")]/following-sibling::text()[1]')
            if scenedate:
                scenedate = scenedate.get().strip()
                meta['date'] = self.parse_date(scenedate, date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')

            duration = scene.xpath('.//i[contains(@class, "video")]/following-sibling::text()[1]')
            if duration:
                duration = re.sub(r'[^0-9a-z]+', '', duration.get().strip().lower())
                duration = re.search(r'(\d+)', duration)
                if duration:
                    duration = duration.group(1)
                    meta['duration'] = str(int(duration) * 60)

            site = scene.xpath('.//a[contains(@href, "&site")]/text()')
            if site:
                site = site.get().strip()
                meta['site'] = site
            else:
                meta['site'] = "DungeonCorp"
            meta['parent'] = "DungeonCorp"

            title = scene.xpath('./a[1]/@title')
            if title:
                meta['title'] = title.get().strip()

            meta['performers'] = scene.xpath('.//a[contains(@href, "=models")]/text()').getall()

            image = scene.xpath('.//img/@src')
            if image:
                image = image.get()
                meta['image'] = image
                meta['image_blob'] = self.get_image_blob_from_link(image)

            update_id = scene.xpath('./a[1]/@data-update-id')
            if update_id:
                meta['sceneid'] = update_id.get().strip()

            scene = scene.xpath('./a[1]/@href').get()
            if meta['sceneid']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_id(self, response):
        meta = response.meta
        sceneid = response.xpath('//span[@class="shootid"]/text()')
        validid = False
        if sceneid:
            sceneid = sceneid.get().strip().lower()
            sceneid = re.sub(r'[^0-9a-z_:-]+', '', sceneid)
            if ":" in sceneid:
                sceneid = re.search(r'\:(.*)', sceneid)
                if sceneid:
                    sceneid = sceneid.group(1)
                    validid = True
        if validid:
            return sceneid
        return meta['sceneid']

    def get_description(self, response):
        description = super().get_description(response)
        return description.replace("( ", "(").replace(" )", ")")

    def parse_scene(self, response):
        meta = response.meta
        item = self.init_scene()

        item['title'] = self.cleanup_title(meta['title'])
        item['id'] = self.get_id(response)
        item['description'] = self.get_description(response)
        item['image'] = meta['image']
        item['image_blob'] = meta['image_blob']
        item['date'] = meta['date']
        item['url'] = response.url
        item['tags'] = ['Bondage', 'Submission']
        item['duration'] = meta['duration']
        item['site'] = meta['site']
        item['parent'] = 'DungeonCorp'
        item['network'] = 'DungeonCorp'
        item['type'] = "Scene"
        item['performers'] = meta['performers']
        item['performers_data'] = []
        for model in item['performers']:
            performer_extra = {}
            performer_extra['network'] = "DungeonCorp"
            performer_extra['site'] = "DungeonCorp"
            performer_extra['name'] = model
            performer_extra['extra'] = {}
            performer_extra['extra']['gender'] = "Female"
            item['performers_data'].append(performer_extra)

        id_check_file = "dungeoncorp_id.txt"
        if not os.path.exists(id_check_file):
            Path(id_check_file).touch()
        with open(id_check_file, 'r', encoding="utf-8") as file1:
            for i in file1.readlines():
                i = i.lower().strip()
                if "|" in i:
                    in_site = re.search(r'(.*)\|', i).group(1)
                    in_sceneid = re.search(r'\|(.*)', i).group(1)
                    if in_site.lower().strip() == item['site'].lower().strip() and in_sceneid == item['id']:
                        if "_2" not in item['id']:
                            item['id'] = item['id'] + "_2"
                        else:
                            item['id'] = item['id'] + "_3"
        file1.close()

        with open(id_check_file, 'a', encoding="utf-8") as file1:
            file1.write(f"{item['site']}|{item['id']}\n")
        file1.close()

        yield self.check_item(item, self.days)
