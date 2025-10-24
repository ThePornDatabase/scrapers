import re
import json
import requests
import scrapy
import string
from datetime import datetime, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteInTheCrackSpider(BaseSceneScraper):
    name = 'InTheCrack'

    selector_map = {
        'external_id': r'',
        'pagination': '',
        'type': 'Scene',
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page
        days_back = int(self.days)
        threshold_date = datetime.today().date() - timedelta(days=days_back)

        meta['collections'] = []
        req = requests.get("https://api.inthecrack.com/Collection")
        if req.status_code == 200:
            meta['collections'] = json.loads(req.content)

        meta['models'] = []
        req = requests.get("https://api.inthecrack.com/Model")
        if req.status_code == 200:
            meta['models'] = json.loads(req.content)

        if meta['collections'] and meta['models']:
            for collection in meta['collections']:
                scenedate = collection['releaseDate']
                scene_date = datetime.strptime(scenedate, "%Y-%m-%d").date()
                is_recent = scene_date >= threshold_date
                if is_recent:
                    meta['date'] = collection['releaseDate']
                    link = f"https://api.inthecrack.com/Collection/{collection['id']}"
                    yield scrapy.Request(link, callback=self.parse_itc_scene, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_itc_scene(self, response):
        force_update = self.settings.get('force_update')
        if force_update:
            force_update = True
        force_fields = self.settings.get('force_fields')
        if force_fields:
            force_fields = force_fields.split(",")
        local_run = self.settings.get('local')
        if local_run:
            local_run = True

        meta = response.meta
        scene = json.loads(response.text)
        item = self.init_scene()
        item['site'] = "In The Crack"
        item['parent'] = "In The Crack"
        item['network'] = "In The Crack"

        item['id'] = str(scene['id'])
        item['title'] = item['id'] + " " + string.capwords(scene['title']).rstrip(string.punctuation)
        item['description'] = f"Shoot Date: {scene['shootDate']}\n" + f"Shoot Location: {scene['shootLocation']}\n" + f"Number of Clips: {len(scene['clips'])}\n\n" + scene['description'].replace('\n', ' ').strip()
        meta['orig_description'] = item['description']

        for clip in scene['clips']:
            clipnum = re.search(r'_(\d{2})_', clip['videos'][0]['filename'])
            clip_number = clipnum.group(1)
            clip_title = string.capwords(clip['title']).rstrip(string.punctuation)
            clip_description = clip['description'].replace('\n', ' ').strip()
            item['description'] += f"\n\nClip {clip_number}: {clip_title}\n{clip_description}"

        item['description'] = item['description'].replace('\r\n', '\n').replace('\r', '\n')
        item['description'] = re.sub(r'\n{3,}', '\n\n', item['description']) + "\n"

        item['date'] = meta['date']
        duration = 0
        for clip in scene['clips']:
            duration = duration + int(clip['length'])
        item['duration'] = str(duration)

        item['performers'] = []
        item['performers_data'] = []
        for model in scene['models']:
            for perf in meta['models']:
                if model == perf['id']:
                    if " " not in perf['name']:
                        perf_name = perf['name'] + str(perf['id'])
                    else:
                        perf_name = perf['name']

                    item['performers'].append(perf_name)
                    perf_data = {}
                    perf_data['site'] = "In The Crack"
                    perf_data['name'] = perf_name
                    perf_data['extra'] = {}
                    perf_data['extra']['gender'] = "Female"
                    if "countries" in perf and perf['countries']:
                        perf_data['extra']['nationality'] = string.capwords(perf['countries'][0]['name'])
                        perf_data['extra']['birthplace'] = string.capwords(perf['countries'][0]['name'])
                        perf_data['extra']['birthplace_code'] = perf['countries'][0]['isO2']

                    if "height" in perf and perf['height']:
                        perf_data['extra']['height'] = str(perf['height']) + "cm"

                    if "weight" in perf and perf['weight']:
                        perf_data['extra']['weight'] = str(perf['weight']) + "kg"

                    if "ethnicity" in perf and perf['ethnicity'] and perf['ethnicity'].lower() != "none":
                        perf_data['extra']['ethnicity'] = perf['ethnicity']

                    if "birthdate" in perf and perf['birthdate']:
                        birthdate = re.search(r'(\d{4}-\d{2}-\d{2})', perf['birthdate'])
                        if birthdate:
                            perf_data['extra']['birthday'] = birthdate.group(1)

                    item['performers_data'].append(perf_data)

        collectionid = f"{int(item['id']):03}" if int(item['id']) < 100 else item['id']
        item['image'] = f"https://api.inthecrack.com/FileStore/images/posters/collections/{collectionid}.jpg"
        if not local_run:
            if not force_update or (force_update and "image" in force_fields):
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['scenes'] = []
        for clip in scene['clips']:
            item['scenes'].append({'site': "In The Crack Clips", 'external_id': f"{item['id']}-{str(clip['id'])}"})

        item['url'] = f"https://www.inthecrack.com/collection/{item['id']}"

        yield item

        for clip in scene['clips']:
            clipitem = []
            clipitem = item.copy()
            clipitem['site'] = "In The Crack Clips"
            clipnum = re.search(r'_(\d{2})_', clip['videos'][0]['filename'])
            if clipnum:
                clipnum = clipnum.group(1)
                clipitem['title'] = item['title'] + ": " + string.capwords(clip['title']).rstrip(string.punctuation)

                clipitem['id'] = f"{item['id']}-{str(clip['id'])}"

                if "length" in clip and clip['length']:
                    clipitem['duration'] = str(clip['length'])

                clean_description = clip['description'].replace('\r\n', '\n').replace('\r', '\n').replace('\n', ' ').strip()
                clipitem['description'] = f"{meta['orig_description']}\n\nClip #{clipnum} of Collection '{item['title']}':\n{clean_description}\n"
                clipitem['description'] = re.sub(r'\n{3,}', '\n\n', clipitem['description']) + "\n"

                if "releaseDate" in clip and clip['releaseDate']:
                    clipdate = re.search(r'(\d{4}-\d{2}-\d{2})', clip['releaseDate'])
                    if clipdate:
                        clipitem['date'] = clipdate.group(1)

                clipimage = re.search(r'(\d+_\d{2}_[a-zA-Z3_]+)\d+x\d+', clip['videos'][0]['filename'])
                if clipimage:
                    clipimage = clipimage.group(1)
                    if not clip['thumbnail'].strip():
                        clip['thumbnail'] = "jpg"
                    clipitem['image'] = f"https://api.inthecrack.com/FileStore/images/posters//clips/{clipimage}.{clip['thumbnail']}"
                    if not local_run:
                        if not force_update or (force_update and "image" in force_fields):
                            clipitem['image_blob'] = self.get_image_blob_from_link(clipitem['image'])

                if "_3d" in clipitem['image']:
                    clipitem['tags'] = ['Virtual Reality']

                clipitem['movies'] = [{'site': item['site'], 'external_id': item['id']}]
                clipitem['scenes'] = []

                yield clipitem
