import re
import string
import requests
import scrapy
from datetime import datetime
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkTeamskeet2025Spider(BaseSceneScraper):
    name = 'NetworkTeamskeet2025'
    network = 'Teamskeet'
    parent = 'Teamskeet'

    start_url = 'https://tours-store.psmcdn.net'

    paginations = [
        '/familybundle/_search?sort=publishedDate:desc&q=(type:video%20AND%20isXSeries:false%20)&size=30&from=<page>',
        '/freeusebundle/_search?sort=publishedDate:desc&q=(type:video%20AND%20isXSeries:false%20)&size=30&from=<page>',
        ## '/mylf_bundle/_search?q=(type:video%20AND%20isXSeries:false%20AND%20isUpcoming:false)&sort=publishedDate:desc&size=30&from=<page>',
        ## '/mylf_bundle2/_search?q=(type:video%20AND%20isXSeries:false%20AND%20isUpcoming:false)&sort=publishedDate:desc&size=30&from=<page>',
        '/network_mylf/_search?q=(type:video%20AND%20isXSeries:false%20AND%20isUpcoming:false)&sort=publishedDate:desc&size=30&from=<page>',
        '/pervbundle/_search?sort=publishedDate:desc&q=(type:video%20AND%20isXSeries:false%20)&size=30&from=<page>',
        '/reptyle_bundle/_search?sort=publishedDate:desc&q=(type:video%20AND%20isXSeries:false%20)&size=30&from=<page>',
        '/sau_network/_search?sort=publishedDate:desc&q=(type:video%20AND%20isUpcoming:false)&size=30&from=<page>',
        '/swap_bundle/_search?sort=publishedDate:desc&q=(type:video%20AND%20isXSeries:false%20)&size=30&from=<page>',
        '/test_fos/_search?sort=publishedDate:desc&q=(type:video%20AND%20isXSeries:false%20)&size=30&from=<page>',
        '/ts_network/_search?q=(type:video%20AND%20isUpcoming:false)&sort=publishedDate:desc&size=30&from=<page>',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/ts_network/_search?q=(type:video)&sort=publishedDate:desc&size=30&from=<page>',
        'type': 'Scene',
    }
    async def start(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            link = self.start_url
            yield scrapy.Request(url=self.get_next_page_url(link, pagination, self.page), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            print (count, response.meta['page'], self.limit_pages)
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                url = self.get_next_page_url(response.url, meta['pagination'], meta['page'])
                print('NEXT PAGE: ' + str(meta['page']) + ' - ' + url)
                yield scrapy.Request(url, callback=self.parse, meta=meta)

    def get_next_page_url(self, base, pagination, page):
        offset = (page - 1) * 30
        returl = self.format_url(base, pagination.replace('<page>', str(offset)))
        return returl

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        for scene in jsondata['hits']['hits']:
            item = self.init_scene()

            item['id'] = scene['_source']['id']

            item['title'] = self.cleanup_title(scene['_source']['title'])
            item['description'] = self.cleanup_description(scene['_source']['description'])

            item['date'] = self.parse_date(scene['_source']['publishedDate']).strftime('%Y-%m-%d')
            if item['date'] <= datetime.now().strftime('%Y-%m-%d'):
                if self.check_item(item, self.days):
                    image = self.format_link(response, scene['_source']['img']).replace(" ", "%20")
                    test_image = image.replace("shared/med.jpg", "shared/hi.jpg")
                    try:
                        response = requests.head(test_image, allow_redirects=False, timeout=5)
                        status = response.status_code

                        if status == 200:
                            item['image'] = test_image
                        else:
                            item['image'] = image
                    except requests.RequestException:
                        item['image'] = image

                    item['performers'], item['performers_data'] = self.parse_model(scene['_source']['models'])

                    item['tags'] = []
                    if 'tags' in scene['_source']:
                        item['tags'] = list(map(lambda x: self.cleanup_title(x), scene['_source']['tags']))

                    if "videoDuration" in scene['_source'] and scene['_source']['videoDuration']:
                        item['duration'] = str(int(scene['_source']['videoDuration']) * 60)

                    if "videoTrailer" in scene['_source'] and scene['_source']['videoTrailer']:
                        item['trailer'] = self.format_link(response, scene['_source']['videoTrailer']).replace(" ", "%20")

                    if "mylf" in meta['pagination']:
                        item['url'] = f"https://www.mylf.com/movies/{scene['_source']['id']}"
                        item['parent'] = "MyLF"
                    if "freeuse" in meta['pagination']:
                        item['url'] = f"https://www.freeuse.com/movies/{scene['_source']['id']}"
                        item['parent'] = "Teamskeet"
                    if "familybundle" in meta['pagination']:
                        item['url'] = f"https://www.familystrokes.com/movies/{scene['_source']['id']}"
                        item['parent'] = "Teamskeet"
                    if "sau_network" in meta['pagination']:
                        item['url'] = f"https://www.sayuncle.com/movies/{scene['_source']['id']}"
                        item['parent'] = "Say Uncle"                        
                    if "swap_bundle" in meta['pagination']:
                        item['url'] = f"https://www.swappz.com/movies/{scene['_source']['id']}"
                        item['parent'] = "Teamskeet"    
                    else:
                        item['url'] = f"https://www.teamskeet.com/movies/{scene['_source']['id']}"
                        item['parent'] = "Teamskeet"

                    item['site'] = scene['_source']['site']['name']
                    item['network'] = "Teamskeet"

                    yield item

    def parse_model(self, models):
        local_run = self.settings.get('local')
        show_blob = self.settings.get('showblob')
        force_update = self.settings.get('force_update')
        if force_update:
            force_update = True
        force_fields = self.settings.get('force_fields')
        if force_fields:
            force_fields = force_fields.split(",")

        performers = []
        performers_data = []
        for perf in models:
                if " " not in perf['name']:
                    perf_name = perf['name'] + str(perf['id'])
                else:
                    perf_name = perf['name']

                performers.append(perf_name)
                perf_data = {}
                perf_data['site'] = "Teamskeet"
                perf_data['name'] = perf_name
                perf_data['extra'] = {}
                perf_data['extra']['gender'] = string.capwords(perf['gender'])

                if "bio" in perf and perf['bio']:
                    if "weight" in perf['bio'] and perf['bio']['weight']:
                        weight_kg = int(round(float(perf['bio']['weight']) / 2.20462))
                        perf_data['extra']['weight'] = str(weight_kg) + "kg"

                    if "birthdate" in perf['bio'] and perf['bio']['birthdate']:
                        birthdate = re.search(r'(\d{4}-\d{2}-\d{2})', perf['bio']['birthdate'])
                        if birthdate:
                            perf_data['extra']['birthday'] = birthdate.group(1)

                    if "about" in perf['bio'] and perf['bio']['about']:
                        about_perf = perf['bio']['about']

                        measurements = re.search(r'Measurements: (\d+[A-Z]+?-\d+-\d+)', about_perf)
                        if measurements:
                            perf_data['extra']['measurements'] = measurements.group(1).replace(" ", "")

                        hair_color = re.search(r'Hair Color: (\w+)\\n', about_perf)
                        if hair_color:
                            perf_data['extra']['hair_color'] = hair_color.group(1)

                        nationality = re.search(r'Nationality: (\w+)\\n', about_perf)
                        if nationality:
                            perf_data['extra']['nationality'] = nationality.group(1)

                        ethnicity = re.search(r'Ethnicity: (\w+)\\n', about_perf)
                        if ethnicity:
                            perf_data['extra']['ethnicity'] = ethnicity.group(1)

                        piercings = re.search(r'Piercings: (\w+)\\n', about_perf)
                        if piercings:
                            perf_data['extra']['piercings'] = piercings.group(1)

                if "modelBio" in perf and perf['modelBio']:
                    perf_data['bio'] = perf['modelBio']

                if "img" in perf and perf['img']:
                    perf_data['image'] = perf['img']
                    if (not force_update or (force_update and "performers" in force_fields)) and (not local_run or (local_run and show_blob)):
                        perf_data['image_blob'] = self.get_image_blob_from_link(perf_data['image'])

                performers_data.append(perf_data)

        return performers, performers_data
