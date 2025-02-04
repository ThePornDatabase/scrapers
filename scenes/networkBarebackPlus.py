import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkBarebackPlusSpider(BaseSceneScraper):
    name = 'BarebackPlus'
    parent = 'BarebackPlus'
    network = 'BarebackPlus'

    start_urls = [
        'https://barebackplus.com',
    ]

    selector_map = {
        'description': '//div[@class="textDescription"]/p/text()',
        'title': '//div[contains(@class,"title-updates-infos")]/h2//text()',
        'date': '//div[@class="releasedate"]/text()',
        're_date': r'(\w+ \d{1,2}, \d{4})',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@class="grid-model-list"]/div[contains(@class, "grid-item")]//h4/text()',
        'tags': '//div[@class="update_tags"]/a/span/text()',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/videos?page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="grid-vid-item"]/div[1]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    # ~ def get_title(self, response):
        # ~ series = response.xpath('//div[contains(@class, "titlePlayer")]//h2[contains(@class, "serie_name")]/text()')
        # ~ if series:
            # ~ series = series.get()
            # ~ series = self.cleanup_title(series) + " - "
        # ~ else:
            # ~ series = ""

        # ~ title = response.xpath('//div[contains(@class, "titlePlayer")]/h2/text()')
        # ~ if title:
            # ~ title = title.get()
            # ~ title = self.cleanup_title(title)
        # ~ else:
            # ~ title = ""

        # ~ return (series + title).replace("|", ":")

    def get_duration(self, response):
        duration = response.xpath('//div[@class="releasedate"]/text()')
        if duration:
            tot_dur = 0
            duration = duration.get()
            duration = re.sub(r'[^a-z0-9]+', '', duration.lower())
            minutes = re.search(r'(\d+)min', duration)
            if minutes:
                tot_dur = tot_dur + int(minutes.group(1)) * 60
            seconds = re.search(r'(\d+)sec', duration)
            if seconds:
                tot_dur = tot_dur + int(seconds.group(1))

            if tot_dur:
                return str(tot_dur)
        return None

    def get_site(self, response):
        site = response.xpath('//div[@class="title-updates"]/div[contains(@class, "updates-logo")]/a/@href')
        if site:
            site = re.sub(r'[^a-zA-Z0-9]+', '', site.get())
            return site
        return "BarebackPlus"

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "Gay" not in tags:
            tags.append("Gay")
        return tags
