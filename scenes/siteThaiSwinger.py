import re
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteThaiSwingerSpider(BaseSceneScraper):
    name = 'ThaiSwinger'
    network = 'Thai Swinger'
    parent = 'Thai Swinger'
    site = 'Thai Swinger'

    start_urls = [
        'https://www.thaiswinger.com',
    ]

    headers = {'X-NATS-cms-area-id': '4ab4cd6a-6644-489e-83cf-f7be8adb759a'}

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
        index = str((int(page) -1) * 48)
        url = f"https://nats.islanddollars.com/tour_api.php/content/sets?cms_set_ids=&data_types=1&content_count=1&count=48&start={index}&cms_area_id=4ab4cd6a-6644-489e-83cf-f7be8adb759a&cms_block_id=105090&orderby=published_desc&content_type=video&status=enabled&text_search=&data_type_search=%7B%22100001%22%3A%22171%22%7D"
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
                    image = ""
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
            item['url'] = f"https://www.thaiswinger.com/index.php?section=1681&start={str(int(meta['page']) * 48)}"
            item['network'] = "Thai Swinger"
            item['parent'] = "Thai Swinger"
            item['site'] = "Thai Swinger"

            yield self.check_item(item, self.days)
