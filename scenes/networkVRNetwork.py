import json
import requests
import scrapy
import re
import pycountry
import html
from datetime import datetime, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteVRNetworkAPISpider(BaseSceneScraper):
    name = 'VRNetwork'
    network = 'VRNetwork'
    parent = 'VRNetwork'
    site = 'VRNetwork'

    start_urls = [
        'https://content.vrconk.com',
        'https://content.vrbangers.com',
        # 'https://content.arporn.com', Not on this API
        'https://content.vrbtrans.com',
        'https://content.blowvr.com',
        'https://content.vrbgay.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/content/v1/videos?page=%s&type=videos&sort=latest&show_custom_video=1&limit=12',
        'type': 'Scene',
    }

    custom_scraper_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0',
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 1,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
        "LOG_LEVEL": 'INFO',
        "EXTENSIONS": {'scrapy.extensions.logstats.LogStats': None},
        "MEDIA_ALLOW_REDIRECTS": True,
        "HTTPERROR_ALLOWED_CODES": [404],
    }

    def start_requests(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for link in self.start_urls:
            meta['base_url'] = link
            self.headers = {"name": "referer", "value": re.sub(r'content\.', '', link)}
            yield scrapy.Request(url=self.get_next_page_url(link, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = json.loads(response.text)
        for movie in scenes['data']['items']:
            meta['id'] = movie['slug']
            meta['date'] = datetime.utcfromtimestamp(movie['publishedAt']).strftime('%Y-%m-%d')
            if "arporn" in response.url:
                link = f"{meta['base_url']}/api/content/v1/jsonld/video/{movie['slug']}"
            else:
                link = f"{meta['base_url']}/api/content/v1/videos/{movie['slug']}"
            yield scrapy.Request(link, callback=self.parse_scene, meta=meta)

    def parse_scene(self, response):
        meta = response.meta
        movie = response.json()
        movie = movie['data']['item']
        base_url = meta['base_url']
        site = re.search(r'content\.(\w+)\.com', base_url).group(1)
        scene_url = f"https://{site}.com/video/"

        item = self.init_scene()

        item['id'] = meta['id']
        item['date'] = meta['date']
        item['title'] = movie['title']

        item['performers'] = []
        item['performers_data'] = []
        if "models" in movie and movie['models']:
            for performer in movie['models']:
                item['performers'].append(performer['title'])
                perf_data = requests.get(f"{base_url}/api/content/v1/models/{performer['slug']}")
                if perf_data:
                    performers_data = self.parse_performer(perf_data.content, performer['title'], site, base_url)
                    if performers_data:
                        item['performers_data'].append(performers_data)

        item['description'] = re.sub(r'<[^>]+>', '', html.unescape(movie['description']))

        if "heroImg" in movie and movie['heroImg']:
            image = base_url + movie['heroImg']['permalink']
        else:
            image = base_url + movie['poster']['permalink']

        if image:
            item['image'] = image
            item['image_blob'] = self.get_image_blob_from_link(item['image'])

        item['tags'] = []
        if "categories" in movie and movie['categories']:
            for category in movie['categories']:
                item['tags'].append(category['name'])

        if "videoPreviewPoster" in movie and movie['videoPreviewPoster']:
            item['trailer'] = movie['videoPreviewPoster']

        item['url'] = f"{scene_url}{movie['slug']}/"

        if "videoSettings" in movie and movie['videoSettings']:
            if "duration" in movie['videoSettings'] and movie['videoSettings']['duration']:
                item['duration'] = str(movie['videoSettings']['duration'])

        item['site'] = site
        item['network'] = "VRNetwork"
        item['parent'] = "VRNetwork"

        yield self.check_item(item, self.days)

    def parse_performer(self, perf_data, name, site, base_url):
        performer = json.loads(perf_data)
        perf_url = f"https://{site}.com/model/"

        perf = {}
        if "data" in performer and performer['data']:
            performer = performer['data']['item']
            perf['name'] = name
            perf['extra'] = {}
            if "vrbgay" in site.lower():
                perf['extra']['gender'] = "Male"
            elif "vrbtrans" in site.lower():
                perf['extra']['gender'] = "Trans Female"
            else:
                perf['extra']['gender'] = "Female"

            perf['network'] = "VRNetwork"
            perf['site'] = "VRNetwork"

            image = False
            if "galleryImages" in performer and len(performer['galleryImages']):
                image_set = performer['galleryImages'][0]
                if "previews" in image_set and image_set['previews']:
                    for image_preview in image_set['previews']:
                        if image_preview['sizeAlias'].lower() == "xs":
                            image = base_url + image_preview['permalink']
            else:
                image_link = performer.get('seoParams', {}).get('ogParams', {}).get('imageSecureFile', {}).get('permalink')
                if image_link:
                    image = base_url + image_link

            if image:
                perf['image'] = image
                perf['image_blob'] = self.get_image_blob_from_link(image)

            if "modelInformation" in performer and len(performer['modelInformation']):
                for model_info in performer['modelInformation']:

                    if model_info['label'].lower() == "birthday":
                        if int(model_info['value']):
                            birthday = int(model_info['value'])
                            if birthday >= 0:
                                date = datetime.utcfromtimestamp(birthday)
                            else:
                                date = datetime(1970, 1, 1) + timedelta(seconds=birthday)
                            perf['extra']['birthday'] = date.strftime('%Y-%m-%d')

                    if model_info['label'].lower() == "measuraments" or model_info['label'].lower() == "measurements":
                        perf['extra']['measurements'] = re.sub(r'[^a-zA-Z0-9-]+', '', model_info['value'])

                    if model_info['label'].lower() == "height" and model_info['value']:
                        perf['extra']['height'] = model_info['value'] + "cm"

                    if model_info['label'].lower() == "weight" and model_info['value']:
                        perf['extra']['weight'] = model_info['value'] + "kg"

                    if model_info['label'].lower() == "tattoos" and model_info['value']:
                        perf['extra']['tattoos'] = model_info['value']

                    if model_info['label'].lower() == "piercings" and model_info['value']:
                        perf['extra']['piercings'] = model_info['value']

                    if "country" in model_info['label'].lower() and model_info['value']:
                        if "european" not in model_info['value'].lower():
                            perf['extra']['nationality'] = model_info['value']
                            country_code = pycountry.countries.get(name=model_info['value'])
                            if country_code:
                                perf['extra']['birthplace_code'] = country_code.alpha_2

                    if "place of" in model_info['label'].lower() and model_info['value']:
                        perf['extra']['birthplace'] = model_info['value']
                        country_code = pycountry.countries.get(name=model_info['value'])
                        if country_code:
                            perf['extra']['birthplace_code'] = country_code.alpha_2
                            perf['extra']['nationality'] = model_info['value']
                        if 'nationality' in perf['extra'] and perf['extra']['nationality']:
                            if perf['extra']['birthplace'].lower() != perf['extra']['nationality'].lower():
                                perf['extra']['birthplace'] = perf['extra']['birthplace'] + ", " + perf['extra']['nationality']

                    if model_info['label'].lower() == "ethnicity" and model_info['value']:
                        perf['extra']['ethnicity'] = model_info['value']

                    if model_info['label'].lower() == "hair color" and model_info['value']:
                        perf['extra']['haircolor'] = model_info['value']

                    if model_info['label'].lower() == "eye color" and model_info['value']:
                        perf['extra']['eyecolor'] = model_info['value']

            if "tags" in performer and len(performer['tags']):
                for tag in performer['tags']:
                    if "fake-tits" in tag['slug']:
                        perf['extra']['fakeboobs'] = True

            if "description" in performer and performer['description']:
                perf['bio'] = re.sub(r'<[^>]+>', '', html.unescape(performer['description']))

            perf['url'] = f"{perf_url}{performer['slug']}/"

        return perf
