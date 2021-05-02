import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class VnaNetworkSpider(BaseSceneScraper):
    name = 'WowNetwork'
    network = 'Wow Girls'

    start_urls = [
        'https://www.wowpornblog.com/',
        'https://www.wowgirlsblog.com/',
        'https://www.ultrafilms.xxx/',
    ]

    selector_map = {
        'title': '//meta[@property="og:title"]/@content',
        'description': '//meta[@property="og:description"]/@content',
        'date': '//div[@itemprop="datePublished"]/text()',
        'image': '//meta[@property="og:image"]/@content',
        'performers': '//div[@itemprop="actor"]/ul/li/a/text()',
        'tags': '//div[@itemprop="keywords"]/ul/li/a/text()',
        'external_id': '/([a-z0-9-]+?)/?$',
        'trailer': '//div[@class="video-embed"]/div/@data-item',
        'pagination': '/category/movies/page/%s/?filtre=date'
    }

    def get_scenes(self, response):
        scenes = response.css('.listing-videos li a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        site = response.xpath('//span[@itemprop="name"]/text()').extract_first()
        return site

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            return list(map(lambda x: x.replace(' Movies', '').strip(), tags))
        return []

    def get_trailer(self, response):
        if 'trailer' in self.get_selector_map() and self.get_selector_map('trailer'):
            return self.process_xpath(
                response, self.get_selector_map('trailer')).get().split('src":"', 1)[1].split('","type', 1)[0].replace(
                '\\', '').strip()
        return ''
