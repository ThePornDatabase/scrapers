import json
from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteMrBigfatdickSpider(BaseSceneScraper):
    name = 'MrBigfatdick'
    network = 'MrBigfatdick'

    start_urls = [
        "https://backend.mrbigfatdick.com",
    ]

    selector_map = {
        'external_id': 'movie\\/(.+)',
        'pagination': '/api/public/videos?p=%s&s=50'
    }

    def get_scenes(self, response):
        movies = json.loads(response.text)

        for movie in movies:
            item = SceneItem()

            item['title'] = self.cleanup_title(movie['fullName'])
            item['description'] = ''

            item['performers'] = []
            for performer in movie['models']:
                item['performers'].append(performer['fullName'].strip().title())

            item['image'] = movie['previewImage960']
            if not item['image']:
                item['image'] = None

            item['image_blob'] = None

            item['date'] = self.parse_date(movie['publishDate']).isoformat()

            item['tags'] = []
            for tag in movie['tags']:
                item['tags'].append(tag['fullName'].strip().title())

            item['trailer'] = ''

            item['site'] = "MrBigfatdick"
            item['parent'] = "MrBigfatdick"
            item['network'] = "MrBigfatdick"
            item['url'] = "https://www.mrbigfatdick.com/videos/" + movie['permaLink']
            item['id'] = movie['id']

            days = int(self.days)
            if days > 27375:
                filterdate = "0000-00-00"
            else:
                filterdate = date.today() - timedelta(days)
                filterdate = filterdate.strftime('%Y-%m-%d')

            if self.debug:
                if not item['date'] > filterdate:
                    item['filtered'] = "Scene filtered due to date restraint"
                print(item)
            else:
                if filterdate:
                    if item['date'] > filterdate:
                        yield item
                else:
                    yield item

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)
