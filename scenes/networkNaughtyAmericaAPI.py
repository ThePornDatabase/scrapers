import re
import requests
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkNaughtyAmericaAPISpider(BaseSceneScraper):
    name = 'NaughtyAmericaAPI'
    site = 'Naughty America'
    parent = 'Naughty America'
    network = 'Naughty America'

    start_urls = ['https://api.naughtyapi.com']

    selector_map = {
        'external_id': r'',
        'pagination': '/tools/scenes/scenes?page=%s',
    }

    def get_scenes(self, response):
        scenes = response.json()
        if "data" in scenes:
            scenes = scenes['data']
            for scene in scenes:
                item = self.init_scene()
                item['title'] = scene['title']
                item['description'] = scene['synopsis']
                item['date'] = re.search(r'(\d{4}-\d{2}-\d{2})', scene['published_date']).group(1)
                item['site'] = scene['site_name']
                item['parent'] = scene['site_name']
                # ~ if "insidenaughty" in re.sub(r'[^a-z]+', '', item['site'].lower()):
                if self.check_item(item, self.days):
                    image_insert = ""
                    if "promo_video_data" in scene and scene['promo_video_data']:
                        promo_data = scene["promo_video_data"]
                        promo_url = next(iter(promo_data.values()))
                        image_insert = re.search(r'promo/(.*?/.*?)/', promo_url).group(1)
                    else:
                        if "trailers" in scene and scene['trailers']:
                            if "trailer_720" in scene['trailers'] and scene['trailers']['trailer_720']:
                                trailer = scene['trailers']['trailer_720']
                                trailer = re.search(r'\.com/(\w+)/trailers/(\w+)_', trailer)
                                if trailer:
                                    abbrev = trailer.group(1)
                                    title = trailer.group(2)
                                    if "trailer" in title:
                                        title = re.search(r'(.*)trailer', title).group(1)
                                    title = title.removeprefix(abbrev)
                                    image_insert = f"{abbrev}/{title}"

                    if image_insert:
                        valid_image = False
                        image = None

                        for cdn in range(1, 6):
                            for ext in ("jpg", "webp"):
                                urls = [
                                    f"https://images{cdn}.naughtycdn.com/cms/nacmscontent/v1/scenes/{image_insert}/scene/horizontal/1499x944c.{ext}",
                                    f"https://images{cdn}.naughtycdn.com/cms/nacmscontent/v1/scenes/{image_insert}/scene/horizontal/1279x852c.{ext}"
                                ]
                                for res in urls:
                                    if self.image_exists(res):
                                        valid_image = True
                                        image = res
                                        break
                                if valid_image:
                                    break
                            if valid_image:
                                break

                        if valid_image:
                            item['image'] = image
                            item['image_blob'] = self.get_image_blob_from_link(image)

                    item['id'] = scene['id']
                    if "trailers" in scene and scene['trailers']:
                        trailers = scene["trailers"]
                        item['trailer'] = next(iter(trailers.values()))

                    item['duration'] = scene['length']
                    item['url'] = scene['scene_url']
                    item['network'] = self.network
                    item['tags'] = scene['tags']
                    item['performers'], item['performers_data'] = self.get_performers_data(scene['performers'], item['site'])

                    yield item

    def image_exists(self, url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=5)
            content_type = response.headers.get('Content-Type', '')
            return response.status_code == 200 and 'image' in content_type.lower()
        except requests.RequestException:
            return False

    def get_performers_data(self, performers, site):
        performers_data = []
        performer_list = []
        if len(performers):
            for performer in performers['female']:
                performer_list.append(performer)
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Female"
                perf['network'] = "Naughty America"
                perf['site'] = site
                performers_data.append(perf)
            for performer in performers['male']:
                performer_list.append(performer)
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = "Naughty America"
                perf['site'] = "Naughty America"
                performers_data.append(perf)
        return performer_list, performers_data
