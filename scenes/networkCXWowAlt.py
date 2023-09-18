import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'pornstarbts': "Pornstar BTS",
        'sissypov': "Sissy POV",
    }
    return match.get(argument, argument)


class CXWowSpiderAlt(BaseSceneScraper):
    name = 'CXWowAlt'
    network = 'CX Wow'

    start_urls = [
        'https://pornstarbts.com',
        'https://sissypov.com',
    ]

    selector_map = {
        'title': '//div[@class="videoDetails clear"]/h3/text()',
        'description': '//div[@class="videoDetails clear"]/p/text()',
        'performers': '//li[@class="update_models"]/a/text()',
        'date': '//span[contains(text(), "Date")]/following-sibling::text()',
        'date_formats': ['%B %d, %Y'],
        'image': '//div[@class="video_area"]//img/@src0_3x|//div[@class="video_area"]//img/@src0_2x|//div[@class="video_area"]//img/@src0_1x',
        'tags': '//li[contains(text(), "Tags")]/following-sibling::li/a/text()',
        'trailer': '',
        'external_id': '/trailers/(.*).html',
        'pagination': '/tour/categories/movies/%s/latest/',

    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="item"]')
        for scene in scenes:
            duration = scene.xpath('.//i[contains(@class, "fa-clock")]/following-sibling::text()')
            if duration:
                duration = duration.get()
                duration = re.search(r'((?:\d{1,2}\:)?\d{2}\:\d{2})', duration)
                if duration:
                    meta['duration'] = self.duration_to_seconds(duration.group(1))
            scene = scene.xpath('./div/a/@href').get()
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))

    def get_performers(self, response):
        performers = super().get_performers(response)
        performers.append("Christian XXX")
        return performers

    def get_duration(self, response):
        duration = response.xpath('//div[@class="videoInfo clear"]//p[contains(text(), "of video")]/text()')
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

    def get_image(self, response):
        image = super().get_image(response)
        if image in response.url:
            image = response.xpath('//script[contains(text(), "video_content")]/text()')
            if image:
                image = image.get()
                poster = re.search(r'poster=[\'\"](.*?)[\'\"]', image)
                if poster:
                    poster = poster.group(1)
                if not poster:
                    poster = re.search(r'src0_3x=[\'\"](.*?)[\'\"]', image)
                    if poster:
                        poster = poster.group(1)
                if not poster:
                    poster = re.search(r'src0_2x=[\'\"](.*?)[\'\"]', image)
                    if poster:
                        poster = poster.group(1)
                if not poster:
                    poster = re.search(r'src0_1x=[\'\"](.*?)[\'\"]', image)
                    if poster:
                        poster = poster.group(1)
                if poster:
                    image = self.format_link(response, poster)
        return image

    def get_trailer(self, response):
        trailer = response.xpath('//script[contains(text(), "video_content")]/text()')
        if trailer:
            trailer = trailer.get()
            if "video src" in trailer:
                trailer = re.search(r'video src=[\'\"](.*?)[\'\"]', trailer)
                if trailer:
                    return self.format_link(response, trailer.group(1))
        return None
