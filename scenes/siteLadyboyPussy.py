import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem
true = True
false = False


class SiteLadyboyPussySpider(BaseSceneScraper):
    name = 'LadyboyPussy'
    network = 'Ladyboy Pussy'
    parent = 'Ladyboy Pussy'
    site = 'Ladyboy Pussy'

    start_urls = [
        'https://www.ladyboypussy.com',
    ]

    headers = {'X-NATS-cms-area-id': '3b74725d-ad01-45a1-8186-ac6be1bc1661'}
    cookies = [{"domain":"www.ladyboypussy.com","expirationDate":1761935244,"hostOnly":true,"httpOnly":false,"name":"nats_unique","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"MC4wLjkuOS4wLjAuMC4wLjA"},{"domain":"www.ladyboypussy.com","expirationDate":1764440844,"hostOnly":true,"httpOnly":false,"name":"nats","path":"/","sameSite":"unspecified","secure":false,"session":false,"storeId":"0","value":"MC4wLjkuOS4wLjAuMC4wLjA"},{"domain":"www.ladyboypussy.com","expirationDate":1764440845,"hostOnly":true,"httpOnly":false,"name":"consent","path":"/","sameSite":"lax","secure":false,"session":false,"storeId":"0","value":"true"},{"domain":".ladyboypussy.com","expirationDate":1770564759.912632,"hostOnly":false,"httpOnly":true,"name":"nats_sess","path":"/","sameSite":"lax","secure":true,"session":false,"storeId":"0","value":"d4d200fc311ad84b3f74d611ca98a2e1"},{"domain":".ladyboypussy.com","expirationDate":1764513159.912368,"hostOnly":false,"httpOnly":true,"name":"nats","path":"/","sameSite":"lax","secure":true,"session":false,"storeId":"0","value":"MC4wLjkuOS4wLjAuMC4wLjA"},{"domain":".ladyboypussy.com","expirationDate":1764513159.91249,"hostOnly":false,"httpOnly":true,"name":"nats_cookie","path":"/","sameSite":"lax","secure":true,"session":false,"storeId":"0","value":"https%253A%252F%252Fwww.ladyboypussy.com%252F"},{"domain":".ladyboypussy.com","expirationDate":1762007559.912542,"hostOnly":false,"httpOnly":true,"name":"nats_unique","path":"/","sameSite":"lax","secure":true,"session":false,"storeId":"0","value":"MC4wLjkuOS4wLjAuMC4wLjA"},{"domain":".ladyboypussy.com","expirationDate":1764513159.912587,"hostOnly":false,"httpOnly":true,"name":"nats_landing","path":"/","sameSite":"lax","secure":true,"session":false,"storeId":"0","value":"No%2BLanding%2BPage%2BURL"}]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'trailer': '',
        'external_id': r'',
        'pagination': '/index.php?section=1681&start=%s'
    }

    def get_next_page_url(self, base, page):
        index = str((int(page) -1) * 12)
        url = f"https://nats.islanddollars.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=12&start={index}&cms_area_id=3b74725d-ad01-45a1-8186-ac6be1bc1661&cms_block_id=113044&orderby=published_desc&content_type=video&status=enabled&text_search=&data_type_search=%7B%22100001%22:%22183%22%7D"
        print(url)
        return url

    def get_scenes(self, response):
        meta = response.meta
        jsondata = response.json()
        scenes = jsondata['sets']
        for scene in scenes:
            item = SceneItem()

            item['title'] = self.cleanup_title(scene['name'])
            item['description'] = scene['description']
            item['date'] = scene['added_nice']

            item['performers'] = []
            item['tags'] = []
            if "data_types" in scene and scene['data_types']:
                if "data_values" in scene['data_types'][0] and scene['data_types'][0]['data_values']:
                    for tag in scene['data_types'][0]['data_values']:
                        item['tags'].append(tag['name'])

            if "preview_formatted" in scene and scene['preview_formatted']:
                if "thumb" in scene['preview_formatted'] and scene['preview_formatted']['thumb']:
                    resolution = 0
                    for thumb in scene['preview_formatted']['thumb']:
                        height = re.search(r'-(\d)', thumb)
                        if height:
                            height = int(height.group(1))
                            if height > resolution:
                                resolution = height
                                imageinfo = scene['preview_formatted']['thumb'][thumb][0]
                                item['image'] = f"https://c762d323d1.mjedge.net{imageinfo['fileuri']}?{imageinfo['signature']}"
            if item['image']:
                item['image_blob'] = self.get_image_blob_from_link(item['image'])

            item['id'] = "thai-swinger-" + scene['slug']
            item['trailer'] = ""
            item['url'] = f"https://www.LadyboyPussy.com/index.php?section=1681&start={str(int(meta['page']) * 48)}"
            item['network'] = "Ladyboy Pussy"
            item['parent'] = "Ladyboy Pussy"
            item['site'] = "Ladyboy Pussy"

            yield self.check_item(item, self.days)
