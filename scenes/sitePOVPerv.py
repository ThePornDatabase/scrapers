import re
from datetime import date, timedelta
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePOVPervSpider(BaseSceneScraper):
    name = 'POVPerv'
    network = 'POV Perv'
    parent = 'POV Perv'
    site = 'POV Perv'

    start_urls = [
        'https://tour.povperv.com',
    ]

    selector_map = {
        'title': '//div[@class="title clear"]/h2/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[contains(@class,"update_date")]/text()',
        'image': '//span[@class="model_update_thumb"]/img/@src',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//span[@class="update_tags"]/a/text()',
        'external_id': r'updates/(.*).html',
        'trailer': '',
        'pagination': '/videos?page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div [@class="content-item-medium"]')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./div//h3/a/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())
            else:
                item['title'] = None

            scenedate = scene.xpath('./div//span[@class="date"]/span/following-sibling::text()')
            if scenedate:
                scenedate = scenedate.get()
                scenedate = re.sub(r"([0123]?[0-9])(st|th|nd|rd)?", r"\1", scenedate)
                item['date'] = self.parse_date(scenedate, date_formats=['%d %b %Y']).isoformat()
            else:
                item['date'] = self.parse_date('today').isoformat()

            performers = scene.xpath('.//h4[@class="models"]/a/text()')
            if performers:
                item['performers'] = list(map(lambda x: self.cleanup_title(x), performers.getall()))
            else:
                item['performers'] = []

            image = scene.xpath('.//a/@data-images')
            if image:
                image = re.search(r'(http.*?\.jpg)', image.get()).group(1)
                item['image'] = image = self.format_link(response, image.replace("\\", ""))
            else:
                item['image'] = None

            item['image_blob'] = None
            item['description'] = ''
            item['tags'] = ['POV']
            item['trailer'] = None
            item['url'] = response.url
            item['network'] = 'POV Perv'
            item['parent'] = 'POV Perv'
            item['site'] = 'POV Perv'

            if item['title']:
                externid = item['title'].replace(" ", "-").lower()
                item['id'] = re.sub('[^a-zA-Z0-9-]', '', externid)
            else:
                item['id'] = None

            if item['title'] and item['id'] and item['date'] > '2021-02-26':
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
