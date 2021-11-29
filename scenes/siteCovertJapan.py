import re
from datetime import date, timedelta
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteSubmissiveXSpider(BaseSceneScraper):
    name = 'CovertJapan'
    network = 'Sex Like Real'
    parent = 'Sex Like Real'
    site = 'CovertJapan'
    max_pages = 15

    start_urls = [
        'https://www.covertjapan.com',
    ]

    custom_settings = {'AUTOTHROTTLE_ENABLED': True,
                       'AUTOTHROTTLE_DEBUG': False,
                       'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
                       'CONCURRENT_REQUESTS': 1,
                       'DOWNLOAD_DELAY': 2
                       }

    selector_map = {
        'title': '//h2[@itemprop="name"]/text()',
        'description': '//div[@id="details"]/div//text()',
        'date': '',
        'image': '//div[@id="images"]/div[1]/div[1]/div[@class="img-polaroid"]/a/@href',
        'performers': '//div[@id="details"]//strong/a/text()',
        'tags': '//meta[@name="keywords"]/@content',
        'external_id': r'videos/(.*)',
        'trailer': '',
        'pagination': '/en/videos?start=%s'
    }

    def parse(self, response, **kwargs):
        if self.limit_pages > self.max_pages:
            self.limit_pages = self.max_pages
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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumbnail"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_next_page_url(self, base, page):
        page = str((int(page) - 1) * 12)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_description(self, response):
        if self.get_selector_map('description'):
            descriptionxpath = self.process_xpath(response, self.get_selector_map('description'))
            if descriptionxpath:
                if len(descriptionxpath) == 1:
                    description = self.cleanup_description(descriptionxpath.get())
                if len(descriptionxpath) > 1:
                    description = ''
                    for descrow in descriptionxpath.getall():
                        if (descrow[:1] != "-" and "STARRING" not in descrow and "RELEASED" not in descrow and "NOTES" not in descrow) or " vr " in descrow.lower():
                            descrow = self.cleanup_description(descrow)
                            if descrow:
                                description = description + " " + descrow
                if description:
                    return self.cleanup_description(description)
        return ''

    def get_date(self, response):
        date = self.process_xpath(response, '//div[@id="details"]//div[contains(text(), "RELEASED")]/text()')
        if date:
            date = date.get()
            if "RELEASED" in date:
                date = re.search(r'(\w+ \d{1,2}, \d{4})', date)
                if date:
                    return self.parse_date(date.group(1), date_formats=['%B %d, %Y']).isoformat()
        return self.parse_date('today').isoformat()

    def get_tags(self, response):
        tags = self.process_xpath(response, self.get_selector_map('tags'))
        if tags:
            tags = tags.get().split(',')
            return list(map(lambda x: x.strip().title(), tags))
        return []

    def parse_scene(self, response):
        item = SceneItem()

        if 'title' in response.meta and response.meta['title']:
            item['title'] = response.meta['title']
        else:
            item['title'] = self.get_title(response)

        if 'description' in response.meta:
            item['description'] = response.meta['description']
        else:
            item['description'] = self.get_description(response)

        if hasattr(self, 'site'):
            item['site'] = self.site
        elif 'site' in response.meta:
            item['site'] = response.meta['site']
        else:
            item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        if 'image' in response.meta:
            item['image'] = response.meta['image']
        else:
            item['image'] = self.get_image(response)

        if 'image' not in item or not item['image']:
            item['image'] = None

        if 'image_blob' in response.meta:
            item['image_blob'] = response.meta['image_blob']
        else:
            item['image_blob'] = self.get_image_blob(response)

        if 'image_blob' not in item or not item['image_blob']:
            item['image_blob'] = None

        if 'performers' in response.meta:
            item['performers'] = response.meta['performers']
        else:
            item['performers'] = self.get_performers(response)

        if 'tags' in response.meta:
            item['tags'] = response.meta['tags']
        else:
            item['tags'] = self.get_tags(response)

        if 'id' in response.meta:
            item['id'] = response.meta['id']
        else:
            item['id'] = self.get_id(response)

        if 'trailer' in response.meta:
            item['trailer'] = response.meta['trailer']
        else:
            item['trailer'] = self.get_trailer(response)

        item['url'] = self.get_url(response)

        if hasattr(self, 'network'):
            item['network'] = self.network
        elif 'network' in response.meta:
            item['network'] = response.meta['network']
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        elif 'parent' in response.meta:
            item['parent'] = response.meta['parent']
        else:
            item['parent'] = self.get_parent(response)

        if self.debug:
            print(item)
        else:
            if "Vr" not in item['tags'] and " vr " not in item['description'].lower():
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
