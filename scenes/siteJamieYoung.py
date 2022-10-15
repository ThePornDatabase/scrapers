import re
import html
import json
import requests
import unidecode
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteJamieYoungSpider(BaseSceneScraper):
    name = 'JamieYoung'
    network = "Jamie Young"
    parent = "Jamie Young"
    site = "Jamie Young"

    custom_settings = {'CONCURRENT_REQUESTS': '1',
                       'AUTOTHROTTLE_ENABLED': 'True',
                       'AUTOTHROTTLE_DEBUG': 'False',
                       'DOWNLOAD_DELAY': '2',
                       'CONCURRENT_REQUESTS_PER_DOMAIN': '1',
                       }

    start_urls = [
        'https://jamie-young.com',
    ]

    headers = {
        'age_gate': '18',
        'wpml_browser_redirect_test': '0',
    }

    selector_map = {
        'performers': '//span[@itemprop="actors"]/a/text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/index.php/wp-json/wp/v2/video_skrn?page=%s&per_page=10'
    }

    def get_scenes(self, response):

        reqheaders = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
        jsondata = json.loads(response.text)
        for scene in jsondata:
            item = SceneItem()
            item['id'] = scene['id']
            item['url'] = scene['link']
            item['date'] = scene['date']
            item['title'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', scene['title']['rendered'])).replace("\n", " ").strip())

            item['image'] = ''
            item['image_blob'] = ''
            link = f"https://jamie-young.com/index.php/wp-json/wp/v2/media?parent={item['id']}"
            req = requests.get(link, headers=reqheaders, timeout=10)
            if req and len(req.text) > 5:
                imagelist = json.loads(req.text)
                item['image'] = imagelist[0]['guid']['rendered']
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['performers'] = []
            link = f"https://jamie-young.com/index.php/wp-json/wp/v2/video-cast?post={item['id']}"
            req = requests.get(link, headers=reqheaders, timeout=10)
            if req and len(req.text) > 5:
                performerlist = json.loads(req.text)
                for performer in performerlist:
                    if performer['name'].lower() == "jamie":
                        item['performers'].append("Jamie Young")
                    else:
                        item['performers'].append(self.cleanup_title(performer['name']))
            if "Jamie Young" not in item['performers']:
                item['performers'].append("Jamie Young")

            item['description'] = scene['content']['rendered']
            if item['description']:
                item['description'] = unidecode.unidecode(html.unescape(re.sub('<[^<]+?>', '', item['description'])).replace("\n", " ").strip())
                if 'vc_raw_html' in item['description']:
                    item['description'] = ''
                if ".arm_" in item['description']:
                    item['description'] = re.sub(r'\.arm_.*\}', '', item['description'])
                    item['description'] = item['description'].replace('\n', '').replace('\r', '').replace('\t', '').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ')
                    # ~ print(f"Title: {item['title']}    Desc: {item['description']}")
                if "Timestamps" in item['description']:
                    timestamps = re.search(r'Timestamps?:?(.*)', item['description']).group(1)
                    item['description'] = re.search(r'(.*)Timestamp', item['description']).group(1)
                    timestamps = re.sub(r'(\d)-(\d)', r'\1 - \2', timestamps)
                    timestamps = re.sub(r' (\d{1,2}:\d{2}) ', r' 00:\1 ', timestamps)
                    timestamps = re.sub(r' (\d{1,2}:\d{2}) ', r' 00:\1 ', timestamps)
                    timestamps = re.sub(r' (\d:\d{2}:\d{2}) ', r' 0\1 ', timestamps)
                    timestamps = re.findall(r'[a-zA-Z]+ ?[a-zA-Z]+?:\s+?\d{2}:\d{2}:\d{2} - \d{2}:\d{2}:\d{2}', timestamps)
                    item['markers'] = []
                    for timestamp in timestamps:
                        marker = {}
                        stamps = re.search(r'([a-zA-Z]+ ?[a-zA-Z]+?):\s+?(\d{2}:\d{2}:\d{2}) - (\d{2}:\d{2}:\d{2})', timestamp)
                        marker['name'] = self.cleanup_title(stamps.group(1))
                        marker['start'] = self.get_second(stamps.group(2))
                        marker['end'] = self.get_second(stamps.group(3))
                        item['markers'].append(marker)
                    if len(item['markers']):
                        item['markers'] = self.clean_markers(item['markers'])

            tags = []
            link = f"https://jamie-young.com/index.php/wp-json/wp/v2/video-genres?post={item['id']}"
            req = requests.get(link, headers=reqheaders, timeout=10)
            if req and len(req.text) > 5:
                taglist = []
                taglist = json.loads(req.text)
                for tag in taglist:
                    tags.append(tag['name'])
            item['tags'] = tags

            item['trailer'] = ""
            item['site'] = "Jamie Young"
            item['parent'] = "Jamie Young"
            item['network'] = "Jamie Young"

            if "Teaser" not in item['tags'] and "teaser" not in item['title'].lower():
                yield self.check_item(item, self.days)

    def get_second(self, marker):
        marker = re.search(r'(\d{2}):(\d{2}):(\d{2})', marker)
        hours = int(marker.group(1))
        minutes = int(marker.group(2))
        seconds = int(marker.group(3))

        return str((hours * 3600) + (minutes * 60) + seconds)

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
                            if (test_end > mark_start) and (mark_end > test_end):
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
