import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class SitePornDudeCastingSpider(BaseSceneScraper):
    name = 'PornDudeCasting'
    network = 'Porn Dude Casting'
    parent = 'Porn Dude Casting'
    site = 'Porn Dude Casting'

    start_urls = [
        'https://porndudecasting.com',
    ]

    selector_map = {
        'title': '//h1[@class="header__nav-user-name"]/text()',
        'description': '//span[@class="desc icon"]/div/text()',
        'date': '//li[@class="model__info-item"]/span[contains(text(), "Cast")]/following-sibling::span/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="model__content"]//div[@class="model__head-name"]/text()',
        'tags': '//div[@class="btn btn--green btn--small header__login-btn"]/text()',
        'external_id': r'.*/(\d+)/',
        'trailer': '',
        'pagination': '/latest-updates/%s/?sort_by=post_date&sort_by=post_date&sort_by=post_date'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="thumb__gallery"]/div/a[@class="thumb__gallery-col"][1]/@data-href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_description(self, response):
        description = self.process_xpath(response, self.get_selector_map('description'))
        if description:
            description = description.getall()
            description = " ".join(description)
            return self.cleanup_description(description)

        return ''

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Professional Model" in tags:
            tags.remove("Professional Model")
        return tags

    def get_date(self, response):
        date = response.xpath('//div[@id="casting-block"]/div[contains(@class, "video__player")]/@data')
        if date:
            date = date.get()
            if re.search(r'(\d{2}/\d{2}/\d{2})', date):
                date = re.search(r'(\d{2}/\d{2}/\d{2})', date).group(1)
                date = self.parse_date(date, date_formats=['%m/%d/%y']).isoformat()
                return date
        date = self.process_xpath(response, self.get_selector_map('date'))
        if date:
            date = date.get()
            date = date.strip().replace(" ", " 1, ")
            return self.parse_date(date).isoformat()
        return ''

    def get_markers(self, response):
        markers = []
        durations = response.xpath('//li[contains(@class, "info-item")]/span//div[contains(@class, "time")]')
        for duration in durations:
            time = duration.xpath('./text()')
            if time:
                time = self.duration_to_seconds(time.get())
            marker = duration.xpath('./@class')
            if marker:
                marker = marker.get()
                if "time" in marker:
                    marker = re.search(r'time (.*)', marker).group(1)
                marker = string.capwords(marker)
            if time and marker:
                marking = {}
                marking['name'] = marker
                marking['start'] = time
                markers.append(marking)
        return markers

    def parse_scene(self, response):
        item = SceneItem()
        item['title'] = self.get_title(response)
        item['description'] = self.get_description(response)
        item['site'] = self.get_site(response)
        item['date'] = self.get_date(response)
        item['image'] = self.get_image(response)
        if item['image'] and "?" in item['image']:
            item['image'] = re.search(r'(.*)\?', item['image']).group(1)
        item['image_blob'] = self.get_image_blob(response)
        item['performers'] = self.get_performers(response)
        item['tags'] = self.get_tags(response)
        item['markers'] = self.get_markers(response)
        item['id'] = re.search(r'.*/(\d+)', response.xpath('//meta[@name="twitter:player"]/@content').get()).group(1)
        item['trailer'] = self.get_trailer(response)
        item['duration'] = self.get_duration(response)
        item['url'] = self.get_url(response)
        item['network'] = self.get_network(response)
        item['parent'] = self.get_parent(response)
        item['type'] = 'Scene'

        yield self.check_item(item, self.days)

    def get_duration(self, response):
        duration = response.xpath('//script[@type="application/ld+json" and contains(text(), "duration")]/text()').get()
        duration = duration.replace("\n", "").replace("\r", "").replace("\t", "").replace(" ", "").strip()
        duration = re.search(r'(PT\d+H\d+M\d+S)', duration)
        if duration:
            duration = duration.group(1)
            duration = self.duration_to_seconds(duration)
        else:
            duration = None
        return duration
