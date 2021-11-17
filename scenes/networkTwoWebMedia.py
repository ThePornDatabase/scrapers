import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkTwoWebMediaSpider(BaseSceneScraper):
    name = 'TwoWebMedia'
    network = 'Two Web Media'

    start_urls = [
        'https://www.boppingbabes.com',
        'https://www.downblousejerk.com',
        'https://www.upskirtjerk.com',
        'https://www.wankitnow.com',
    ]

    selector_map = {
        'title': '//h1[@class="page_title"]/text()',
        'description': '//div[@class="post_excerpt"]/p/text()',
        'date': '',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//span[contains(@class,"meta_modelcategory")]/a/text()',
        'tags': '//span[contains(@class,"meta_videotag")]/a/text()',
        'external_id': r'.*\/(.*?)\/',
        'trailer': '//script[contains(text(),"jwplayer.key")]/text()',
        're_trailer': r'.*(http.*?\.mp4).*',
        'pagination': '/videoentry/page/%s/'
    }

    def get_next_page_url(self, base, page):
        if "boppingbabes" in base:
            pagination = '/v2/videoentry/page/%s/'
        else:
            pagination = '/videoentry/page/%s/'
        return self.format_url(base, pagination % page)

    def get_scenes(self, response):
        scenes = response.xpath('//div[contains(@class,"loop_content")]')
        for scene in scenes:
            date = scene.xpath('.//span[@class="meta_date"]/text()').get()
            if date:
                date = self.parse_date(date).isoformat()
            else:
                date = self.parse_date('today').isoformat()
            scene = scene.xpath('.//h2/a/@href').get()
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date})

    def get_title(self, response):
        title = self.process_xpath(response, self.get_selector_map('title'))
        if title:
            title = self.get_from_regex(title.get(), 're_title')
        title = title.replace("'", "")
        title = title.replace(u"\u2019", "")
        title = title.replace(" & ", " and ")
        title = re.sub(r'&#\d+;', '', title)
        title = re.sub(r'[^a-zA-Z0-9-:;.,_() ]', ' ', title)
        return self.cleanup_title(title).replace("  ", " ")

    def get_image(self, response):
        imageurl = super().get_image(response)
        if not imageurl:
            image = response.xpath('//div[contains(@class,"wpfp_custom_background")]/@style')
            if image:
                image = image.get()
                image = re.search(r'.*(http.*?\.jpg).*', image)
                if image:
                    imageurl = image.group(1)
        return imageurl.strip()

    def get_site(self, response):
        site = super().get_site(response)
        if "wankitnow" in site:
            return "Wank It Now"
        if "boppingbabes" in site:
            return "Bopping Babes"
        if "downblousejerk" in site:
            return "Downblouse Jerk"
        if "upskirtjerk" in site:
            return "Upskirt Jerk"
        return site

    def get_parent(self, response):
        site = super().get_parent(response)
        if "wankitnow" in site:
            return "Wank It Now"
        if "boppingbabes" in site:
            return "Bopping Babes"
        if "downblousejerk" in site:
            return "Downblouse Jerk"
        if "upskirtjerk" in site:
            return "Upskirt Jerk"
        return site
