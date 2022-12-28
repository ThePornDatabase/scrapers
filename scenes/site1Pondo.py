import json
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class Site1PondoSpider(BaseSceneScraper):
    name = '1Pondo'

    start_urls = [
        'https://www.10musume.com',
        'http://en.1pondo.tv',
        'https://www.pacopacomama.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/dyn/phpauto/movie_lists/list_newest_%s.json',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 50)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        jsondata = json.loads(response.text)
        jsondata = jsondata['Rows']
        for scene in jsondata:
            item = SceneItem()
            item['id'] = scene['MovieID']
            if "10musume" in response.url:
                item['site'] = "10Musume"
                item['parent'] = "10Musume"
                item['url'] = f"https://en.10musume.tv/movies/{item['id']}/"
            if "pondo" in response.url:
                item['site'] = "1Pondo"
                item['parent'] = "1Pondo"
                item['url'] = f"https://en.1pondo.tv/movies/{item['id']}/"
            if "pacopacomama" in response.url:
                item['site'] = "Pacopacomama"
                item['parent'] = "Pacopacomama"
                item['url'] = f"https://www.pacopacomama.com/movies/{item['id']}/"
            item['network'] = "D2Pass"
            item['type'] = "Scene"

            item['title'] = self.cleanup_title(scene['TitleEn'])
            if scene['DescEn']:
                item['description'] = self.cleanup_description(scene['DescEn'])
            else:
                item['description'] = ""
            item['date'] = self.parse_date(scene['Release']).isoformat()
            item['image'] = scene['ThumbHigh']
            item['image'] = item['image'].replace("///", "//")
            if "https://moviepages" in item['image']:
                item['image'] = self.format_link(response, item['image'].replace("https://", ""))
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['duration'] = scene['Duration']
            item['performers'] = scene['ActressesEn']
            item['tags'] = scene['UCNAMEEn']
            if "Asian" not in item['tags']:
                item['tags'].append("Asian")
            for trailer in scene['SampleFiles']:
                item['trailer'] = trailer['URL']
            yield self.check_item(item, self.days)
