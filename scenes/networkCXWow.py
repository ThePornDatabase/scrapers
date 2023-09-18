import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'becomingfemme': "Becoming Femme",
        'pure-bbw': "Pure BBW",
        'pure-ts': "Pure TS",
        'pure-xxx': "Pure XXX",
        'tspov': "TSPOV",
    }
    return match.get(argument, argument)


class CXWowSpider(BaseSceneScraper):
    name = 'CXWow'
    network = 'CX Wow'

    start_urls = [
        'https://www.becomingfemme.com/',
        'https://www.pure-bbw.com/',
        'https://www.pure-ts.com/',
        'https://www.pure-xxx.com/',
        'https://www.tspov.com/',
    ]

    selector_map = {
        'title': '//div[contains(@class, "titlebox")]//h3/text()',
        'description': '//div[contains(@class, "aboutvideo")]//p/text()',
        'performers': '//ul[contains(@class, "featuredModels")]/li//span/text()',
        'date': '//div[contains(@class, "video_description")]//h4/text()',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//div[contains(@class, "videohere")]//img[contains(@src,"contentthumbs")]/@src',
        'tags': '//meta[@name="keywords"]/@content',
        'trailer': '',
        'external_id': '/trailers/(.*).html',
        'pagination': '/tour/updates/page_%s.html',

    }

    def get_scenes(self, response):
        scenes = response.xpath('//body//section[2]//div[@class="empireimg"]/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_tags(self, response):
        performers = super().get_performers(response)
        tags = self.process_xpath(response, self.get_selector_map('tags')).get()
        if tags:
            tags2 = []
            tags = tags.split(",")
            for tag in tags:
                addtag = True
                for performer in performers:
                    if performer.lower().strip() in tag.lower().strip():
                        addtag = False
                    if "movie" in tag.lower() or "photo" in tag.lower():
                        addtag = False
                    if "photo" in tag.lower():
                        addtag = False
                    if " id " in tag.lower():
                        addtag = False
                if addtag:
                    tags2.append(tag)
            return tags2


    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers.append("Christian XXX")
        return performers

    def get_image(self, response):
        image = super().get_image(response)
        if image and image not in response.url:
            return image

        image = response.xpath('//script[contains(text(), "playTrailer")]/text()')
        if image:
            image = image.get()
            image = re.search(r'(?:[^\/])image.*?[\'\"](.*?)[\'\"]', image)
            if image:
                image = image.group(1)
                return self.format_link(response, image)
        return None

    def get_trailer(self, response):
        trailer = response.xpath('//script[contains(text(), "playTrailer")]/text()')
        if trailer:
            trailer = trailer.get()
            trailer = re.search(r'(?:[^\/])file.*?[\'\"](.*?)[\'\"]', trailer)
            if trailer:
                trailer = trailer.group(1)
                return self.format_link(response, trailer)
        return None

    def get_date(self, response):
        date = response.xpath('//div[contains(@class, "video_description")]//h4/text()')
        if date:
            date = date.getall()
            date = "".join(date)
            date = date.replace(" ", "").strip()
            date = re.search(r'(\d{4}-\d{2}-\d{2})', date)
            if date:
                date = date.group(1)
                return date
        return None

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class, "video_description")]//h4/text()')
        if duration:
            total_duration = 0
            duration = duration.getall()
            duration = "".join(duration)
            duration = re.sub(r'[^a-z0-9-]', '', duration.lower())
            minutes = re.search(r'(\d+)min', duration)
            if minutes:
                minutes = int(minutes.group(1)) * 60
                total_duration = total_duration + minutes
            seconds = re.search(r'(\d+)second', duration)
            if seconds:
                seconds = int(seconds.group(1))
                total_duration = total_duration + seconds
            if total_duration:
                return str(total_duration)
        return None
