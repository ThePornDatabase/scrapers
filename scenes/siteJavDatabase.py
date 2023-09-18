import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteJavDatabaseSpider(BaseSceneScraper):
    name = 'JavDatabase'
    network = 'JavDatabase'

    start_urls = [
        'https://www.javdatabase.com',
    ]

    selector_map = {
        'title': '//header[@class="entry-header"]/h1/text()',
        'description': '',
        'date': '//b[contains(text(), "Release Date:")]/../following-sibling::td[1]/text()',
        'image': '//div[@class="entry-content"]/div/table//img[contains(@src, "covers")]/@src',
        'performers': '//h2[contains(text(), "Actress")]/following-sibling::div[1]//p/a/text()',
        'tags': '//td[@class="tablevalue"]/span/a[contains(@href, "genres")]/text()',
        'director': '//b[contains(text(), "Director:")]/../following-sibling::td[1]/span/a/text()',
        'trailer': '',
        'external_id': r'.*/(.*?)/',
        'pagination': '/movies/page/%s/',
        'type': 'JAV',
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[@class="movie-cover-thumb"]/a[contains(@href, "javdatabase")]/@href').getall()
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_duration(self, response):
        duration = response.xpath('//b[contains(text(), "Runtime:")]/../following-sibling::td[1]/text()')
        if duration:
            duration = duration.get()
            duration = re.search(r'(\d+) min', duration)
            if duration:
                return str(int(duration.group(1)) * 60)
        return None

    def get_site(self, response):
        site = response.xpath('//b[contains(text(), "Studio:")]/../following-sibling::td[1]/span/a/text()').get()
        return site

    def get_parent(self, response):
        return super().get_site(response)

    def get_tags(self, response):
        tags = super().get_tags(response)
        tags2 = []
        matches = ['hours', 'hi-def', 'exclusive', 'featured']
        for tag in tags:
            tag = tag.lower()
            if not any(x in tag for x in matches):
                tags2.append(string.capwords(tag))
        return tags2

    def get_id(self, response):
        javid = super().get_id(response)
        return javid.upper()

    def get_title(self, response):
        title = super().get_title(response)
        if len(title) > 240:
            title = title[:240] + "..."
            print(f"*** Title truncated to: {title}")
        return self.uncensor_title(title)

    def uncensor_title(self, title):
        title = title.replace("A*****t", "Assault")
        title = title.replace("A****p", "Asleep")
        title = title.replace("A***e", "Abuse")
        title = title.replace("B***d", "Blood")
        title = title.replace("B**d", "Bled")
        title = title.replace("C***d", "Child")
        title = title.replace("C*ck", "Cock")
        title = title.replace("D******e", "Disgrace")
        title = title.replace("D***king", "Drinking")
        title = title.replace("D***k", "Drunk")
        title = title.replace("D**g", "Drug")
        title = title.replace("F*****g", "Forcing")
        title = title.replace("F***e", "Force")
        title = title.replace("G*******g", "Gangbang")
        title = title.replace("G******g", "Gang Bang")
        title = title.replace("H*********n", "Humiliation")
        title = title.replace("H*******e", "Hypnotize")
        title = title.replace("H*******m", "Hypnotism")
        title = title.replace("H**t", "Hurt")
        title = title.replace("I****t", "Incest")
        title = title.replace("K****p", "Kidnap")
        title = title.replace("K****r", "Killer")
        title = title.replace("K**l", "Kill")
        title = title.replace("K*d", "Kid")
        title = title.replace("L****a", "Lolita")
        title = title.replace("M************n", "Mother And Son")
        title = title.replace("M****t", "Molest")
        title = title.replace("P********t", "Passed Out")
        title = title.replace("P****h", "Punish")
        title = title.replace("R****g", "Raping")
        title = title.replace("R**e", "Rape")
        title = title.replace("RStepB****************r", "Stepbrother and Sister")
        title = title.replace("S*********l", "School Girl")
        title = title.replace("S**********s", "School Girls")
        title = title.replace("S********l", "Schoolgirl")
        title = title.replace("S*********s", "Schoolgirls")
        title = title.replace("S******g", "Sleeping")
        title = title.replace("S*****t", "Student")
        title = title.replace("S***e", "Slave")
        title = title.replace("S**t", "Scat")
        title = title.replace("Sch**l", "School")
        title = title.replace("StepM************n", "Stepmother and Son")
        title = title.replace("T******e", "Tentacle")
        title = title.replace("T*****e", "Torture")
        title = title.replace("U*********s", "Unconscious")
        title = title.replace("V*****e", "Violate")
        title = title.replace("V*****t", "Violent")
        title = title.replace("Y********l", "Young Girl")
        title = title.replace("A*****t", "Assault")
        title = title.replace("a*****t", "assault")
        title = title.replace("a****p", "asleep")
        title = title.replace("a***e", "abuse")
        title = title.replace("b***d", "blood")
        title = title.replace("b**d", "bled")
        title = title.replace("c***d", "child")
        title = title.replace("c*ck", "cock")
        title = title.replace("d******e", "disgrace")
        title = title.replace("d***king", "drinking")
        title = title.replace("d***k", "drunk")
        title = title.replace("d**g", "drug")
        title = title.replace("f*****g", "forcing")
        title = title.replace("f***e", "force")
        title = title.replace("g*******g", "gangbang")
        title = title.replace("g******g", "gang bang")
        title = title.replace("h*********n", "humiliation")
        title = title.replace("h*******e", "hypnotize")
        title = title.replace("h*******m", "hypnotism")
        title = title.replace("h**t", "hurt")
        title = title.replace("i****t", "incest")
        title = title.replace("k****p", "kidnap")
        title = title.replace("k****r", "killer")
        title = title.replace("k**l", "kill")
        title = title.replace("k*d", "kid")
        title = title.replace("l****a", "lolita")
        title = title.replace("m************n", "mother and son")
        title = title.replace("m****t", "molest")
        title = title.replace("p********t", "passed out")
        title = title.replace("p****h", "punish")
        title = title.replace("r****g", "raping")
        title = title.replace("r**e", "rape")
        title = title.replace("rstepb****************r", "stepbrother and sister")
        title = title.replace("s*********l", "school girl")
        title = title.replace("s********l", "schoolgirl")
        title = title.replace("s**********s", "school girls")
        title = title.replace("s*********s", "schoolgirls")
        title = title.replace("s******g", "sleeping")
        title = title.replace("s*****t", "student")
        title = title.replace("s***e", "slave")
        title = title.replace("s**t", "scat")
        title = title.replace("sch**l", "school")
        title = title.replace("stepm************n", "stepmother and son")
        title = title.replace("t******e", "tentacle")
        title = title.replace("t*****e", "torture")
        title = title.replace("u*********s", "unconscious")
        title = title.replace("v*****e", "violate")
        title = title.replace("v*****t", "violent")
        title = title.replace("y********l", "young girl")

        return title
