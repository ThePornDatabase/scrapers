import re
import string
from datetime import datetime
import dateparser
import scrapy
from tpdb.BaseMovieScraper import BaseMovieScraper


class AdultDVDEmpireMovieSpider(BaseMovieScraper):
    name = 'AdultDVDEmpireMovie-Filler'
    site = "Adult DVD Empire"
    days = 9999

    url = 'https://www.adultdvdempire.com'

    paginations = [
        '/all-dvds.html?page=%s&sort=current_bestseller_sorts&media=2',
        '/new-release-porn-videos.html?page=%s&media=14',
        '/best-selling-blu-ray-movies.html?sort=released&page=%s'
    ]

    selector_map = {
        'title': '//div[contains(@class,"title-rating-section")]/div/h1/text()',
        'description': '//h4[contains(@class,"synopsis")]/p/text()',
        'date': '//li/small[contains(text(),"Released")]/following-sibling::text()',
        'front': '//a[@id="front-cover"]/img/@src',
        'front_blob': True,
        'back': '//a[@id="back-cover"]/@href',
        'back_blob': True,
        'performers': '//strong[contains(text(),"Starring")]/following-sibling::a/div/u/text()',
        'tags': '//strong[contains(text(),"Categories")]/following-sibling::a/text()',
        'external_id': r'/(\d+)/',
        'studio': '//li/small[contains(text(), "Studio:")]/following-sibling::a/text()',
        'director': '//a[@label="Director"]/text()',
        'format': '//div[contains(@class, "pricing")]/h2/text()[1]',
        'length': '//li/small[contains(text(), "Length:")]/following-sibling::text()',
        'year': '//li/small[contains(text(), "Production Year:")]/following-sibling::text()',
        'rating': '//span[@class="rating-stars-avg"]/text()',
        'sku': '//li/small[contains(text(), "SKU:")]/following-sibling::text()',
        'upc': '//li/small[contains(text(), "UPC Code:")]/following-sibling::text()',
        'pagination': 'https://www.adultdvdempire.com/all-dvds.html?page=%s&sort=current_bestseller_sorts&media=2'
    }

    def start_requests(self):
        for pagination in self.paginations:
            yield scrapy.Request(url=self.get_next_page_url(self.url, self.page, pagination),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination': pagination},
                                 headers=self.headers,
                                 cookies=self.cookies)

    def parse(self, response, **kwargs):
        if response.status == 200:
            scenes = self.get_movies(response)
            count = 0
            for scene in scenes:
                count += 1
                yield scene

            if count:
                if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                    meta = response.meta
                    meta['page'] = meta['page'] + 1
                    print('NEXT PAGE: ' + str(meta['page']))
                    yield scrapy.Request(url=self.get_next_page_url(self.url, meta['page'], meta['pagination']),
                                         callback=self.parse,
                                         meta=meta,
                                         headers=self.headers,
                                         cookies=self.cookies)

    def get_next_page_url(self, url, page, pagination):
        return self.format_url(url, pagination % page)

    def get_movies(self, response):
        movies = response.xpath('//div[@class="product-card"]/div/a/@href').getall()
        for movie in movies:
            movie = movie.strip()
            if re.search(self.get_selector_map('external_id'), movie):
                yield scrapy.Request(url=self.format_link(response, movie), callback=self.parse_movie)

    def get_description(self, response):

        description = response.xpath('//h4[contains(@class,"synopsis")]/p/text()|//h4[contains(@class,"synopsis")]/following-sibling::p/text()').get()

        if description is not None:
            return description.strip()
        return ""

    def get_tags(self, response):
        if self.get_selector_map('tags'):
            tags = self.process_xpath(
                response, self.get_selector_map('tags')).getall()
            if tags:
                return self.clean_tags(list(map(lambda x: x.strip().title(), tags)))
        return []

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date.replace('Released:', '').replace('Added:', '').strip()
        else:
            date = response.xpath('//li/small[contains(text(),"Production")]/following-sibling::text()').get()
            if date:
                date = date + "-01-01"
            if not date:
                return datetime.now().isoformat()

        return dateparser.parse(date.strip()).isoformat()

    def get_rating(self, response):
        rating = super().get_rating(response)
        if rating:
            rating = float(rating) * 2
            rating = round(rating, 2)
            rating = str(rating)
        return rating

    def get_length(self, response):
        length = super().get_length(response)
        if length:
            length = length.lower()
            if "hr" in length and "min" in length:
                if re.search(r'(\d{1,2}).+?hr.+?(\d{1,2}).+?min', length):
                    length = re.search(r'(\d{1,2}).+?hr.+?(\d{1,2}).+?min', length)
                    hour = int(length.group(1))
                    minute = int(length.group(2))
                    length = str((hour * 60) + minute)
        return length

    def get_format(self, response):
        if 'format' in self.get_selector_map():
            if self.get_selector_map('format'):
                movieformat = self.process_xpath(response, self.get_selector_map('format'))
                if movieformat:
                    movieformat = list(map(lambda x: string.capwords(x.strip()), movieformat.getall()))
                    movieformat.sort()
                    movieformat = " / ".join(movieformat)
                    return movieformat

        return []

    def clean_tags(self, tags):
        cleanlist = [
            'movie',
            'vod exclusive',
        ]
        newlist = []
        for word in tags:
            if word.lower() not in cleanlist:
                newlist.append(word)
        return newlist
