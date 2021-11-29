import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class OrgasmAbuseSpider(BaseSceneScraper):
    name = 'OrgasmAbuse'
    network = 'Orgasm Abuse'
    parent = 'Orgasm Abuse'
    site = 'Orgasm Abuse'

    start_urls = [
        'https://www.orgasmabuse.com/'
    ]

    selector_map = {
        'title': '//div[contains(@class,"detail-content-main")]//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'performers': '//div[contains(@class,"detail-content-main")]//a[contains(@href,"?mid")]/text()',
        'date': '',
        'image': '//div[contains(@class,"video-cover")]/@style',
        're_image': r'url\(//(.*.jpe?g)',
        'tags': '//div[@class="pb-5"]//a[contains(@href, "?gid") or contains(@href,"?lid")]/text()',
        'external_id': r'/video/(\d+)/',
        'trailer': '',
        'pagination': '/browsevideos?lt=latest&page=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div/a[contains(@href,"/video/")]')
        # ~ scenes = list(dict.fromkeys(scenes))
        for scene in scenes:
            date = scene.xpath('.//div[contains(@class,"text-gray-600")]/div[contains(@class,"text-right")]/text()').get()
            if date:
                date = self.parse_date(date.strip()).isoformat()
            else:
                date = self.parse_date('today').isoformat()
            trailer = scene.xpath('./video-thumb/@video')
            if trailer:
                trailer = trailer.get().strip()
            else:
                trailer = ''
            scene = scene.xpath('./@href').get()
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta={'date': date, 'trailer': trailer})

    def get_image(self, response):
        image = super().get_image(response)
        if "orgasmabuse.com/img." in image:
            image = "https://" + image.replace("https://www.orgasmabuse.com/", "")
        return image
