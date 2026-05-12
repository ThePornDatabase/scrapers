import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteKenMarcusExquisiteEroticaSpider(BaseSceneScraper):
    name = 'KenMarcusExquisiteErotica'
    network = 'Ken Marcus Exquisite Erotica'
    parent = 'Ken Marcus Exquisite Erotica'
    site = 'Ken Marcus Exquisite Erotica'

    start_urls = [
        'https://www.kenmarcus.com',
    ]

    paginations = [
        '/tour3/categories/updates_%s_d.html',
        '/tour3/categories/movies_%s_d.html',
        ]

    selector_map = {
        'external_id': r'',
        'pagination': '/tour3/categories/updates_%s_d.html',
        'type': 'Scene',
    }
    
    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)
    
    async def start(self):
        meta = {}
        for url in self.start_urls:
            meta['url'] = url
            meta['firstpage'] = True
            meta['page'] = self.page - 1
            for pagination in self.paginations:
                meta['pagination'] = pagination
                yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, cookies=self.cookies, meta=meta, dont_filter=True)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="updateItem"]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//h4/a/text()').get()
            item['title'] = self.cleanup_title(title)

            scenedate = scene.xpath('.//span[contains(text(), ",")]/text()')
            if scenedate:
                scenedate = scenedate.get().strip()
                item['date'] = self.parse_date(scenedate, date_formats=['%B %d, %Y']).isoformat()
            
            if self.check_item(item, self.days):
                performers = scene.xpath('.//span[contains(@class, "tour_update_models")]/a/text()').getall()
                item['performers'] = []
                item['performers_data'] = []
                for performer in performers:
                    performer = self.cleanup_title(performer)
                    item['performers'].append(performer)
                    perf = {}
                    perf['name'] = performer
                    if performer.lower() in ['alex payne', 'charlie comet', 'jason', 'john henry', 'master bos', 'master liam', 'richie black', 'simon blaise', 'taime', 'tj cummings']:
                        perf['gender'] = 'Male'
                    else:
                        perf['gender'] = 'Female'
                    perf['site'] = 'Ken Marcus Exquisite Erotica'
                    item['performers_data'].append(perf)

                item['tags'] = ['Bondage', 'Domination', 'Erotic Photography']

                image = scene.xpath('./a[1]/@href')
                if image:
                    item['image'] = f"https://www.kenmarcus.com/tour3/{image.get()}"
                    item['image_blob'] = self.get_image_blob_from_link(item['image'])
                else:
                    item['image'] = None
                    item['image_blob'] = None

                item['id'] = re.search(r'content/(.*?)/', item['image']).group(1)
                item['url'] = f"https://www.kenmarcus.com/content/{item['id']}"

                item['site'] = 'Ken Marcus Exquisite Erotica'
                item['parent'] = 'Ken Marcus Exquisite Erotica'
                item['network'] = 'Ken Marcus Exquisite Erotica'

                yield item