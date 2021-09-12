import re
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class LethalPassSpider(BaseSceneScraper):
    name = 'LethalPass'
    network = 'HOH Limited'
    parent = 'LethalPass'

    start_urls = [
        'https://www.lethalpass.com'
        # ~ --------- Added for search compatibility
        # ~ 'https://www.asianchickslikeblackdicks.com',
        # ~ 'https://www.bigjuicyjuggs.com',
        # ~ 'https://www.bigleaguesquirters.com',
        # ~ 'https://www.cashforchunkers.com',
        # ~ 'https://www.cougarscravekittens.com',
        # ~ 'https://www.couplesbangthebabysitter.com',
        # ~ 'https://www.fuckmymommy.com',
        # ~ 'https://www.gloryholeadmissions.com',
        # ~ 'https://www.hugecockgloryholes.com',
        # ~ 'https://www.jawdroppingasses.com',
        # ~ 'https://www.lethalcougars.com',
        # ~ 'https://www.lethalcreampies.com',
        # ~ 'https://www.lethalinterracial.com',
        # ~ 'https://www.mystepdaughteratemyass.com',
        # ~ 'https://www.naturalbornswallowers.com',
        # ~ 'https://www.seducedbyalesbian.com',
        # ~ 'https://www.spinonmycock.com',
        # ~ 'https://www.yourmomtossedmysalad',
    ]

    selector_map = {
        'title': '//div[@class="title"]/h1/text()',
        'description': '//div[@class="description"]/p/text()',
        'performers': '//a[@class="model"]/span/text()',
        'date': '//span[contains(text(),"Added")]/text()',
        'image': '//a[@class="noplayer"]/img/@src',
        'tags': '//span[@class="label"]/following-sibling::a/text()',
        'external_id': r'lethalpass.*\/(.+?)$',
        'trailer': '',
        'pagination': '/videos?p=%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="scene"]/div/div/a/@href').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if date:
            date = re.search(r'Added\ ?(.*)', date).group(1)
        else:
            date = date.today()
        return dateparser.parse(date.strip()).isoformat()

    def get_site(self, response):
        site = response.xpath('//div[@class="pdSRC"]/p/a/text()').get()
        if site:
            sitetest = response.xpath('//div[@class="pdSRC"]/p/text()').get()
            if sitetest:
                if "site" not in sitetest.lower():
                    site = "LethalPass"
            return site
        return super().get_site(response)

    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get().strip()
        if not title:
            dvd = response.xpath('//div[@class="bc"]/span[2]/following-sibling::a/text()').get().strip()
            title = response.xpath('//div[@class="bc"]/span[3]/following-sibling::text()').get().strip()
            title = dvd + ": " + title
            title = title.strip()
        return title

    def get_id(self, response):
        search = re.search(self.get_selector_map(
            'external_id'), response.url, re.IGNORECASE)
        search = search.group(1)
        if re.match(r'.*(\d+)$', search):
            search = re.search(r'(\d+)$', search.strip()).group(1)
            return search.strip()
        if re.match(r'.*(\d+)', search):
            search = re.search(r'(\d+)$', search.strip()).group(1)
            if len(search) > 4:
                return search.strip()

        return search
