import re
import json
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePacopacomamaSpider(BaseSceneScraper):
    name = 'Pacopacomama'
    network = 'Pacopacomama'
    parent = 'Pacopacomama'
    site = 'Pacopacomama'

    start_urls = [
        'https://en.pacopacomama.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'',
        'trailer': '',
        'pagination': '/dyn/phpauto/movie_lists/list_newest_%s.json'
    }

    def get_next_page_url(self, base, page):
        page = (page - 1) * 50
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['Rows']
        for scene in jsondata:
            item = SceneItem()
            if scene['TitleEn']:
                item['title'] = scene['TitleEn']
            else:
                item['title'] = f"Pacopacomama: #{scene['MovieID']}"
            item['description'] = ''
            if scene['DescEn'] and len(scene['DescEn']) > 5:
                item['description'] = scene['DescEn'].replace("\r", "").replace("\n", "").replace("\t", "").strip()
            item['date'] = self.parse_date(scene['Release'], date_formats=['%Y-%m-%d']).isoformat()
            item['id'] = scene['MovieID']
            item['url'] = f"https://en.pacopacomama.com/movies/{item['id']}/"
            item['image'] = scene['ThumbHigh']
            item['image_blob'] = ''
            item['trailer'] = ''
            if "SampleFiles" in scene and scene['SampleFiles']:
                for trailer in scene['SampleFiles']:
                    if "1080p" in trailer['FileName']:
                        item['trailer'] = trailer['URL']
                if not item['trailer']:
                    for trailer in scene['SampleFiles']:
                        if "720p" in trailer['FileName']:
                            item['trailer'] = trailer['URL']
                if not item['trailer']:
                    for trailer in scene['SampleFiles']:
                        if "480p" in trailer['FileName']:
                            item['trailer'] = trailer['URL']
            item['tags'] = []
            for tag in scene['UCNAMEEn']:
                if not re.search(r'(\d+)p$', tag) and not re.search(r'(\d+)fps$', tag):
                    item['tags'].append(string.capwords(tag))
            item['performers'] = []
            for performer in scene['ActressesEn']:
                item['performers'].append(string.capwords(performer))
            item['site'] = 'Pacopacomama'
            item['parent'] = 'Pacopacomama'
            item['network'] = 'Pacopacomama'
            yield item
