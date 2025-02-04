import re
import string
import scrapy
import requests
from datetime import datetime
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteModelMediaAsiaSpider(BaseSceneScraper):
    name = 'ModelMediaAsia'
    site = 'Model Media Asia'
    parent = 'Model Media Asia'
    network = 'Model Media Asia'

    start_urls = [
        'https://api.modelmediaasia.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/v2/videos?page=%s&pageSize=12&sort=published_at',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.json()
        scenes = scenes['data']['list']
        for scene in scenes:
            url = f"https://api.modelmediaasia.com/api/v2/videos/{scene['serial_number']}"
            yield scrapy.Request(url, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        scene = response.json()
        scene = scene['data']
        item = SceneItem()
        item['title'] = self.cleanup_title(scene['title'])
        item['description'] = self.cleanup_description(scene['description'])
        item['date'] = datetime.fromtimestamp(scene['published_at'] / 1000).strftime("%Y-%m-%d")

        item['image'] = scene['cover']
        if item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        else:
            item['image_blob'] = ''

        item['id'] = scene['id']
        item['trailer'] = scene['preview_video']
        item['duration'] = str(scene['duration'])
        item['url'] = f"https://modelmediaasia.com/en-US/videos/{scene['serial_number']}"
        item['network'] = "Model Media"
        item['site'] = "Model Media Asia"
        item['parent'] = "Model Media"

        item['performers'], item['performers_data'] = self.get_performers_data(scene['models'])
        for performer in item['performers_data']:
            if "image" in performer and performer['image']:
                performer['image_blob'] = self.get_image_blob_from_link(performer['image'])

        item['tags'] = []
        for tag in scene['tags']:
            item['tags'].append(tag['name'])

        yield self.check_item(item, self.days)

    def get_performers_data(self, performer_list):
        performers_data = []
        performers = []
        if len(performer_list):
            for performer in performer_list:
                if performer['name'].lower().strip() != "amateur":
                    performers.append(performer['name'])
                    perf = {}
                    perf['name'] = performer['name']
                    perf['extra'] = {}
                    if "gender" in performer and performer['gender']:
                        if performer['gender'].lower() == "trans":
                            performer['gender'] = "Transgender Female"
                        perf['extra']['gender'] = string.capwords(performer['gender'])

                    if performer['avatar']:
                        perf['image'] = performer['avatar']

                    if "birth_day" in performer and performer['birth_day'] and performer['birth_day'] > "1950-01-01":
                        perf['extra']['birthday'] = performer['birth_day']

                    if "height_cm" in performer and performer['height_cm'] and performer['height_cm'] > 100:
                        perf['extra']['height'] = str(performer['height_cm']) + "cm"
                    elif "height_ft" in performer and performer['height_ft'] and performer['height_ft'] > 100:
                        perf['extra']['height'] = str(performer['height_ft']) + "cm"

                    if "weight_kg" in performer and performer['weight_kg'] and performer['weight_kg'] > 30:
                        perf['extra']['weight'] = str(performer['weight_kg']) + "kg"
                    elif "weight_lbs" in performer and performer['weight_lbs'] and performer['weight_lbs'] < 90:
                        perf['extra']['height'] = str(performer['weight_lbs']) + "kg"

                    if performer['measurements_chest'] and performer['measurements_waist'] and performer['measurements_hips']:
                        chestcm = 0
                        hipscm = 0
                        waistcm = 0
                        cupsize = ""

                        chest = re.search(r'(\d+)', performer['measurements_chest'])
                        if chest:
                            chest = int(chest.group(1))
                            if chest > 40:
                                chestcm = round(chest / 2.54)
                            else:
                                chestcm = chest

                        cup = re.search(r'([a-zA-Z]+)', performer['measurements_chest'])
                        if cup:
                            cupsize = cup.group(1).upper()

                        waist = performer['measurements_waist']
                        if waist:
                            if waist > 40:
                                waistcm = round(waist / 2.54)
                            else:
                                waistcm = performer['measurements_waist']

                        hips = performer['measurements_hips']
                        if hips:
                            if hips > 40:
                                hipscm = round(hips / 2.54)
                            else:
                                hipscm = performer['measurements_hips']

                        if chestcm and hipscm and waistcm:
                            perf['extra']['measurements'] = f"{str(chestcm)}{cupsize}-{str(waistcm)}-{str(hipscm)}"

                    if "birth_day" in performer and performer['birth_day'] and performer['birth_day'] > "1950-01-01":
                        perf['extra']['birthday'] = performer['birth_day']

                    perf['network'] = "Model Media"
                    perf['site'] = "Model Media Asia"
                    performers_data.append(perf)
        return performers, performers_data

    def get_image_from_link(self, image):
        if image:
            headers = {'referer': "https://modelmediaasia.com/"}
            req = requests.get(image, headers=headers, verify=False)
            if req and req.ok:
                return req.content
        return None
