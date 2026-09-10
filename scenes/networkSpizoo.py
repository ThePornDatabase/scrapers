import re
import string
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'creamher': "Cream Her",
        'firstclasspov': "First Class POV",
        'gothgirlfriendsvip': "Goth Girlfriends VIP",
        'mrluckypov': "Mr Lucky POV",
        'mrluckyraw': "Mr Lucky Raw",
        'mrluckyvip': "Mr Lucky VIP",
        'rawattack': "Raw Attack",
        'realsensual': "Real Sensual",
        'spizoo': "Spizoo",
    }
    return match.get(argument, argument)


class SpizooSpider(BaseSceneScraper):
    name = 'Spizoo'
    network = "Spizoo"

    custom_scraper_settings = {
        'TWISTED_REACTOR': 'twisted.internet.asyncioreactor.AsyncioSelectorReactor',
        'DOWNLOAD_HANDLERS': {
            'http': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
            'https': 'scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler',
        },
        'PLAYWRIGHT_LAUNCH_OPTIONS': {'headless': True},
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60000,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
    }

    start_urls = [
        'https://www.creamher.com/',
        'https://firstclasspov.com/',
        'https://www.gothgirlfriendsvip.com/',
        'https://mrluckypov.com/',
        'https://mrluckyraw.com/',
        'https://mrluckyvip.com/',
        'https://rawattack.com/',
        'https://realsensual.com/',
        'https://www.spizoo.com/',
    ]

    selector_map = {
        'title': '/',
        'description': '',
        'date': "//p[@class='date']/text()",
        'image': '//video/@poster|//div[@id="hpromo"]/a/img[contains(@src,".jpg")]/@src',
        'image_blob': True,
        'performers': '//div[@class="col-12"]//a[contains(@href, "/models")]/@title|//div[@class="col-3"]//a[contains(@href, "/models")]/@title|//span[@class="update_models"]/a/text()',
        'tags': '//a[contains(@class,"category-tag")]/@title|//a[contains(@href,"/categories/")]/text()',
        'external_id': r'/updates/(.*)\.html$',
        'duration': '//h4[contains(text(), "Length")]/following-sibling::p/text()|//h2[contains(text(), "Length")]/following-sibling::p/text()',
        'trailer': '',  # Hashed and tokened link.  Will be no good later
        'pagination': '/categories/movies_%s_d.html',
        'pagination_gothgirlfriendsvip': '/categories/videos_%s_d.html',
    }

    # These sites never fire the 'load' event, so Playwright's default navigation
    # wait times out on every page.  Wait for the DOM instead, which is all the
    # content we scrape anyway.
    goto_kwargs = {'wait_until': 'domcontentloaded'}
    domready_sites = ["mrluckyvip", "gothgirlfriendsvip"]

    async def start(self):
        for link in self.start_urls:
            meta = {'page': self.page, 'playwright': True}
            if any(x in link for x in self.domready_sites):
                meta['playwright_page_goto_kwargs'] = dict(self.goto_kwargs)
            yield scrapy.Request(
                url=self.get_next_page_url(link, self.page),
                callback=self.parse,
                meta=meta,
                headers=self.headers,
                cookies=self.cookies,
            )

    def get_scenes(self, response):
        if "mrluckyvip" in response.url:
            scenes = response.xpath('//div[@class="thumb-pic"]//a/@href').getall()
        elif any(x in response.url for x in ["creamher", "spizoo", "gothgirlfriendsvip"]):
            scenes = response.xpath('//div[@class="thumb-pic"]/a/@href').getall()
        elif "mrluckyraw" in response.url:
            scenes = response.xpath("//div[@class='thumb-title']/a/@href").getall()
        elif "realsensual" in response.url:
            scenes = response.xpath("//div[@class='item']/a/@href").getall()
        elif "rawattack" in response.url or "mrluckypov" in response.url or "firstclasspov" in response.url:
            scenes = response.xpath("//div[contains(@class, 'thumb-pic')]/a[1]/@href").getall()
        else:
            scenes = response.xpath("//a[@data-event='106']/@href").getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                meta = {'playwright': True}
                if any(x in response.url for x in self.domready_sites):
                    meta['playwright_page_goto_kwargs'] = dict(self.goto_kwargs)
                yield scrapy.Request(
                    url=self.format_link(response, scene),
                    callback=self.parse_scene,
                    meta=meta,
                )

    def get_title(self, response):
        matches = ["spizoo", "mrluckyraw", "creamher", "gothgirlfriendsvip"]
        if any(x in response.url for x in matches):
            titlexpath = '//div[@class="title"]/h1/text()'
        if "mrluckyvip" in response.url:
            titlexpath = '//div[@class="title-trailer"]/h2/text()|//div[@class="trailer-title"]/h2/text()'
        matches = ["firstclasspov", "mrluckypov"]
        if any(x in response.url for x in matches):
            titlexpath = '//section[@id="scene"]/div/div/div/h1/text()|//div[@class="title"]/h1/text()'
        if "rawattack" in response.url:
            titlexpath = '//title/text()'
        if "realsensual" in response.url:
            titlexpath = '//h2[contains(@class,"titular")]/text()'
        return response.xpath(titlexpath).get().strip()

    def get_description(self, response):
        if "mrluckyvip" in response.url:
            descriptionxpath = '//div[@class="description-trailer"]/text()|//div[@class="trailer-description"]/text()'
        elif "rawattack" in response.url:
            descriptionxpath = '//section[@id="sceneInfo"]/div/div/div/p/text()'
        elif "realsensual" in response.url:
            descriptionxpath = '//p[@class="description-scene"]/text()'
        else:
            descriptionxpath = '//p[@class="description"]/text()'
        description = response.xpath(descriptionxpath)
        if description:
            return description.get().strip()
        return ""

    def get_performers(self, response):
        performers = super().get_performers(response)
        if "mrluckyvip" in response.url:
            # The page repeats the cast in two blocks, so drop the repeats
            performers = list(dict.fromkeys(performers))
        return performers

    def get_site(self, response):
        return match_site(super().get_site(response))

    def get_parent(self, response):
        return match_site(super().get_parent(response))

    def get_next_page_url(self, base, page):
        if "gothgirlfriendsvip" in base:
            return self.format_url(base, self.get_selector_map('pagination_gothgirlfriendsvip') % page)
        if page == 1:
            return base + 'categories/Movies.html'
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_tags(self, response):
        tags = super().get_tags(response)
        if "creamher" in response.url:
            tags = response.xpath('//div[@class="categories-holder"]/a[contains(@class,"category-tag")]/text()').getall()
            tags = list(map(lambda x: string.capwords(x.strip()), tags))
        # Some sites match the category links twice over, so drop the repeats
        tags = list(dict.fromkeys(filter(None, tags)))
        return tags
