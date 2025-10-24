import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteCollegeUniformSpider(BaseSceneScraper):
    name = 'CollegeUniform'
    network = 'College Uniform'

    start_urls = [
        'https://college-uniform.com',
    ]

    selector_map = {
        'title': '//span[@class="update_title"]/text()',
        'description': '//span[contains(@class,"description")]/text()',
        'date': '//span[@class="update_date"]/text()',
        'date_formats': ['%m/%d/%Y'],
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[@class="tour_update_models"]/a/text()',
        'tags': '//comment()[contains(., "Tags")]',
        'external_id': r'.*\/(.*?).html',
        'trailer': '',
        'pagination': '/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="update_details" and .//div[@class="update_counts" and contains(text(), "video")]]')
        for scene in scenes:
            sceneid = scene.xpath('./@data-setid')
            if sceneid:
                meta['id'] = sceneid.get()

            scene = scene.xpath('./a[1]/@href').get()
            if meta['id']:
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if 'page' in response.meta and response.meta['page'] < self.limit_pages:
            meta = response.meta
            meta['page'] = meta['page'] + 1
            print('NEXT PAGE: ' + str(meta['page']))
            yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page']), callback=self.parse, meta=meta)

    def get_id(self, response):
        return super().get_id(response).lower().strip()

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(response, self.get_selector_map('tags'))
            if tags:
                tags = tags.getall()
                tags = "".join(tags)
                tags = re.findall(r'<a href.*\">(.*?)<\/a', tags)
                for tag in tags:
                    if re.search(r'\d{3}', tag):
                        tags.remove(tag)
                return list(map(lambda x: x.strip().title(), tags))

        return []

    def get_site(self, response):
        return "College Uniform"

    def get_parent(self, response):
        return "College Uniform"
