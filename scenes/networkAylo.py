import re
import string
from urllib.parse import urlencode
import datetime
import scrapy
import requests
from slugify import slugify
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem

## To do list
# - Add a cache check against local TPDB for performer data to avoid re-fetching
# - Add a cache check against local TPDB for scene data to avoid re-fetching, for older scenes
# - Use local tpdb database to get site mappings from exported csv


class NetworkAyloSpider(BaseSceneScraper):
    name = 'NetworkAylo'

    start_urls = [
        'https://www.adultmobile.com',
        'https://www.brazzers.com',
        'https://www.bangbros.com',
        'https://www.babes.com',
        'https://www.biempire.com',
        'https://www.bromo.com',
        'https://www.dancingbear.com',
        'https://www.deviante.com',
        'https://www.czechhunter.com/',
        'https://www.digitalplayground.com',
        'https://www.dilfed.com',
        'https://www.doghousedigital.com',
        'https://www.gilfed.com', # API responses from this site are borked
        'https://www.erito.com',
        'https://www.fakehub.com',
        'https://www.familysinners.com',
        'https://www.guyselector.com',
        'https://www.iconmale.com',
        'https://www.letsdoeit.com',
        'https://www.men.com',
        'https://www.metrohd.com',
        'https://www.milehighmedia.com',
        'https://www.milfed.com',
        'https://www.mofos.com',
        'https://www.mypervyfamily.com',
        'https://www.nextdoorhobby.com',
        'https://www.noirmale.com',
        'https://www.propertysex.com',
        'https://www.realitydudesnetwork.com',
        'https://www.realitykings.com',
        'https://www.realityjunkies.com',
        'https://www.seancody.com',
        'https://www.sexselector.com',
        'https://www.sexyhub.com',
        'https://www.squirted.com',
        'https://www.sweetheartvideo.com',
        'https://www.sweetsinner.com',
        'https://www.thegayoffice.com',
        'https://www.touchmywife.com',
        'https://www.transangelsnetwork.com',
        'https://www.transharder.com',  # Seems to be the same as TransAngels, but some additional
        'https://www.transsensual.com',  # Seems to be the same as TransAngels, but some additional
        'https://www.trueamateurs.com',
        'https://www.tube8vip.com',
        'https://www.twistys.com',
        'https://virtualporn.com',
        'https://www.voyr.com',
        'https://www.whynotbi.com',
    ]

    selector_map = {
        'external_id': 'scene\\/(\\d+)'
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.performer_cache = {}
      
        # Site abbreviation mappings: abbreviation -> (full_name, parent)
        self.site_mappings = {
            'fmf': ('Forgive Me Father', 'Deviante'),
            'sw': ('Sex Working', 'Deviante'),
            'pdt': ('Pretty Dirty Teens', 'Deviante'),
            'lha': ('Love Her Ass', 'Deviante'),
            'es': ('Erotic Spice', 'Deviante'),
            'dlf': ('DILFed', 'DILFed'),
            'rks': ('RK Shorts', 'Reality Kings'),
            'vrt': ('VR Temptation', 'VR Temptation'),
            'zzvr': ('Brazzers VR', 'Brazzers VR'),
        }

        # Sites that will use spartanId instead of Id
        self.spartan_id_sites = ['touchmywife', 'filthyfamily', 'mypervyfamily']
        
        # URL text mappings: network -> url_text, will override the default of 'scene'
        self.url_text_map = {
            'brazzers': 'video',
            'bangbros': 'video',
            'mypervyfamily': 'video',
            'touchmywife': 'video',
            'men': 'sceneid',
        }
        
        # Brands to skip
        self.skip_brands = ['spicevids', 'offline', 'branding', 'pornportal']

        # Site date restrictions: [site_name, minimum_date]
        self.site_date_restrictions = [
            ['touchmywife', '2025-11-01'],
            ['mypervyfamily', '2025-11-01'],
            ['cockyboys', '2025-11-01'],
            ['filthyfamily', '2025-08-01'],
            ['mygf', '2025-08-01'],
            ['baitbus', '2025-07-01'],
            ['virtualporn', '2024-07-01'],
            ['mydirtyvault', '2024-07-01'],
            ['sexselector', '2024-07-01'],
            ['brownbunnies', '2023-09-01'],
        ]

        # Brand date restrictions: [brand_name, minimum_date]
        self.brand_date_restrictions = [
            ['bangbros', '2023-07-01'],
        ]

    async def start(self):
        # if self.limit_pages == 1:
        #     self.limit_pages = 5
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'url': url})

    def parse(self, response):
        token = self.get_token(response)
        if not token:
            print(f"*** No instance_token issued by {response.meta['url']}, skipping site")
            return

        headers = {
            'instance': token,
            'origin': response.meta['url'],
            'referer': response.meta['url'],
        }

        response.meta['headers'] = headers
        response.meta['limit'] = 25
        # ~ response.meta['page'] = -1
        response.meta['page'] = self.page - 1
        response.meta['url'] = response.url

        return self.get_next_page(response)

    def get_next_page(self, response):
        meta = self.copy_meta(response)

        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        query = {
            'adaptiveStreamingOnly': 'false',
            'dateReleased': f"<{tomorrow}",
            'orderBy': '-dateReleased',
            'type': 'scene',
            'limit': meta['limit'],
            'offset': (meta['page'] * meta['limit']),
        }
        meta = {
            'url': response.meta['url'],
            'headers': response.meta['headers'],
            'page': (response.meta['page'] + 1),
            'limit': response.meta['limit']
        }

        print('NEXT PAGE: ' + str(meta['page']))

        link = 'https://site-api.project1service.com/v2/releases?' + \
            urlencode(query)
        return scrapy.Request(url=link, callback=self.get_scenes, headers=response.meta['headers'], meta=meta, dont_filter=True)

    def check_restrictions(self, scene, item):
        parse_scene = True
        check_site = re.sub(r'[^a-z0-9]', '', item['site'].lower())

        for site_name, min_date in self.site_date_restrictions:
            if check_site == site_name and item['date'] < min_date:
                parse_scene = False
                break

        for brand_name, min_date in self.brand_date_restrictions:
            if brand_name.lower() in scene['brand'].lower() and item['date'] < min_date:
                parse_scene = False
                break

        if check_site in ['killergram']:
            parse_scene = False
        return parse_scene

    def clean_markers(self, markers):
        markers = sorted(markers, key=lambda k: (k['name'].lower(), int(k['start']), int(k['end'])))
        marker_final = []
        marker_work = markers.copy()
        marker2_work = markers.copy()
        for test_marker in marker_work:
            if test_marker in markers:
                for marker in marker2_work:
                    if test_marker['name'].lower().strip() == marker['name'].lower().strip():
                        test_start = int(test_marker['start'])
                        mark_start = int(marker['start'])
                        test_end = int(test_marker['end'])
                        mark_end = int(marker['end'])
                        if test_start < mark_start or test_start == mark_start:
                            test1 = mark_start - test_end
                            test2 = mark_start - test_start
                            if 0 < test1 < 60 or 0 < test2 < 60 or test1 == 0 or test2 == 0:
                                if mark_end > test_end:
                                    test_marker['end'] = marker['end']
                                    if marker in markers:
                                        markers.remove(marker)
                            if test_end > mark_start and mark_end > test_end:
                                test_marker['end'] = marker['end']
                                if marker in markers:
                                    markers.remove(marker)
                            if test_start < mark_start and (mark_end < test_end or test_end == mark_end):
                                if marker in markers:
                                    markers.remove(marker)
                marker2_work = markers.copy()

                if test_marker in markers:
                    marker_final.append(test_marker)
                    markers.remove(test_marker)
        marker_final = sorted(marker_final, key=lambda k: (int(k['start']), int(k['end'])))
        return marker_final

    def get_image(self, scene):
        if 'images' not in scene:
            return None
            
        image_arr = []
        if 'card_main_rect' in scene['images'] and len(
                scene['images']['card_main_rect']):
            image_arr = scene['images']['card_main_rect']
        elif 'poster' in scene['images'] and len(scene['images']['poster']):
            image_arr = scene['images']['poster']

        # Sizes in order: largest to smallest
        sizes = ['xx', 'xl', 'lg', 'md', 'sm']
        
        # Check all indices for each size to guarantee largest available
        for size in sizes:
            for index in image_arr:
                image = image_arr[index]
                if isinstance(image, dict) and size in image:
                    return image[size]['url']
        
        return None

    def get_performer_name(self, model):
        """Build performer name, adding ID if single word"""
        performer = string.capwords(model['name'])
        if " " not in performer:
            performer = f"{performer} {model['id']}"
        return performer

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.json()['result']
        skipped_count = 0
        
        local_run = self.settings.get('local')
        show_blob = self.settings.get('showblob')
        force_update = self.settings.get('force_update')
        if force_update:
            force_update = True
        force_fields = self.settings.get('force_fields')
        if force_fields:
            force_fields = force_fields.split(",")

        for scene in scenes:
            brand_lower = scene['brand'].lower().strip()
            if any(skip in brand_lower for skip in self.skip_brands):
                skipped_count = skipped_count + 1
        print(f"Current Page; {meta['page']}:  Number of scenes found: {len(scenes)}, {skipped_count} scenes skipped.")

        for scene in scenes:
            brand_lower = scene['brand'].lower().strip()
            if not any(skip in brand_lower for skip in self.skip_brands):

                # Handle missing brandMeta early
                if not scene.get('brandMeta') or 'displayName' not in scene['brandMeta']:
                    if scene.get('groups') and len(scene['groups']) > 0:
                        scene['brandMeta'] = {
                            'displayName': scene['groups'][0]['displayName']
                        }
                    else:
                        continue  # Skip if no valid brand info
                
                item = SceneItem()
                item['date'] = self.parse_date(scene['dateReleased']).strftime('%Y-%m-%d')

                if 'title' in scene:
                    item['title'] = scene['title']
                else:
                    item['title'] = item['site'] + ' ' + self.parse_date(scene['dateReleased']).strftime('%b/%d/%Y')

                ## Get Site, Network, Parent, URL
                if scene['collections'] and len(scene['collections']):
                    item['site'] = scene['collections'][0]['name']
                else:
                    item['site'] = scene['brandMeta']['displayName']
                item = self.get_site_url_info(scene, item)
                check_site = re.sub(r'[^a-z0-9]', '', item['site'].lower())
                ##

                item['id'] = scene['id']
                # Sites that use spartanId instead of regular id
                if "letsdoeit" in scene['brand'].lower().strip() or check_site in self.spartan_id_sites:
                    item['id'] = scene['spartanId']

                if self.check_item(item, self.days):
                    item['trailer'] = self.get_trailer(scene)
                    if not item['trailer']:
                        item['trailer'] = ''

                    if self.check_restrictions(scene, item):
                        item['description'] = scene.get('description', '')

                        item['image'] = self.get_image(scene)
                        if (not force_update or (force_update and "image" in force_fields)) and (not local_run or (local_run and show_blob)):
                            item['image_blob'] = self.get_image_blob_from_link(item['image'])
                        else:
                            item['image_blob'] = None

                        self.process_performers(scene, item, meta)
                        self.process_tags(scene, item, response)
                        
                        videos = scene.get('videos', {})
                        if isinstance(videos, dict):
                            duration = videos.get('mediabook', {}).get('length')
                            item['duration'] = duration if duration else ''
                        else:
                            item['duration'] = ''

                        item['markers'] = []
                        if "timeTags" in scene:
                            for timetag in scene['timeTags']:
                                timestamp = {
                                    'name': self.cleanup_title(timetag['name']),
                                    'start': str(timetag['startTime']),
                                    'end': str(timetag['endTime'])
                                }
                                item['markers'].append(timestamp)
                                item['tags'].append(timestamp['name'])
                            item['markers'] = self.clean_markers(item['markers'])
                            item['tags'] = list(map(lambda x: string.capwords(x.strip()), set(item['tags'])))

                        yield item

                        # if "Sexy Private Investigator" in item['title']:
                        #     print(scene)

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            yield self.get_next_page(response)

    def get_site_url_info(self, scene, item):

        ## Network rewrites
        net_check = re.sub(r'[^a-z0-9]', '', scene['brandMeta']['displayName'].lower())
        
        # Special network rewrites
        if net_check == "bigstr":
            scene['brandMeta']['displayName'] = "Czech Hunter"
            item['site'] = "Czech Hunter"
            net_check = "czechhunter"
        if net_check == "metro":
            scene['brandMeta']['displayName'] = "MetroHD"
            item['site'] = "MetroHD"
            if "groups" in scene:
                for group in scene['groups']:
                    if group.get('id') != 167 and "Report" not in group['name']:
                        item['site'] = group['name']
                        break
            net_check = "metrohd"            
        if net_check == "whynotby":
            scene['brandMeta']['displayName'] = "WhyNotBi"
            item['site'] = "WhyNotBi"
            net_check = "whynotbi"                 
        elif net_check == "leviproductions":
            scene['brandMeta']['displayName'] = item['site']
            net_check = re.sub(r'[^a-zA-Z0-9]', '', item['site']).lower()
        elif net_check == "brazzersplus":
            item['site'] = "Brazzers Plus"
            scene['brandMeta']['displayName'] = "Brazzers"
            net_check = "brazzers"
        elif net_check in ["milehighmedia", "bangbros"] and scene.get('sexualOrientation', '').lower().strip() in ["gay", "trans"]:
            scene['brandMeta']['displayName'] = item['site']
            net_check = re.sub(r'[^a-zA-Z0-9]', '', item['site']).lower()

        item['network'] = "Mindgeek"
        item['parent'] = scene['brandMeta']['displayName']

        if net_check == "leviproductions":
            net_check = re.sub(r'[^a-zA-Z0-9]', '', item['site']).lower()

        # Get URL text from mapping, default to "scene"
        url_text = self.url_text_map.get(net_check, "scene")
            
        item['url'] = f"https://www.{net_check}.com/{url_text}/{scene['id']}/{slugify(item['title'])}"

        # Apply site abbreviation mappings
        if item['site'] in self.site_mappings:
            item['site'], item['parent'] = self.site_mappings[item['site']]
        elif item['site'] in ["NextDoorHobby", 'ndhe']:
            item['site'] = "Next Door Hobby"
            item['parent'] = "Next Door Hobby"
            for group in scene.get('groups', []):
                if group.get('id') == 12201:
                    item['site'] = "Next Door Hobby (German)"
                    break
        
        return item

    def get_token(self, response):
        """Only the first Set-Cookie header used to be searched, but instance_token
        is rarely the first one the sites send -- brazzers puts it second and
        babes/realitykings/mofos/seancody third -- so the match returned None and
        .group(1) aborted the whole site.  Every header is scanned now."""
        for header in response.headers.getlist('Set-Cookie'):
            token = re.search('instance_token=(.+?);', header.decode("utf-8"))
            if token:
                return token.group(1)
        return None

    def get_trailer(self, scene):
        if 'videos' not in scene:
            return None
        videos = scene['videos']
        if not isinstance(videos, dict):
            return None
        for index in videos:
            trailer = videos[index]
            for size in ['720p', '576p', '480p', '360p', '320p', '1080p', '4k']:
                if size in trailer.get('files', {}):
                    return trailer['files'][size]['urls']['view']
        return None

    def parse_performer(self, model_data, site, url):
        
        local_run = self.settings.get('local')
        show_blob = self.settings.get('showblob')
        force_update = self.settings.get('force_update')
        if force_update:
            force_update = True
        force_fields = self.settings.get('force_fields')
        if force_fields:
            force_fields = force_fields.split(",")

        model_data = model_data['result']
        perf = {}

        perf['name'] = string.capwords(model_data['name'])
        if " " not in perf['name']:
            perf['name'] = f"{perf['name']} {model_data['id']}"

        perf['site'] = site
        if "gender" in model_data and model_data['gender']:
            perf['extra'] = {}
            perf['extra']['gender'] = model_data['gender']

        sizes = ['lg', 'xl', 'md', 'sm', 'xs']
        primary_keys = ['card_main_rect', 'master_profile', 'profile']
        image = None

        if "images" in model_data and model_data['images']:
            for key in primary_keys:
                section = model_data['images'].get(key)
                if section and "0" in section:
                    mod_images = section["0"]
                    for size in sizes:
                        if size in mod_images and 'url' in mod_images[size]:
                            image = mod_images[size]['url']
                            break
                if image:
                    break

        if image:
            perf['image'] = image
            if (not force_update or (force_update and "performers" in force_fields)) and (not local_run or (local_run and show_blob)):
                perf['image_blob'] = self.get_image_blob_from_link(image)
            else:
                perf['image_blob'] = None
        
        baseurl = re.search(r'(https://.*?/)', url).group(1)
        url_text = "model"
        if "men.com" in baseurl or "fakehub" in baseurl or "sexyhub" in baseurl:
            url_text = "modelprofile"
        if "brazzers.com" in baseurl:
            url_text = "pornstar"

        perf['url'] = f"{baseurl}{url_text}/{model_data['id']}/{slugify(perf['name'])}"

        return perf

    def process_performers(self, scene, item, meta):
        """Process and cache performer data for a scene"""
        item['performers'] = []
        item['performers_data'] = []

        if "actors" not in scene or not scene['actors']:
            return

        for model in scene['actors']:
            performer = self.get_performer_name(model)
            
            # Check cache first
            if model['id'] in self.performer_cache:
                performer_extra = self.performer_cache[model['id']].copy()
            else:
                # Fetch and cache performer data
                req = requests.get(f"https://site-api.project1service.com/v1/actors/{model['id']}", headers=meta['headers'])
                if req and req.ok:
                    model_data = req.json()
                    performer_extra = self.parse_performer(model_data, item['site'], item['url'])
                    # Cache the performer data
                    self.performer_cache[model['id']] = performer_extra.copy()
                else:
                    performer_extra = {
                        'name': performer,
                        'site': item['site']
                    }
                    if "gender" in model and model['gender']:
                        performer_extra['extra'] = {'gender': model['gender']}

            item['performers_data'].append(performer_extra)
            item['performers'].append(performer)

    def process_tags(self, scene, item, response):
        """Process and add tags from scene data"""
        item['tags'] = [tag['name'] for tag in scene.get('tags', [])]
        
        # Add sexual orientation tags
        orientation = scene.get('sexualOrientation', '').lower()
        if orientation == "gay":
            item['tags'].append('Gay')
        elif orientation == "trans":
            item['tags'].append('Trans')
        
        # Add VR tag if applicable
        if scene.get('isVR') or "virtualporn" in response.url:
            item['tags'].append("VR")