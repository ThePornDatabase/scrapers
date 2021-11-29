from datetime import date, timedelta
import tldextract
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


def match_site(argument):
    match = {
        'backroomcastingcouch': "Backroom Casting Couch",
        'blackambush': "Black Ambush",
        'exploitedcollegegirls': "Exploited College Girls",
        'ikissgirls': "I Kiss Girls",
        'interracialpass': "Interracial Pass",
    }
    return match.get(argument, '')


class InterracialPassSpider(BaseSceneScraper):
    name = 'InterracialPass'
    network = 'InterracialPass'

    start_urls = [
        'https://www.interracialpass.com',
        'https://www.backroomcastingcouch.com',
        'https://blackambush.com',
        'https://exploitedcollegegirls.com',
        'https://www.ikissgirls.com'
    ]

    selector_map = {
        'title': '//h2[@class="section-title"]/text()',
        'description': '//div[@class="update-info-block"]/h3[contains(text(),"Description")]/following-sibling::text()',
        'date': '//div[@class="update-info-row"]/text()',
        'image': '//div[@class="player-thumb"]//img/@src0_1x | //img[contains(@class,"main-preview")]/@src',
        'performers': '//div[contains(@class, "models-list-thumbs")]//li//span/text()',
        'tags': '//ul[@class="tags"]//li//a/text()',
        'external_id': 'trailers/(.+)\\.html',
        'trailer': '',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class, "item-video")]')
        for scene in scenes:
            link = scene.css('a::attr(href)').get()
            meta = {}
            if scene.xpath('.//img/@src0_1x').get() is not None:
                meta['image'] = self.format_link(
                    response, scene.xpath('//img/@src0_1x').get())

            if link:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page):
        selector = '/t1/categories/movies_%s_d.html'

        if 'exploitedcollegegirls' in base:
            selector = '/site/categories/movies_%s_d.html'
        elif 'ikissgirls' in base:
            selector = '/categories/movies_%s_d.html'
        elif 'blackambush' in base:
            selector = '/categories/movies_%s_d.html'
        elif 'backroomcastingcouch' in base:
            selector = '/site/categories/movies_%s_d.html'

        return self.format_url(base, selector % page)

    def get_date(self, response):
        date = self.process_xpath(
            response, self.get_selector_map('date')).extract()
        return self.parse_date(date[1].strip()).isoformat()

    def get_image(self, response):
        meta = response.meta
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = self.get_from_regex(image.get(), 're_image')

            if image:
                image = self.format_link(response, image)
                return image.replace(" ", "%20")
        else:
            if 'image' in meta:
                return self.format_link(response, meta['image'])
        return ''

    def get_site(self, response):
        site = tldextract.extract(response.url).domain
        site = match_site(site)
        return site

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

        if 'site' in response.meta:
            item['site'] = response.meta['site']
        else:
            item['site'] = self.get_site(response)

        if 'date' in response.meta:
            item['date'] = response.meta['date']
        else:
            item['date'] = self.get_date(response)

        item['image'] = self.get_image(response)

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
        else:
            item['network'] = self.get_network(response)

        if hasattr(self, 'parent'):
            item['parent'] = self.parent
        else:
            item['parent'] = self.get_parent(response)

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
