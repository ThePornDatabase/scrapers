import re
from tpdb.BaseSceneScraper import BaseSceneScraper
import tldextract
import scrapy


def match_site(argument):
    match = {
        'abbiemaley': 'Abbie Maley',
        'analamateur': 'Anal Amateur',
        'analbbc': 'Anal BBC',
        'analized': 'Analized',
        'analviolation': 'Anal Violation',
        'badbrotherpov': 'Bad Brother POV',
        'baddaddypov': 'Bad Daddy POV',
        'badfamilypov': 'Bad Family POV',
        'badmommypov': 'Bad Mommy POV',
        'badsisterpov': 'Bad Sister POV',
        'daughterjoi': 'Daughter JOI',
        'downtofuckdating': 'DTF Dating',
        'dtfsluts': 'DTF Sluts',
        'girlfaction': 'Girl Faction',
        'hergape': 'Her Gape',
        'homemadeanalwhores': 'Homemade Anal Whores',
        'jamesdeen': 'James Deen',
        'lesbiananalsluts': 'Lesbian Anal Sluts',
        'mommyjoi': 'Mommy JOI',
        'mugfucked': 'Mug Fucked',
        'onlyprince': 'Only Prince',
        'pervertgallery': 'Pervert Gallery',
        'povperverts': 'POV Perverts',
        'pornforce': 'Porn Force',
        'publicsexdate': 'Public Sex Date',
        'realfuckingdating': 'Real Fucking Dating',
        'shefucksonthefirstdate': 'She Fucks on the First Date',
        'sisterjoi': 'Sister JOI',
        'slutinspection': 'Slut Inspection',
        'slutsbts': 'Sluts BTS',
        'slutspov': 'Sluts POV',
        'sluttybbws': 'Slutty BBWs',
        'teenageanalsluts': 'Teenage Anal Sluts',
        'teenagecorruption': 'Teenage Corruption',
        'teenagetryouts': 'Teenage Tryouts',
        'twistedvisual': 'Twisted Visual',
        'wifespov': 'Wifes POV',
        'yourmomdoesanal': 'Your Mom Does Anal',
        'yourmomdoesporn': 'Your Mom Does Porn',
    }
    return match.get(argument, '')


class FullPornNetworkSpider(BaseSceneScraper):
    name = 'FullPorn'
    network = 'Full Porn Network'

    #  This setup is after 2021-11-01 network redesign
    start_urls = [
        'https://abbiemaley.com',
        'https://analamateur.com',
        'https://analbbc.com',
        'https://analized.com',
        'https://analviolation.com',
        'https://badbrotherpov.com',
        'https://baddaddypov.com',
        # ~ #'https://badfamilypov.com',  # Sites pulled from the sub-sites
        'https://badmommypov.com',
        'https://badsisterpov.com',
        'https://daughterjoi.com',
        'https://downtofuckdating.com/',
        'https://dtfsluts.com',
        'https://girlfaction.com',
        'https://hergape.com',
        'https://homemadeanalwhores.com',
        'https://jamesdeen.com',
        'https://lesbiananalsluts.com',
        'https://mommyjoi.com',
        'https://mugfucked.com',
        'https://onlyprince.com',
        'https://pervertgallery.com',
        'https://pornforce.com',
        'https://povperverts.net',
        'https://publicsexdate.com',
        'https://realfuckingdating.com',
        'https://shefucksonthefirstdate.com',
        'https://sisterjoi.com',
        'https://slutinspection.com',
        'https://slutsbts.com',
        'https://slutspov.com',
        'https://sluttybbws.com',
        'https://teenageanalsluts.com',
        'https://teenagecorruption.com',
        'https://teenagetryouts.com',
        'https://twistedvisual.com',
        'https://wifespov.com',
        'https://yourmomdoesanal.com',
        'https://yourmomdoesporn.com',
    ]

    selector_map = {
        'title': '//h1[contains(@class, "title_bar")]/text()',
        'description': '//p[@class="description-text"]/text()',
        'performers': '//div[@class="video-info"]//span[@class="update_models"]/a/text()',
        'image': '//video/@poster|//div[@id="preview"]/a/div/img/@src0_1x',
        'date': '//label[contains(text(), "Date Added")]/following-sibling::p[1]/text()',
        'date_formats': ['%Y-%m-%d'],
        'tags': '//ul/li/a[contains(@href, "/categories/")]/text()',
        'external_id': r'trailers/([A-Za-z0-9-_]+)\.htm?',
        'trailer': '',
        'pagination': '/categories/movies_%s_d.html'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//div[@class="relative group"]/a/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)

    def get_site(self, response):
        if "badfamily" in response.url:
            trailerstring = response.xpath('//video/@src').get()
            if trailerstring:
                trailerstring = trailerstring.lower()
                trailerstring = re.search(r'upload/(.*)/', trailerstring)
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

    def get_parent(self, response):

        parsed_uri = tldextract.extract(response.url)
        if parsed_uri.domain == "elxcomplete":
            domain = parsed_uri.subdomain
        else:
            domain = parsed_uri.domain
        site = match_site(domain)
        if not site:
            site = tldextract.extract(response.url).domain

        return site
