import string
import html
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLasVegasAmateursSpider(BaseSceneScraper):
    name = 'LasVegasAmateurs'
    network = 'Las Vegas Amateurs'
    max_pages = 20

    start_urls = [
        'http://lasvegasamateurs.com'
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title")]/text()',
        'description': '//p[contains(@class, "description")]/text()',
        'performers': '//span[contains(@class,"models")]/a/text()',
        'date': '//div[contains(@class, "date")]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'tags': '//div[contains(@class, "video-tags")]/a/text()',
        'trailer': '',
        'external_id': r'trailers/(.*)\.html',
        'pagination': '/tour/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]')
        if response.meta['page'] < self.max_pages:
            for scene in scenes:
                item = SceneItem()
                title = scene.xpath('./div/h5/a/text()').get()
                if title:
                    item['title'] = html.unescape(string.capwords(title))
                else:
                    item['title'] = ''

                item['description'] = ''

                performers = scene.xpath('.//span[@class="tour_update_models"]/a/text()')
                if performers:
                    performers = performers.getall()
                    item['performers'] = list(map(lambda x: x.strip(), performers))
                else:
                    item['performers'] = []

                scenedate = scene.xpath('./div/p/span[contains(text(), "/")]/text()')
                item['date'] = dateparser.parse('today').isoformat()
                if scenedate:
                    scenedate = dateparser.parse(scenedate.get(), date_formats=['%m/%d/%Y']).isoformat()
                    item['date'] = scenedate

                image = scene.xpath('./div/a/img/@src0_3x')
                if image:
                    image = image.get()
                    item['image'] = "http://lasvegasamateurs.com/tour/" + image.strip()
                else:
                    item['image'] = []

                item['tags'] = []
                trailer = scene.xpath('./div/a/@onclick')
                item['trailer'] = ''
                if trailer:
                    trailer = trailer.get()
                    trailer = re.search(r'\'(/.*.mp4)', trailer)
                    if trailer:
                        item['trailer'] = 'https://lasvegasamateurs.com' + trailer.group(1).strip()

                item['site'] = "Las Vegas Amateurs"
                item['parent'] = "Las Vegas Amateurs"
                item['network'] = "Las Vegas Amateurs"

                extern_id = re.search(r'content/(.*?)/.*?.jpg', item['image'])
                if extern_id:
                    item['id'] = extern_id.group(1).strip().lower()

                item['url'] = response.url

                yield item
