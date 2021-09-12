import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteBrokenBabesSpider(BaseSceneScraper):
    name = 'BrokenBabes'
    network = 'Broken Babes'
    parent = 'Broken Babes'
    site = 'Broken Babes'

    start_urls = [
        'https://www.brokenbabes.com'
    ]

    selector_map = {
        'title': '//div[@class="scene-container"]/h1/text()',
        'description': '//section[@class="scene"]/p/text()',
        'performers': '//meta[@name="keywords"]/@content',
        'date': '//meta[@itemprop="datePublished"]/@content',
        'image': '//meta[@itemprop="thumbnailUrl"]/@content',
        'tags': '//meta[@name="keywords"]/@content',
        'site': '//a[contains(@class,"source")]/text()',
        'external_id': r'updates\/(.*)\.html',
        'trailer': '//meta[@itemprop="contentURL"]/@content',
        'pagination': '/categories/updates_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//a[contains(@href,"/updates/")]/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'site': 'Broken Babes'})

    def get_performers(self, response):
        performers = []
        performerkeywords = self.process_xpath(
            response, self.get_selector_map('performers')).get()
        if performerkeywords:
            performerpointer = 0
            performerlist = performerkeywords.split(",")
            for performer in performerlist:
                if performerpointer == 1:
                    performers.append(performer)
                if "Broken Babes" in performer:
                    performerpointer = 1

        return list(map(lambda x: x.strip(), performers))

    def get_tags(self, response):
        tags = []
        tagkeywords = self.process_xpath(
            response, self.get_selector_map('tags')).get()
        if tagkeywords:
            tagpointer = 0
            taglist = tagkeywords.split(",")
            for tag in taglist:
                if "Broken Babes" in tag:
                    tagpointer = 1
                if tagpointer == 0:
                    if "HD" not in tag and "Movies" not in tag and "Photos" not in tag and "Pornstars" not in tag:
                        tags.append(tag.replace("...", ""))

        return list(map(lambda x: x.strip(), tags))

    def get_trailer(self, response):
        return self.format_link(response, super().get_trailer(response))
