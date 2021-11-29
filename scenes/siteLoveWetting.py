import re
from datetime import date, timedelta
import string

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteLoveWettingSpider(BaseSceneScraper):
    name = 'LoveWetting'

    start_urls = [
        'https://www.lovewetting.com',
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
        'pagination': '/wetting-desperation-videos.html?order=date&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="item"]')
        print(f'Found {len(scenes)} Scenes')
        for scene in scenes:
            item = SceneItem()

            title = scene.xpath('./div[@class="box-info"]/h3/text()')
            item['title'] = ''
            if title:
                item['title'] = self.cleanup_title(title.get())

            description = scene.xpath('./div[@class="box-info"]/article/div[contains(@class, "description")]/text()')
            item['description'] = ''
            if description:
                item['description'] = self.cleanup_description(description.get())

            scenedate = scene.xpath('./div[@class="box-info"]/p/span/i[contains(@class, "calendar")]/following-sibling::text()')
            item['date'] = self.parse_date('today').isoformat()
            item['date'] = ''
            if scenedate:
                item['date'] = self.parse_date(scenedate.get().strip()).isoformat()

            image = scene.xpath('.//div[@class="imgwrap"]//img/@src')
            item['image'] = None
            item['id'] = ''
            item['url'] = ''
            if image:
                image = image.get().strip().replace("&amp;", "&")
                item['image'] = self.format_link(response, image)
                item['id'] = re.search(r'\d{4}\/(.*)\&', item['image']).group(1)
                item['url'] = re.search(r'(.*\d{4}\/.*)\&', item['image']).group(1)

            item['image_blob'] = None

            performers = scene.xpath('.//p[@class="tags"]/strong[contains(text(), "Models")]/following-sibling::a/text()')
            item['performers'] = []
            if performers:
                item['performers'] = list(map(lambda x: string.capwords(x.strip()), performers.getall()))

            tags = scene.xpath('.//p[@class="tags"]/strong[contains(text(), "Tags")]/following-sibling::a/text()')
            item['tags'] = []
            if tags:
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags.getall()))

            item['site'] = "Love Wetting"
            item['parent'] = "Love Wetting"
            item['network'] = "Love Wetting"
            item['trailer'] = ''

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
