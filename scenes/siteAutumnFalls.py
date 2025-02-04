import re
from requests import get
from cleantext import clean
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAutumnFallsSpider(BaseSceneScraper):
    name = 'AutumnFalls'

    start_urls = [
        'https://autumnfalls.com/page-data/videos/page-data.json'
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
        meta = response.meta
        scenes = response.json()
        scenes = scenes['result']['pageContext']['videosData']['allAirtableVideos']['nodes']
        for scene in scenes:
            scene = scene['data']
            item = self.init_scene()

            title = scene['Video_Title']
            if title:
                title = clean(title, no_emoji=True)
                item['title'] = self.cleanup_title(title)

            description = scene['Video_Description']
            if description:
                description = clean(description.replace("\n", "").strip(), no_emoji=True)
                item['description'] = self.cleanup_description(description)

            image = scene['Thumbnail']['localFiles'][0]['childImageSharp']['gatsbyImageData']['images']['fallback']['src']
            if image:
                image = self.format_link(response, image)
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)

            item['id'] = scene['UID']

            item['duration'] = scene['Duration']
            item['performers'] = ['Autumn Falls']

            item['site'] = "Autumn Falls"
            item['parent'] = "Autumn Falls"
            item['network'] = "Autumn Falls"

            item['type'] = 'Scene'
            item['url'] = f"https://autumnfalls.com/video/{item['id']}"

            yield item
            # ~ print(item)
