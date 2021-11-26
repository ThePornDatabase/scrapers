import re
from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class AlettaOceanLiveSpider(BaseSceneScraper):
    name = 'AlettaOceanLive'
    network = "Aletta Ocean Live"
    parent = "Aletta Ocean Live"

    start_urls = [
        'https://alettaoceanlive.com/',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'.*/(.*?)\.html',
        'trailer': '',
        'pagination': '/tour/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="movie-set-list-item"]')
        scenelist = []
        for scene in scenes:
            item = SceneItem()
            item['site'] = "Aletta Ocean Live"
            item['parent'] = "Aletta Ocean Live"
            item['network'] = "Aletta Ocean"
            title = scene.xpath('.//div[contains(@class,"title")]/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())
            else:
                item['title'] = 'No Title Available'

            scenedate = scene.xpath('.//div[contains(@class,"date")]/text()')
            if scenedate:
                item['date'] = self.parse_date(scenedate.get().strip()).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            item['performers'] = ['Aletta Ocean']

            image = scene.xpath('./@style').get()
            if image:
                image = re.search(r'url\((.*.jpg)', image).group(1)
                if image:
                    item['image'] = image.strip()
            else:
                item['image'] = ''

            item['image_blob'] = ''

            item['trailer'] = ''

            url = scene.xpath('./a/@href').get()
            if url:
                item['url'] = url.strip()
                external_id = re.search(r'.*/(.*).html', url).group(1)
                if external_id:
                    item['id'] = external_id.strip().lower()
                else:
                    item['id'] = ''
            else:
                item['url'] = ''

            item['description'] = ''
            item['tags'] = []

            if item['title'] and item['id']:
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
                            scenelist.append(item.copy())
                    else:
                        scenelist.append(item.copy())

            item.clear()

        return scenelist
