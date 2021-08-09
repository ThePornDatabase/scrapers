import dateparser
import scrapy
import re

from tpdb.BaseSceneScraper import BaseSceneScraper


class OrgasmAbuseSpider(BaseSceneScraper):
    name = 'OrgasmAbuse'
    network = 'Orgasm Abuse'


    start_urls = [
        'https://www.orgasmabuse.com/'
    ]

    selector_map = {
        'title': '//div[contains(@class,"detail-content-main")]//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'performers': '//div[contains(@class,"detail-content-main")]//a[contains(@href,"?mid")]/text()',
        'date': '',
        'image': '//div[contains(@class,"video-cover")]/@style',
        'tags': '//div[@class="pb-5"]//a[contains(@href, "?gid") or contains(@href,"?lid")]/text()',
        'external_id': '\/video\/(\d+)\/',
        'trailer': '',
        'pagination': '/browsevideos?lt=latest&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div/a[contains(@href,"/video/")]')
        # ~ scenes = list(dict.fromkeys(scenes))
        for scene in scenes:
            date = scene.xpath('.//div[contains(@class,"text-gray-600")]/div[contains(@class,"text-right")]/text()').get()
            if date:
                date = dateparser.parse(date.strip()).isoformat()                
            scene = scene.xpath('./@href').get()
            
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': 'Orgasm Abuse', 'date':date})

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            trailer = self.process_xpath(
                response, self.get_selector_map('trailer')).get()
            trailer = re.search('video_url:\ .*?(https:\/\/.*?\.mp4)\/', trailer).group(1)
            if trailer:
                return trailer
        return ''

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.strip().title(), tags))
        return []


    def get_image(self, response):
        image = self.process_xpath(response, self.get_selector_map('image')).get()
        if image:
            image = re.search('url\(\/\/(.*.jpe?g)', image).group(1)
            if image:
                return "https://" + image.strip()
        return ''

    def get_site(self, response):
        return "Orgasm Abuse"
        
    def get_parent(self, response):
        return "Orgasm Abuse"
        
