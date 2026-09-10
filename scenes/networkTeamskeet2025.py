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
    page_size = 30

    # tours-store is an open Elasticsearch cluster - /_cat/aliases?format=json lists every
    # index it serves.  Scene ids are tour specific, so an alias' ids only resolve on the
    # domain that alias backs.  Between them these cover the whole catalogue.
    #   [alias, tour base url, parent, sites to take from this alias (None = all of them)]
    endpoints = [
        ['ts_network', 'https://www.teamskeet.com', 'Teamskeet', None],
        ['mylf_bundle', 'https://www.mylf.com', 'MyLF', None],
        ['sau_network', 'https://www.sayuncle.com', 'Say Uncle', None],
        # brand tours carrying series that none of the three network indexes hold
        ['freeusebundle', 'https://www.freeuse.com', 'Teamskeet', ['FreeUse Milf', 'UsePOV', 'FreeUse Singles']],
        ['mylf_ppv', 'https://www.pervprincipal.com', 'MyLF', None],
        ['familybundle', 'https://www.familystrokes.com', 'Teamskeet', ['Ask Your Mother', 'Family Strokes Features']],
        ['swap_bundle', 'https://www.swappz.com', 'Teamskeet', ['Swappz Features', 'Swappz Singles']],
        # series that have no public page on any tour - the teamskeet.com urls built for these
        # 404, they are here for the metadata
        ['reptyle_bundle', 'https://www.teamskeet.com', 'Teamskeet', ['Reptyle Selects', 'Extras', 'TeamSkeet X Mr Lucky POV', 'TeamSkeet X Spizoo', 'TeamSkeet X Raw Attack']],
        ['test_fos', 'https://www.teamskeet.com', 'Teamskeet', ['Reptyle Features']],
        ['pervbundle', 'https://www.teamskeet.com', 'Teamskeet', ['Pervz Singles', 'Pervz Features', 'Charmed']],
        ['network_mylf', 'https://www.teamskeet.com', 'MyLF', ['Milf Taxi']],
        ['sau_dkl', 'https://www.teamskeet.com', 'Say Uncle', ['Dakota Lovell']],
    ]

    # site names the api uses that we submit under a different name
    site_names = {
        'Extras': 'Reptyle Extras',
    }

    selector_map = {
        'external_id': r'',
        'pagination': '/ts_network/_search?q=(type:video AND isUpcoming:false)&sort=publishedDate:desc&size=30&from=<page>',
        'type': 'Scene',
    }

    async def start(self):
        ip = requests.get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        yield scrapy.Request(url=self.format_url(self.start_url, '/mylf_bundle/_search?q=(type:series)&size=100'),
                             callback=self.parse_mylf_sites,
                             headers=self.headers,
                             cookies=self.cookies)

    def parse_mylf_sites(self, response):
        # mylf_bundle is the index behind mylf.com.  For every site it carries it holds that
        # site's complete run, and ts_network carries the same scenes under the same ids, so
        # those sites are excluded from the ts_network pass and taken with a mylf.com url
        mylf_sites = sorted(hit['_source']['name'] for hit in response.json()['hits']['hits'])
        print('MyLF tour sites: ' + str(len(mylf_sites)))

        for alias, base, parent, sites in self.endpoints:
            pagination = self.get_pagination(alias, sites, mylf_sites if alias == 'ts_network' else None)
            meta = {'page': self.page, 'pagination': pagination, 'base': base, 'parent': parent}
            yield scrapy.Request(url=self.get_next_page_url(self.start_url, pagination, self.page),
                                 callback=self.parse,
                                 meta=meta,
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_pagination(self, alias, sites=None, exclude=None):
        # the site filter goes in the query rather than being dropped while parsing, so that a
        # page never comes back empty for any reason other than reaching the end of the index
        query = 'type:video AND isUpcoming:false'
        if sites:
            query = query + ' AND site.name.keyword:(' + ' OR '.join(f'"{site}"' for site in sites) + ')'
        if exclude:
            query = query + ' AND NOT site.name.keyword:(' + ' OR '.join(f'"{site}"' for site in exclude) + ')'

        return f"/{alias}/_search?q=({query})&sort=publishedDate:desc&size=<size>&from=<page>"

    def parse(self, response, **kwargs):
        meta = self.copy_meta(response)
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
        offset = (page - 1) * self.page_size
        pagination = pagination.replace('<page>', str(offset)).replace('<size>', str(self.page_size))
        returl = self.format_url(base, pagination)
        return returl

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        jsondata = response.json()
        for scene in jsondata['hits']['hits']:
            site = scene['_source']['site']['name']

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
                        head = requests.head(test_image, allow_redirects=False, timeout=5)
                        status = head.status_code

                        if status == 200:
                            item['image'] = test_image
                        else:
                            item['image'] = image
                    except requests.RequestException as e:
                        item['image'] = image

                    item['performers'], item['performers_data'] = self.parse_model(scene['_source']['models'])

                    item['tags'] = []
                    if 'tags' in scene['_source']:
                        item['tags'] = list(map(lambda x: self.cleanup_title(x), scene['_source']['tags']))

                    if "videoDuration" in scene['_source'] and scene['_source']['videoDuration']:
                        item['duration'] = str(int(scene['_source']['videoDuration']) * 60)

                    if "videoTrailer" in scene['_source'] and scene['_source']['videoTrailer']:
                        item['trailer'] = self.format_link(response, scene['_source']['videoTrailer']).replace(" ", "%20")

                    item['url'] = f"{meta['base']}/movies/{scene['_source']['id']}"
                    item['parent'] = meta['parent']

                    item['site'] = self.site_names.get(site, site)
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
                    # id used to be the numeric key but is a slug now, so appending it turned
                    # single word names into "Broganbrogan" - itemId is the numeric one
                    perf_name = perf['name'] + str(perf['itemId'])
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
