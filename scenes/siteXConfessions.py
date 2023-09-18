import re
import html
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteXConfessionsSpider(BaseSceneScraper):
    name = 'XConfessions'
    network = 'XConfessions'
    parent = 'XConfessions'

    start_urls = [
        'https://xconfessions.com/',
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//h2/..//text()',
        'date': '//script[contains(@type,"json") and not(contains(text(), "BreadcrumbList"))]/text()',
        're_date': r'dateCreated.*?(\d{4}-\d{2}-\d{2})',
        'image': '//div[contains(@class,"w-1/3")][1]/div/div/picture/source/@data-srcset',
        're_image': r'(.*)\?',
        'performers': '//div[contains(@class,"w-1/3")]//a[@data-cy="performer-link"]/text()|//a[@data-cy="performer-link"]/text()',
        'tags': '//div[contains(@class,"w-1/3")]//a[contains(@href,"/categories/")]/text()',
        'duration': '//div[contains(@class,"tablet:hidden laptop:block")]/p[contains(text(), "mins")]/text()',
        're_duration': r'(\d+)\s+?mins',
        'director': '//p[contains(text(), "Director")]/a/text()',
        'external_id': r'.*\/(.*)',
        'trailer': '',
        'pagination': '/?page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@data-cy,"hover-wrapper")]/a[contains(@href,"/film")]')
        for scene in scenes:
            image = scene.xpath('./div/div/img/@src')
            if image:
                meta['image'] = image.get()
                meta['image_blob'] = self.get_image_blob_from_link(meta['image'])
            scene = scene.xpath('./@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return "XConfessions"

    def get_description(self, response):
        desc_rows = self.process_xpath(response, self.get_selector_map('description')).getall()
        if desc_rows:
            description = ''
            for desc in desc_rows:
                desc = desc.strip()
                if desc:
                    description = description + " " + desc
            return html.unescape(description.strip())
        return ''

    def get_director(self, response):
        director = response.xpath(self.get_selector_map('director'))
        if director:
            director = self.cleanup_title(director.get().replace("\n", " ").replace("  ", " "))
            return director
        return ''

    def get_duration(self, response):
        duration = super().get_duration(response)
        if duration:
            duration = str(int(duration) * 60)
        return duration
