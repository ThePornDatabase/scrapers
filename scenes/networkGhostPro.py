import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class NetworkGhostProSpider(BaseSceneScraper):
    name = 'GhostPro'
    network = 'Ghost Pro'

    paginations = [
        ['https://www.thaigirlswild.com', '/categories/scenes_%s_d', ['Asian', 'Amateur'], 'Thai Girls Wild'],
        ['https://www.thaigirlswild.com', '/index.php', ['Asian', 'Amateur'], 'Thai Girls Wild'],
        ['https://www.creampieinasia.com', '/categories/creampie-in-asia-scenes_%s_d', ['Asian', 'Amateur'], 'Creampie in Asia'],
        ['https://www.creampieinasia.com', '/index.php', ['Asian', 'Amateur'], 'Creampie in Asia'],
        ['https://www.creampiethais.com/', '/categories/creampiethais_%s_d', ['Asian', 'Amateur'], 'Creampie Thais'],
        ['https://www.creampiethais.com/', '/index.php', ['Asian', 'Amateur'], 'Creampie Thais'],
        ['https://asiansuckdolls.com', '/categories/asiansuckdolls_%s_d', ['Asian', 'Amateur'], 'Asian Suck Dolls'],
        ['https://asiansuckdolls.com', '/index.php', ['Asian', 'Amateur'], 'Asian Suck Dolls'],
        ['https://creampiecuties.com', '/categories/creampiecuties_%s_d', ['Creampie', 'Amateur'], 'Creampie Cuties'],
        ['https://creampiecuties.com', '/index.php', ['Creampie', 'Amateur'], 'Creampie Cuties'],
    ]

    selector_map = {
        'title': '//div[contains(@class, "updatesBlock")]/div[contains(@class, "section-heading")]/h3/text()',
        'description': '//div[@class="wrapper"]//span[contains(@class,"tour_update_models")]/../following-sibling::div/text()',
        'date': '//div[@class="updateDetails"]/div[1]/div[1]/p[1]/text()',
        'image': '//meta[@property="og:image"]/@content|//meta[@property="twitter:image"]/@content',
        'performers': '//div[@class="wrapper"]//span[contains(@class,"tour_update_models")]/a/text()',
        'tags': '',
        'trailer': '',
        'external_id': r'.*/(.*)?\.html',
    }

    def start_requests(self):
        for pagination in self.paginations:
            url = self.get_next_page_url(pagination[0], self.page, pagination[1])
            yield scrapy.Request(url, callback=self.parse, meta={'page': self.page, 'url': pagination[0], 'pagination': pagination[1], 'site': pagination[3], 'addtags': pagination[2]}, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta = response.meta
                    meta['page'] = meta['page'] + 1
                    print('NEXT PAGE: ' + str(meta['page']))
                    url = self.get_next_page_url(meta['url'], meta['page'], meta['pagination'])
                    yield scrapy.Request(url,
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)


    def get_next_page_url(self, url, page, pagination):
        if "%s" in pagination:
            url = self.format_url(url, pagination % str(page))
        else:
            url = url + pagination
        return url


    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class, "videoBlock")]')
        for scene in scenes:
            item = SceneItem()
            title = scene.xpath('.//h4/text()')
            if title:
                title = title.get()
            else:
                title = scene.xpath('./p/text()')
                if title:
                    title = title.get().strip()
                    if "." in title:
                        title = re.search(r'(.*)\.', title).group(1)
            try:
                item['title'] = self.cleanup_title(title)
            except:
                print(scene.xpath('.//*').getall())
            item['tags'] = meta['addtags']
            item['date'] = self.parse_date('today').isoformat()
            item['description'] = scene.xpath('./p/text()').get().strip()
            item['image'] = self.format_link(response, scene.xpath('./div//img[contains(@src, "content")]/@src').get())
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['performers'] = []
            item['trailer'] = ''
            item['network'] = 'Ghost Pro'
            item['parent'] = meta['site']
            item['site'] = meta['site']
            item['id'] = re.search(r'.*/(\d*)', item['image']).group(1)
            item['url'] = re.search(r'(http.*\.com)', response.url).group(1) + '/videos/' + item['id']
            yield item
