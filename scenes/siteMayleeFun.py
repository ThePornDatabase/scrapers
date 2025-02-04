import string
from requests import get
from cleantext import clean
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteMayleeFunSpider(BaseSceneScraper):
    name = 'MayleeFun'

    start_urls = [
        'https://hinalvakharia.com/api/getData?Video_type=PREMIUM%20VIDEOS&searchme='
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '',
    }

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for link in self.start_urls:
            yield scrapy.Request(link, callback=self.get_scenes, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.json()
        for scene in scenes:
            item = self.init_scene()

            title = scene['video_title']
            if title:
                title = clean(title, no_emoji=True)
                item['title'] = self.cleanup_title(title)

            description = scene['video_desc']
            if description:
                description = clean(description.replace("\n", "").strip(), no_emoji=True)
                item['description'] = self.cleanup_description(description)

            image = scene['poster_image']
            if image:
                image = self.format_link(response, image)
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)

            item['id'] = scene['video_id']

            tags = scene['tags'].split(",")
            item['tags'] = []
            for tag in tags:
                if "http" not in tag:
                    item['tags'].append(string.capwords(tag.strip()))

            if "video_url" in scene and scene['video_url']:
                item['trailer'] = scene['video_url']

            item['duration'] = self.duration_to_seconds(scene['duration'])
            item['performers'] = ['Maylee Fun']

            item['site'] = "Maylee Fun"
            item['parent'] = "Maylee Fun"
            item['network'] = "Maylee Fun"

            item['type'] = 'Scene'
            item['url'] = f"https://videos.mayleefun.xxx/video/{item['id']}"

            yield item
            # ~ print(item)
