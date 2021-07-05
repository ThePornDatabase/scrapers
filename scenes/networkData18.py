import scrapy
import re


from tpdb.BaseSceneScraper import BaseSceneScraper

    # This scraper is just to fill in historical scenes from Data18 that don't exist on the "actual" sites
    # any longer.  Obviously data isn't being added, so it's just a one-time scrape for each site


class Data18Spider(BaseSceneScraper):
    name = 'Data18'


    # Note: These scenes could all have been pulled from one API location, but the returned JSON doesn't include any
    #       site or category information, so I needed to split them up like this to return the associated site per scene
    #       I checked available scenes as of writing and there were not any duplicate ids between sites

    start_urls = [
    
        #### Scraped 2021-07-05
        # ~ ['http://www.data18.com', '/sites/21sextury/bootyfull_babes/content.html/p=%s', 'Bootyfull Babes', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/busty_fever/content.html/p=%s', 'Busty Fever', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/daily_sex_dose/content.html/p=%s', 'Daily Sex Dose', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/dp_overload/content.html/p=%s', 'DP Overload', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/enslaved_gals/content.html/p=%s', 'Enslaved Gals', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/intermixed_sluts/content.html/p=%s', 'Intermixed Sluts', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/lust_for_anal/content.html/p=%s', 'Lust for Anal', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/lusty_busty_chix/content.html/p=%s', 'Lusty Busty Chix', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/only_swallows/content.html/p=%s', 'Only Swallows', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/oral_quickies/content.html/p=%s', 'Oral Quickies', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/sex_city_asia/content.html/p=%s', 'Sex City Asia', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/sophie_moone_official/content.html/p=%s', 'Sophie Moone Official Site', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/squirting_files/content.html/p=%s', 'Squirting Files', '21Sextury', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextury/teen_bitch_club/content.html/p=%s', 'Teen Bitch Club', '21Sextury', 'Gamma Enterprises'],
    ]

    selector_map = {
        'title': '//h1/text()',
        'description': '//b[contains(text(), "Story")]/following-sibling::text()',
        'date': '//span[contains(text(),"Release date")]/a/text()',
        'image': '//div[@id="moviewrap"]/img/@src',
        'performers': '//b[contains(text(),"Starring")]/following-sibling::a/text()',
        'tags': '//b[contains(text(),"Categories")]/following-sibling::a/text()',
        'external_id': '\/(\d+)$',
        'trailer': '//video/source/@src',
    }

    def start_requests(self):
        if not hasattr(self, 'start_urls'):
            raise AttributeError('start_urls missing')

        if not self.start_urls:
            raise AttributeError('start_urls selector missing')

        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link[0], self.page, link[1]),
                                 callback=self.parse,
                                 meta={'page': self.page, 'pagination':link[1], 'site':link[2], 'parent':link[3], 'network':link[4]},
                                 headers=self.headers,
                                 cookies=self.cookies)

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
                yield scrapy.Request(url=self.get_next_page_url(response.url, meta['page'], meta['pagination']),
                                     callback=self.parse,
                                     meta=meta,
                                     headers=self.headers,
                                     cookies=self.cookies)

    def get_next_page_url(self, base, page, pagination):
        return self.format_url(base, pagination % page)


    def get_scenes(self, response):
        meta=response.meta
        scenes = response.xpath('//p[@class="line1"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)
            
    def get_title(self, response):
        title = self.process_xpath(
            response, self.get_selector_map('title')).get()
        if title:
            return title.strip().title()
        return ''                    


    def get_site(self, response):
        meta = response.meta
        return meta['site']


    def get_parent(self, response):
        meta = response.meta
        return meta['parent']


    def get_network(self, response):
        meta = response.meta
        return meta['network']
