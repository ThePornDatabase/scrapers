import scrapy
import re
import dateparser

from tpdb.BaseSceneScraper import BaseSceneScraper

    # This scraper is just to fill in historical scenes from Data18 that don't exist on the "actual" sites
    # any longer.  Obviously data isn't being added, so it's just a one-time scrape for each site


class Data18Spider(BaseSceneScraper):
    name = 'Data18'

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
        
        #### Scraped 2021-07-06
        # ~ ['http://www.data18.com', '/sites/21sextreme/baby_got_balls/content.html/p=%s', 'Baby Got Balls', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/creampie_reality/content.html/p=%s', 'Creampie Reality', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/cumming_matures/content.html/p=%s', 'Cumming Matures', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/dominated_girls/content.html/p=%s', 'Dominated Girls', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/grandpas_fuck_teens/content.html/p=%s', 'Grandpas Fuck Teens', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/home_porn_reality/content.html/p=%s', 'Home Porn Reality', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/lusty_grandmas/content.html/p=%s', 'Lusty Grandmas', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/mandy_is_kinky/content.html/p=%s', 'Mandy is Kinky', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/mighty_mistress/content.html/p=%s', 'Mighty Mistress', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/pee_and_blow/content.html/p=%s', 'Pee and Blow', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/speculum_plays/content.html/p=%s', 'Speculum Plays', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/teach_me_fisting/content.html/p=%s', 'Teach Me Fisting', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/tranny_from_brazil/content.html/p=%s', 'Tranny From Brazil', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/tranny_smuts/content.html/p=%s', 'Tranny Smuts', '21Sextreme', 'Gamma Enterprises'],
        # ~ ['http://www.data18.com', '/sites/21sextreme/zoliboy/content.html/p=%s', 'Zoliboy', '21Sextreme', 'Gamma Enterprises'],
        
        # ~ ['http://www.data18.com', '/sites/brazzers/butts_and_blacks/content.html/p=%s', 'Butts and Blacks', 'Brazzers', 'mindgeek'],
        # ~ ['http://www.data18.com', '/sites/brazzers/jugfuckers/content.html/p=%s', 'Jugfuckers', 'Brazzers', 'mindgeek'],
        
        # ~ ['http://www.data18.com', '/sites/dogfart/barbie_cummings_official/content.html/p=%s', 'Barbie Cummings Official', 'Dogfart Network', 'Dogfart Network'],
        # ~ ['http://www.data18.com', '/sites/dogfart/candy_monroe_official/content.html/p=%s', 'Candy Monroe Official', 'Dogfart Network', 'Dogfart Network'],
        # ~ ['http://www.data18.com', '/sites/dogfart/katie_thomas/content.html/p=%s', 'Katie Thomas Official', 'Dogfart Network', 'Dogfart Network'],
        # ~ ['http://www.data18.com', '/sites/dogfart/ruth_blackwell_official/content.html/p=%s', 'Ruth Blackwell Official', 'Dogfart Network', 'Dogfart Network'],
        # ~ ['http://www.data18.com', '/sites/dogfart/spring_thomas/content.html/p=%s', 'Spring Thomas Official', 'Dogfart Network', 'Dogfart Network'],
        # ~ ['http://www.data18.com', '/sites/dogfart/the_minion/content.html/p=%s', 'The Minion', 'Dogfart Network', 'Dogfart Network'],
        # ~ ['http://www.data18.com', '/sites/dogfart/wife_writing/content.html/p=%s', 'Wife Writing', 'Dogfart Network', 'Dogfart Network'],
        
        # ~ ['http://www.data18.com', '/sites/bangbros/ho_in_headlights/content.html/p=%s', 'Ho in Headlights', 'Bang Bros', 'Bang Bros'],
        # ~ ['http://www.data18.com', '/sites/bangbros/moms_anal_adventure/content.html/p=%s', 'Moms Anal Adventure', 'Bang Bros', 'Bang Bros'],
        # ~ ['http://www.data18.com', '/sites/bangbros/spring_break_spycam/content.html/p=%s', 'Spring Break Spycam', 'Bang Bros', 'Bang Bros'],
        
        # ~ ['http://www.data18.com', '/sites/msp/bang_a_midget/content.html/p=%s', 'Bang a Midget', 'Wankz', 'Wankz'],
        # ~ ['http://www.data18.com', '/sites/msp/chocolate_sistas/content.html/p=%s', 'Chocolate Sistas', 'Wankz', 'Wankz'],
        # ~ ['http://www.data18.com', '/sites/msp/dp_latinas/content.html/p=%s', 'DP Latinas', 'Wankz', 'Wankz'],
        # ~ ['http://www.data18.com', '/sites/msp/fucking_machine_1000/content.html/p=%s', 'Fucking Machine 1000', 'Wankz', 'Wankz'],
        # ~ ['http://www.data18.com', '/sites/msp/tv/content.html/p=%s', 'Porncom TV', 'Wankz', 'Wankz'],
        
        # ~ ['http://www.data18.com', '/sites/screwbox/content.html/p=%s', 'Screwbox', 'Screwbox', 'Screwbox'],
        
        # ~ ['http://www.data18.com', '/sites/arp/content.html/p=%s', 'ScrapeSites', 'All Reality Pass', 'All Reality Pass'],
            #############################
            #  Included Sites in Network
            #############################
            # Bare Foot Maniacs
            # Big Cock Teen Addiction
            # Big League Facials
            # Big Tit Patrol
            # Blind Date Bangers
            # Bruthas Who Luv Muthas
            # Bus Stop Whores
            # Casting Couch Teens
            # Cheerleaders For Sex
            # College Teens Bookbang
            # Giants Black Meat White Treat
            # Horny Spanish Flies
            # Hot Chicks Perfect Tits
            # I Spy Camel Toe
            # Ice Cream Bang Bang
            # Lesbian Teen Hunter
            # Lolipop Teenies
            # Milfs In Heat
            # Mr Big Dicks Hot Chicks
            # Mr Chews Asian Beaver
            # Mr Happys Glory Hole
            # My Girlfriends Revenge
            # Natural Bush Girls
            # Panties And Fannies
            # Pimp My Black Teen
            # Please Bang My Wife
            # Round Mound Of Ass
            # See Her Squirt
            # Teeny Bopper Club
            # The Big Swallow
            # Tinys Black Adventures
            # Tits Ass And Ammo
            # Xxx Proposal
        
        # ~ ['http://www.data18.com', '/sites/pp/content.html/p=%s', 'ScrapeSites', 'Premium Pass', 'Premium Pass'],
            #############################
            #  Included Sites in Network
            #############################
            # Alanah Rae Official Site
            # Aleksa Nicole Official Site
            # Alexis Texas Official Site
            # Amy Brooke Official Site
            # Ann Marie Rios Official Site
            # Audrey Bitoni Official Site
            # Blowbanged
            # Brandy Talore Official Site
            # Breanne Benson Official Site
            # Chanel Preston Official Site
            # Diamond Foxxx Official Site
            # Eva Angelina Official Site
            # Gina Lynn Official Site
            # Her First Milf
            # Housewives Adventures
            # Jenna Haze Official Site
            # Kagney Linn Karter Official Site
            # Katsuni Official Site
            # Lexi Belle Official Site
            # Marie Mccray Official Site
            # Monique Alexander Official Site
            # Phoenix Marie Official Site
            # Sara Stone Official Site
            # Sarah Vandella Official Site
            # Shawna Lenee Official Site
            # Sindee Jennings Official Site
            # Sybian Solos
            # Tasha Reign Official Site
            # Tori Black Official Site
            # Tory Lane Official Site        
        
        # ~ ['http://www.data18.com', '/sites/rg/content.html/p=%s', 'ScrapeSites', 'Reality Gang', 'SexyHub'],
            #############################
            #  Included Sites in Network
            #############################
            # 2Chicks 1Dick
            # After Class Adventures
            # All Wives Cheat
            # Big Dicks Tight Fits
            # Big Sausage Pizza
            # Big Tit Bangers
            # Cheerleader Auditions
            # Contortionist
            # Cougar Recruits
            # Donger Brothers
            # Eat My Black Meat
            # Euro Bride Tryouts
            # First Time Wife Swappers
            # Freak Fuckers
            # Girls Hunting Girls
            # Hardcore Partying
            # How To Bang A Pornstar
            # Huge Hardons
            # Inexperienced Amateurs
            # Jr College Lesbians
            # Latina Caliente
            # Limo Patrol
            # Major Cans
            # Maximum Naturals
            # Milf Cruiser
            # Milfs Want Big Cock
            # Motor Tramps
            # Needy Wives
            # Nude Beach House
            # Reality Gang
            # Right Off The Boat
            # Sex Revenger
            # Slut Seeker
            # Tap That Onion Ass
            # Teen Hitchhikers
            # Teenage Delinquents
            # Whopper Lesbians
            # Your Moms Ass Is Tight        
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
                                 meta={'page': self.page, 'pagination':link[1], 'sitename':link[2], 'parent':link[3], 'network':link[4]},
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
        sitename = meta['sitename'].strip()
        if sitename == 'ScrapeSites':
            sitename = response.xpath('//b[contains(text(), "Site")]/following-sibling::a/text()').get()
            if sitename:
                sitename = sitename.strip()
            else:
                sitename = "No Site Available"
        return sitename.title()


    def get_parent(self, response):
        meta = response.meta
        return meta['parent']


    def get_network(self, response):
        meta = response.meta
        return meta['network']

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if not date:
            date = response.xpath('//span[contains(text(),"Release date")]/i/text()').get()
            if date.lower() == "unknown":
                date = "1970-01-01T00:00:00"
                return date
        date.replace('Released:', '').replace('Added:', '').strip()
        return dateparser.parse(date.strip()).isoformat()
