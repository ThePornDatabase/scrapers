import re
import dateparser
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class XXXHorrorSpider(BaseSceneScraper):
    name = 'XXXHorror'
    network = 'XXX Horror'
    parent = 'XXX Horror'

    start_urls = [
        'https://xxxhorror.com/',
    ]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': "",
        'external_id': 'updates\\/(.*)\\.html$',
        'trailer': '//video/source/@src',
        'pagination': '/home/page/%s/'
    }

    def parse(self, response, **kwargs):
        count = 0

        scenes = self.parse_scenepage(response)
        if scenes:
            count = len(scenes)
            for scene in scenes:
                yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def parse_scenepage(self, response):
        scenelist = []
        scenes = response.xpath('//article[contains(@class,"post")]')
        for scene in scenes:
            item = SceneItem()
            item['performers'] = []
            item['title'] = ''
            item['id'] = ''

            title = scene.xpath('./header/h2/a/text()').get()
            if title:
                title = title.strip()
                item['title'] = title

            url = scene.xpath('./header/h2/a/@href').get()
            if url:
                item['url'] = url.strip()
                scene_id = re.search(r'.*/(.*?)/$', item['url']).group(1)
                if scene_id:
                    item['id'] = scene_id.strip()

            date = scene.xpath('.//time[contains(@class,"published")]/@datetime').get()
            if date:
                date = date.strip()
            else:
                date = "1970-01-01"
                date = dateparser.parse(date).isoformat()

            item['date'] = date

            description = scene.xpath('.//div[@class="entry-content"]/p/text()').getall()
            if not description:
                description = scene.xpath('.//div[@class="entry-content"]//img/following-sibling::text()').getall()
            if description:
                description = list(map(lambda x: x.strip(), description))
                description = " ".join(description)
                item['description'] = description
            else:
                item['description'] = ''

            image = scene.xpath('.//div[@class="entry-content"]/figure//img/@src').get()
            if not image:
                image = scene.xpath('.//img[contains(@src,"uploads")]/@src').get()

            if image:
                image = image.strip()
            else:
                image = None

            item['image'] = image
            item['image_blob'] = None

            performers = scene.xpath('.//span[@class="cat-links"]/a/text()').getall()
            if performers:
                performers = list(map(lambda x: x.strip(), performers))
                item['performers'] = performers
            else:
                item['performers'] = []

            tags = scene.xpath('.//span[@class="tags-links"]/a/text()').getall()
            if tags:
                tags = list(map(lambda x: x.strip().title(), tags))
                item['tags'] = tags
            else:
                item['tags'] = []

            item['trailer'] = ''
            item['parent'] = "XXX Horror"
            item['network'] = "XXX Horror"
            item['site'] = "XXX Horror"

            if item['id']:
                scenelist.append(item.copy())
                item.clear()

        return scenelist
