import re
from requests import get
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteAVEJAVSpider(BaseSceneScraper):
    name = 'AVEJAV_PPV'
    network = 'R18'

    start_urls = 'https://www.aventertainments.com'

    paginations = [
        '/ppv/255/1/1/dept?countpage=%s',
    ]

    selector_map = {
        'title': '//div[@class="section-title"]/h3/text()',
        'description': '',
        'date': '//div[@class="single-info"]/span[contains(text(), "Date")]/following-sibling::span/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//div[@id="PlayerCover"]/img/@src',
        'performers': '//div[@class="single-info"]/span[contains(text(), "Starring")]/following-sibling::span/a/text()',
        'tags': '//div[@class="single-info"]/span[contains(text(), "Category")]/following-sibling::span/a/text()',
        'trailer': '//div[contains(@class, "button-set")]//span/a[contains(@href, "javascript")]/@onclick',
        're_trailer': r'(https.*?)[\'\"]',
        'external_id': r'.*?/(\d+)/.*',
        'pagination': '',
        'type': 'JAV',
    }

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def start_requests(self):
        ip = get('https://api.ipify.org').content.decode('utf8')
        print('My public IP address is: {}'.format(ip))

        meta = {}
        meta['page'] = self.page

        for pagination in self.paginations:
            meta['pagination'] = pagination
            yield scrapy.Request(url=self.get_next_page_url(self.start_urls, self.page, pagination), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        meta = response.meta
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta)

    def get_scenes(self, response):
        meta = response.meta
        meta['ignore_sites'] = 'Caribbeancom,1Pondo,Heyzo'
        scenes = response.xpath('//div[contains(@class, "single-slider-product__image")]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        studio = response.xpath('//div[@class="single-info"]/span[contains(text(), "Studio")]/following-sibling::span/a/text()')
        if studio:
            return string.capwords(studio.get().strip())
        return "AV Entertainments"

    def get_parent(self, response):
        return self.get_site(response)

    def get_duration(self, response):
        duration = response.xpath('//div[@class="single-info"]/span[contains(text(), "Play") and contains(text(), "ime")]/following-sibling::span/text()')
        if duration:
            duration = duration.get()
            if re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration):
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration).group(1)
                return self.duration_to_seconds(duration)
            else:
                duration = re.search(r'(\d+)', duration)
                if duration:
                    duration = duration.group(1)
                    return str(int(duration) * 60)
        return None

    def get_id(self, response):
        sceneid = response.xpath('//div[@class="single-info"]/span[contains(text(), "Item") and contains(text(), "#")]/following-sibling::span/text()')
        if sceneid:
            sceneid = sceneid.get()
            return sceneid.lower().strip()
        return super().get_id(response)

    def get_title(self, response):
        title = string.capwords(super().get_title(response))
        sceneid = self.get_id(response)
        return f"{sceneid.upper()} - {title}"

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        for performer in performers:
            perf = {}
            perf['name'] = performer
            perf['extra'] = {}
            perf['extra']['gender'] = "Female"
            perf['network'] = "R18"
            perf['site'] = "R18"
            performers_data.append(perf)
        return performers_data

    def parse_scene(self, response):
        meta = response.meta
        item = self.init_scene()

        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)

        if 'image' not in item or not item['image']:
            item['image'] = None

        if ('image_blob' not in item or not item['image_blob']) and item['image']:
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
        item['performers'] = self.get_performers(response)
        item['performers_data'] = self.get_performers_data(response)
        item['tags'] = self.get_tags(response)
        item['id'] = self.get_id(response)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.get_network(response)
        item['parent'] = self.get_parent(response)
        item['type'] = 'JAV'

        if item['duration'] and int(item['duration']) > 3600:
            allow_site = True
            if 'ignore_sites' in meta and meta['ignore_sites']:
                ignore_sites = response.meta['ignore_sites']
                ignore_sites = ignore_sites.split(",")
                for ignore_site in ignore_sites:
                    ignore_site = re.sub('[^0-9a-zA-Z]', '', ignore_site.lower())
                    site = re.sub('[^0-9a-zA-Z]', '', item['site'].lower())
                    if site == ignore_site:
                        allow_site = False

            if allow_site:
                if item['duration'] and int(item['duration']) > 3540:
                    if "check_date" in response.meta:
                        check_date = response.meta['check_date']
                        if item['date'] > check_date:
                            yield self.check_item(item, self.days)
                    else:
                        yield self.check_item(item, self.days)
            else:
                print(f"*** Not processing item due to disallowed site: {item['site']}")
