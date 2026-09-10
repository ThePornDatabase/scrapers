import scrapy
import re
import dateparser
from tpdb.BaseSceneScraper import BaseSceneScraper
true = True
false = False


class networkDungeonCorpSpider(BaseSceneScraper):
    name = 'DungeonCorp'
    network = 'Dungeon Corp'

    cookies = [{
            "domain": ".dungeoncorp.com",
            "hostOnly": false,
            "httpOnly": true,
            "name": "_age_confirmed_1",
            "path": "/",
            "sameSite": "unspecified",
            "value": "a8166b5f7ec8fa7508efd3b276320d6f"
        }
    ]

    start_urls = [
        'https://dungeoncorp.com',
    ]

    selector_map = {
        'title': '//title/text()',
        'description': '//p[@class="lead text-center"]//text()',
        'image': '//img[contains(@src,"vidt1.jpg")]/@src|//img[contains(@src,"vidt.jpg")]/@src',
        'external_id': '',
        'trailer': '',
        'pagination': '/?page=updates&p=%s'
    }

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)
    

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath('//a[contains(@href, "/updates/")]/parent::div[contains(@class, "col-md-4")]')
        for scene in scenes:
            scenedate = scene.xpath('.//i[contains(@class, "fa-clock")]/following-sibling::text()[1]').get()
            if scenedate:
                scenedate = dateparser.parse(scenedate.strip(), date_formats=['%m/%d/%Y']).strftime('%Y-%m-%d')
            if scenedate:
                meta['date'] = scenedate
            
            orig_image = scene.xpath('.//img/@src')
            if orig_image:
                meta['orig_image'] = self.format_link(response, orig_image.get())

            performers = scene.xpath('.//a[contains(@href, "model=")]/text()')
            if performers:
                meta['performers'] = performers.getall()
            else:
                meta['performers'] = []

            site = scene.xpath('.//a[contains(@href, "site=")]/text()')
            if site:
                meta['site'] = site.get()

            sceneurl = scene.xpath('./a[contains(@href, "/updates/")]/@href').get()

            if self.check_item(meta, self.days):
                yield scrapy.Request(url=self.format_link(response, sceneurl), callback=self.parse_scene, meta=meta)

    def get_image(self, response):
        meta = self.copy_meta(response)
        image = self.process_xpath(response, self.get_selector_map('image'))
        if image:
            image = image.get()

        if not image or image in response.url:
            image = meta['orig_image']

        image = self.format_link(response, image)
        return image.replace(" ", "%20")

    def get_tags(self, response):
        return ['Bondage', 'Submission']

    def get_id(self, response):
        external_id = response.xpath('//span[@class="shootid"]/text()')
        if external_id:
            external_id = external_id.get()
            external_id = re.sub(r'[^a-z0-9:_-]+', '', external_id.lower())
            external_id = re.search(r'\:(.*)', external_id)
            if external_id:
                external_id = external_id.group(1)
                return external_id.strip()
        else:
            return ''
        
    def get_duration(self, response):
        duration = response.xpath('//i[contains(@class, "fa-video")]/following-sibling::span[contains(following-sibling::text(), "minutes")]//text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                return str(int(duration.group(1)) * 60)