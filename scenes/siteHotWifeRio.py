import re
from datetime import date, timedelta
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteHotWifeRioSpider(BaseSceneScraper):
    name = 'HotWifeRio'
    network = 'Hot Wife Rio'

    start_urls = [
        'https://hotwiferio.com',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'external_id': r'updates\/(.*).html',
        'trailer': '',
        'pagination': '/new-tour/updates/page_%s.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="update_block"]')
        for scene in scenes:
            item = SceneItem()
            title = scene.xpath('./div/span[@class="update_title"]/text()')
            item['title'] = ''
            if title:
                item['title'] = self.cleanup_title(title.get())

            description = scene.xpath('.//span[@class="update_description"]/text()')
            item['description'] = ''
            if description:
                item['description'] = self.cleanup_description(description.get())

            scenedate = scene.xpath('.//span[@class="update_date"]/text()')
            item['date'] = self.parse_date('today').isoformat()
            if scenedate:
                item['date'] = self.parse_date(scenedate.get().strip(), date_formats=['%m/%d/%Y']).isoformat()

            image = scene.xpath('./following-sibling::div[@class="update_image"]/img/@src')
            item['image'] = None
            if image:
                item['image'] = "https://hotwiferio.com/new-tour/" + image.get().strip()

            item['image_blob'] = None

            item['performers'] = ['Rio Blaze']

            tags = scene.xpath('.//span[@class="update_tags"]/a/text()')
            item['tags'] = []
            if tags:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags.getall()))

            item['url'] = response.url
            item['site'] = "Hot Wife Rio"
            item['parent'] = "Hot Wife Rio"
            item['network'] = "Hot Wife Rio"

            item['trailer'] = ''

            item['id'] = ''
            externid = re.search(r'content/(.*?)/', item['image'])
            if externid:
                item['id'] = externid.group(1).strip()

            if item['id'] and item['title']:
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
