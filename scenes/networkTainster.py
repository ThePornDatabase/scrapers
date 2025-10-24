import re
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteTainsterSpider(BaseSceneScraper):
    name = 'Tainster'

    selector_map = {
        'title': '//h1[@class="title--3"]/text()',
        'description': '//div[contains(@class,"accordion__content")]/h5/following-sibling::p//text()',
        'date': '//div[contains(@class,"accordion__content")]//td[contains(text(), "Date added")]/following-sibling::td/text()',
        'date_formats': ['%d %B %Y'],
        'image': '//div[contains(@class,"show---link")]/img/@src',
        'performers': '//figcaption[contains(@class,"girls-item--content")]/h4/text()',
        'trailer': '',
        'external_id': r'movie/(\d+)/',
        'pagination': '',
        'type': 'Scene',
    }

    start_urls = [
        ['https://www.sinx.com/channel/Allwam/all', 'ALLWAM'],
        ['https://www.sinx.com/channel/Cumsquad/all', 'Cumsquad'],
        ['https://www.sinx.com/channel/Eromaxx-Liveshow/all', 'Eromaxx Liveshow'],
        ['https://www.sinx.com/channel/Eromaxx-Vintage/all', 'Eromaxx Vintage'],
        ['https://www.sinx.com/channel/Fullyclothed-Pissing/all', 'Fullyclothed Pissing'],
        ['https://www.sinx.com/channel/Fullyclothed-Sex/all', 'Fullyclothed Sex'],
        ['https://www.sinx.com/channel/Leony-Aprill/all', 'Leony Aprill'],
        ['https://www.sinx.com/channel/Messy-Wrestling/all', 'Messy Wrestling'],
        ['https://www.sinx.com/channel/My-Fetish/all', 'My-Fetish'],
        ['https://www.sinx.com/channel/Orgasmatics/all', 'Orgasmatics'],
        ['https://www.sinx.com/channel/Party-Hardcore/all', 'Party Hardcore'],
        ['https://www.sinx.com/channel/Peesquad/all', 'Peesquad'],
        ['https://www.sinx.com/channel/Pissing-In-Action/all', 'Pissing In Action'],
        ['https://www.sinx.com/channel/Pornstars-At-Home/all', 'Pornstars At Home'],
        ["https://www.sinx.com/channel/Slime-Wave/all", 'Slimewave'],
        ["https://www.sinx.com/channel/Tyrannized/all", 'Tyrannized'],
        ['https://www.sinx.com/channel/Upper-Class-Fuck-Fest/all', 'Upper-Class-Fuck-Fest'],
        ['https://www.sinx.com/channel/Upper-Class-Fuck-Fest-Vol-2/all', 'Upper-Class-Fuck-Fest-Vol-2'],
        ['https://www.sinx.com/channel/Lezboxx/all', 'Lezboxx'],
        ['https://www.sinx.com/channel/Lezboxx-Vol-2/all', 'Lezboxx-Vol-2'],
        ['https://www.sinx.com/Leather-Chronicle', 'Leather-Chronicle'],
        ['https://www.sinx.com/X-Sorority', 'X Sorority'],
        ['https://www.sinx.com/channel/Backstage-Bangers/all', 'Backstage Bangers'],
        ['https://www.sinx.com/Big-Tits-On-Screen', 'Big Tits On Screen'],
        ['https://www.sinx.com/channel/Bash-Bastards/all', 'Bash Bastards'],
        ['https://www.sinx.com/Sex-In-Jeans', 'Sex In Jeans'],
        ['https://www.sinx.com/Cutie-By-Nature', 'Cutie-By-Nature'],
        ['https://www.sinx.com/channel/Pervy-Ones/all', 'Pervy Ones'],
        ['https://www.sinx.com/Fisting-In-Action', 'Fisting In Action'],
        ['https://www.sinx.com/Golden-Shower-Power', 'Golden Shower Power'],
        ['https://www.sinx.com/Golden-Shower-Power-Vol-2', 'Golden Shower Power'],
        ['https://www.sinx.com/Golden-Shower-Power-Vol-3', 'Golden Shower Power'],
        ['https://www.sinx.com/Golden-Shower-Power-Vol-4', 'Golden Shower Power'],
    ]


    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)

    def start_requests(self):
        meta = {}
        meta['page'] = self.page

        for site in self.start_urls:
            link = site[0]
            meta['site'] = site[1]
            meta['parent'] = site[1]
            meta['network'] = "Tainster"
            if "/all" in link or "sexualOrientation" in link:
                yield scrapy.Request(link, callback=self.start_requests_2, meta=meta, headers=self.headers, cookies=self.cookies)
            else:
                meta['pagination'] = link + "?page=%s"
                yield scrapy.Request(link, callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def start_requests_2(self, response):
        meta = response.meta
        links = response.xpath('//a[@class="item--link"]/@href').getall()
        for link in links:
            meta['pagination'] = link + "?page=%s"
            yield scrapy.Request(url=self.get_next_page_url("https://www.sinx.com/", self.page, meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def parse(self, response, **kwargs):
        scenes = self.get_scenes(response)
        count = 0
        for scene in scenes:
            count += 1
            yield scene

        if count:
            if 'page' in response.meta and response.meta['page'] < self.limit_pages:
                meta = response.meta
                meta['page'] = meta['page'] + 1
                print('NEXT PAGE: ' + str(meta['page']))
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']), callback=self.parse, meta=meta, headers=self.headers, cookies=self.cookies)

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="video_item--player"]/a[1]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//div[contains(@class,"accordion__content")]//td[contains(text(), "Runtime")]/following-sibling::td/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+)', duration)
            if duration:
                duration = str(int(duration.group(1)) * 60)
                return duration
        return None

    def get_tags(self, response):
        taglist = response.xpath('//div[contains(@class,"video-page--tag")]//a/span/text()').getall()
        tags = []
        for tag in taglist:
            tag = tag.replace("#", "")
            tag = re.sub(r"([A-Z])", r" \1", tag)
            tags.append(tag)
        return tags
