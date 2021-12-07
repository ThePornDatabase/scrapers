import scrapy

from tpdb.BasePerformerScraper import BasePerformerScraper


class SiteAdultAuditionsPerformerSpider(BasePerformerScraper):
    selector_map = {
        'name': '//h2/text()',
        'image': '//div[@class="carousel-inner"]/div[1]/img/@src',
        'nationality': '//li/span[contains(text(), "Nationality")]/following-sibling::text()',
        'height': '//li/span[contains(text(), "Height")]/following-sibling::text()',
        'tattoos': '//li/span[contains(text(), "Tattoos")]/following-sibling::text()',
        'bio': '//li/span[contains(text(), "Specialities")]/following-sibling::text()',
        'pagination': '/models.php?p=%s&i=20&a=1&f=1&c=72&s=&o=1',
        'external_id': r'model/(.*)/'
    }

    name = 'AdultAuditionsPerformer'
    network = 'Adult Auditions'

    start_urls = [
        'https://adultauditions.co',
    ]

    def start_requests(self):
        url = 'https://adultauditions.co'
        yield scrapy.Request(url, callback=self.start_requests_2, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 callback=self.parse,
                                 meta={'page': self.page},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def get_gender(self, response):
        return 'Female'

    def get_performers(self, response):
        performers = response.xpath('//div[@class="col-sm-3"]/a/@href').getall()
        for performer in performers:
            if performer[0] == ".":
                performer = performer[1:]
            yield scrapy.Request(
                url=self.format_link(response, performer),
                callback=self.parse_performer
            )

    def get_image(self, response):
        image = super().get_image(response)
        image = image.replace("/./", "/")
        return image
