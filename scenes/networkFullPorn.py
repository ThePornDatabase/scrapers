import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper
from datetime import date
from urllib.parse import urlparse
import tldextract

import re


def match_site(argument):
    match = {
        'analbbc': 'Anal BBC',
        'analized': 'Analized',
        'analviolation': 'Anal Violation',
        'baddaddypov': 'Bad Daddy POV',
        'badfamilypov': 'Bad Family POV',
        'badmommypov': 'Bad Mommy POV',
        'mommyjoi': 'Mommy JOI',
        'badsisterpov': 'Bad Sister POV',
        'sisterjoi': 'Sister JOI',
        'daughterjoi': 'Daughter JOI',
        'downtofuckdating': 'DTF Dating',
        'dtfsluts': 'DTF Sluts',
        'girlfaction': 'Girl Faction',
        'hergape': 'Her Gape',
        'homemadeanalwhores': 'Homemade Anal Whores',
        'jamesdeen': 'James Deen',
        'mugfucked': 'Mug Fucked',
        'onlyprince': 'Only Prince',
        'pervertgallery': 'Pervert Gallery',
        'povperverts': 'POV Perverts',
        'teenageanalsluts': 'Teenage Anal Sluts',
        'twistedvisual': 'Twisted Visual',
        'yourmomdoesanal': 'Your Mom Does Anal',
        'yourmomdoesporn': 'Your Mom Does Porn',
    }
    return match.get(argument, '')
    

class FullPornNetworkSpider(BaseSceneScraper):
    name = 'FullPorn'
    network = 'Full Porn Network'

    # Recently several of the sites have put their scene info behind paywalls
    start_urls = [
        #'https://analbbc.com',
        'https://analized.com',
        #'https://analviolation.com',
        #'https://baddaddypov.com',
        'https://badfamilypov.com',
        'https://downtofuckdating.com/',
        'https://dtfsluts.com',
        'https://girlfaction.com',
        #'https://hergape.com',
        #'https://homemadeanalwhores.com',
        'https://jamesdeen.com',
        'https://mugfucked.com',
        'https://onlyprince.com',
        'https://pervertgallery.com',
        'https://povperverts.net',
        #'https://teenageanalsluts.com',
        'https://twistedvisual.com',
        #'https://yourmomdoesanal.com',
        'https://yourmomdoesporn.com',
    ]

    selector_map = {
        'title': "//h4[contains(@class, 'text-center')]/text()",
        'description': "//p[contains(@class, 'hide-for-small-only')]/text()",
        'performers': "//div[@class='small-12'][2]//p[1]//a/text()",
        'tags': '//a[contains(@href,"/category/")]/text()',
        'external_id': 'scene/([A-Za-z0-9-_]+)/?',
        'trailer': '//video/source/@src',
        'pagination': '/1/scenes/recent/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath(
            "//div[contains(@class, 'section-updates')]//div[contains(@class, 'scene-update')]")
        for scene in scenes:
            meta = {
                'image': scene.css('img::attr(src)').get(),
            }
            url = self.format_link(
                response, scene.css('a::attr(href)').get() + '/')
            yield scrapy.Request(url=url, meta=meta, callback=self.parse_scene)


    def get_date(self, response):
        return date.today().isoformat()


    def get_trailer(self, response):
        parsed_uri = urlparse(response.url)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        trailer = self.process_xpath(response, self.get_selector_map('trailer')).get()
        if trailer:
            return (domain + trailer).replace(" ","%20")
        
        return ''
        
    def get_site(self, response):
        if "badfamily" in response.url:
            trailerstring = response.xpath('//video/source/@src').get()
            if trailerstring:
                trailerstring = trailerstring.lower()
                trailerstring = re.search('upload\/(.*)\/', trailerstring)
                if trailerstring:
                    trailerstring = trailerstring.group(1)
                    if "bdp_joi" in trailerstring:
                        return "Daughter JOI"
                    if "bdp_" in trailerstring:
                        return "Bad Daddy POV"
                    if "bmp_joi" in trailerstring:
                        return "Mommy JOI"
                    if "bmp_" in trailerstring:
                        return "Bad Mommy POV"
                    if "bbpov_joi" in trailerstring:
                        return "Sister JOI"
                    if "bbpov_" in trailerstring:
                        return "Bad Sister POV"
                
        
        parsed_uri = tldextract.extract(response.url)
        if parsed_uri.domain == "elxcomplete":
            domain = parsed_uri.subdomain
        else:
            domain = parsed_uri.domain
        site = match_site(domain)
        if not site:
            site = tldextract.extract(response.url).domain
            
        return site        
