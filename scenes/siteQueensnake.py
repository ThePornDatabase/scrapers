import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SiteQueensnakeSpider(BaseSceneScraper):
    name = 'Queensnake'
    network = 'Queensnake'
    parent = 'Queensnake'
    site = 'Queensnake'

    start_urls = [
        'https://queensect.com',
        'https://queensnake.com',
    ]

    cookies = {
        'cLegalAge': 'true',
        'cCookieConsent': 'true',
    }

    selector_map = {
        'title': './/span[@class="contentFilmName"]/text()',
        'description': './/div[@class="contentPreviewDescription"]/text()',
        'date': './/span[@class="contentFileDate"]/a/text()',
        'date_formats': ['%Y %B %d'],
        'image': './/div[@class="contentPreviewRightImageWrap"]/a[1]/div[1]/img/@src',
        'performers': './/div[@class="contentPreviewTags"]/a/text()',
        'tags': './/div[@class="contentPreviewTags"]/a/text()',
        'duration': './/span[@class="contentFileDate"]/a/following-sibling::text()',
        'trailer': '',
        'external_id': r'',
        'pagination': '/previewmovies/%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="contentBlock"]')
        for scene in scenes:
            item = SceneItem()
            item['id'] = scene.xpath('./div[1]/@data-filmid').get()

            item['url'] = response.url
            image = scene.xpath('.//div[@class="contentPreviewRightImageWrap"]/a[1]/div[1]/img/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = ""
                item['image_blob'] = ""
            if "?" in item['image']:
                item['image'] = re.search(r'(.*)\?', item['image']).group(1)
            item['title'] = self.get_title(scene)
            item['description'] = self.get_description(scene)
            item['date'] = self.get_date(scene)
            item['performers'] = self.get_performers(scene)
            item['tags'] = self.get_tags(scene)
            item['duration'] = self.get_duration(scene)
            item['trailer'] = ""
            if "queensnake" in response.url:
                item['site'] = "Queensnake"
                item['parent'] = "Queensnake"
                item['network'] = "Queensnake"
            if "queensect" in response.url:
                item['site'] = "Queensect"
                item['parent'] = "Queensect"
                item['network'] = "Queensnake"
            yield self.check_item(item, self.days)

    def get_next_page_url(self, base, page):
        page = str(int(page) - 1)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_performers(self, scene):
        performers = scene.xpath('.//div[@class="contentPreviewTags"]/a/text()').getall()
        performers2 = []
        for performer in performers:
            if not performer.islower():
                performers2.append(string.capwords(performer))
        return performers2

    def get_tags(self, scene):
        tags = scene.xpath('.//div[@class="contentPreviewTags"]/a/text()').getall()
        tags2 = []
        for tag in tags:
            if tag.islower() and "4k" not in tag:
                tags2.append(string.capwords(tag))
        return tags2

    def get_date(self, scene):
        scenedate = scene.xpath('.//span[@class="contentFileDate"]/text()')
        if scenedate:
            scenedate = scenedate.get()
            scenedate = re.search(r'(\d{4} \w+ \d+)', scenedate)
            if scenedate:
                scenedate = scenedate.group(1)
                scenedate = self.parse_date(scenedate, date_formats=['%Y %B %d']).strftime('%Y-%m-%d')
                return scenedate
        return None

    def get_duration(self, scene):
        duration = scene.xpath('.//span[@class="contentFileDate"]/text()')
        if duration:
            duration = duration.get()
            duration = duration.replace(" ", "")
            duration = re.search(r'(\d+)min', duration.lower())
            if duration:
                duration = duration.group(1)
                duration = str(int(duration) * 60)
                return duration
        return None
