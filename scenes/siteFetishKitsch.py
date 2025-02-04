from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteFetishKitschSpider(BaseSceneScraper):
    name = 'FetishKitsch'

    start_urls = [
        'https://fetishkitsch.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/api/post?limit=1000&keywords=&type=all&sort=new&index=%s',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_scenes(self, response):
        scenes = response.json()
        for scene in scenes['posts']:
            item = self.init_scene()

            item['title'] = scene['title'].replace("_", " ")
            item['date'] = self.parse_date(scene['publishDate'], date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')
            item['image'] = scene['videoThumbnail']

            item['performers'] = scene['people']
            item['performers'] = list(map(lambda x: x.replace("_", " ").strip(), item['performers']))

            item['tags'] = scene['tags']
            item['tags'] = list(map(lambda x: x.replace("_", " ").strip(), item['tags']))

            item['duration'] = scene['videoLength']
            item['trailer'] = scene['promoVideo']
            item['id'] = scene['_id']
            item['url'] = f"https://fetishkitsch.com/post/{item['id']}"
            item['site'] = 'Fetish Kitsch'
            item['parent'] = 'Fetish Kitsch'
            item['network'] = 'Fetish Kitsch'
            item['type'] = "Scene"

            yield self.check_item(item, self.days)
