import re
import string
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper


def match_site(argument):
    match = {
        'asianamericantgirls': "Asian-American TGirls",
        'black-tgirls': "Black TGirls",
        'blacktgirlshardcore': "Black TGirls Hardcore",
        'bobstgirls': "Bobs TGirls",
        'brazilian-transsexuals': "Brazilian Transexuals",
        'braziltgirls': "Brazil Tgirls",
        'canada-tgirl': "Canada Tgirl",
        'euro-tgirls': "Euro Tgirls",
        'femoutsexxxx': "FemOutSex.xxx",
        'femoutxxx': "FemOut.xxx",
        'franks-tgirlworld': "Franks TGirl World",
        'futa': "Futa.xxx",
        'grooby-archives': "Grooby Archives",
        'groobygirls': "Grooby Girls",
        'ladyboyxxx': "Ladyboy.xxx",
        'realtgirls': "Real TGirls",
        'tgirljapanhardcore': "TGirl Japan Hardcore",
        'tgirljapancom': "TGirl Japan",
        'tgirlsporn': "TGirls Porn",
        'tgirlsex': "TGirl Sex",
        'tgirltops': "TGirl Tops",
        'tgirlsxxx': "TGirls.xxx",
        'tgirlx': "TGirlX",
        'tgirlsfuck': "TGirls Fuck",
        'transexpov': "Transex POV",
        'transgasm': "Transgasm",
    }
    return match.get(argument, argument)


class NetworkGroobySpider(BaseSceneScraper):
    name = 'Grooby'
    network = 'Grooby Network'

    start_urls = [
        # ~ # 'https://www.asianamericantgirls.com', In grooby.club
        # ~ 'https://www.black-tgirls.com',
        # ~ 'https://www.blacktgirlshardcore.com',
        # ~ 'https://www.bobstgirls.com',
        # ~ 'https://www.brazilian-transsexuals.com',
        # ~ 'https://www.braziltgirls.xxx',
        # ~ # 'https://www.canada-tgirl.com', In grooby.club
        # ~ # 'https://www.euro-tgirls.com', In grooby.club
        # ~ 'https://www.grooby.club/',
        # ~ 'https://www.femout.xxx',
        # ~ 'https://www.femoutsex.xxx',
        # ~ 'https://www.franks-tgirlworld.com',
        # ~ 'https://www.futa.xxx',
        # ~ 'https://www.grooby-archives.com',
        # ~ 'https://www.groobygirls.com',
        # ~ 'https://www.ladyboy.xxx',
        # ~ 'https://www.realtgirls.com',
        # ~ 'https://www.tgirljapan.com',
        # ~ 'https://www.tgirljapanhardcore.com',
        # ~ 'https://www.tgirltops.com',
        # ~ 'https://www.tgirls.porn',
        'https://www.tgirls.xxx',
        # ~ 'https://www.tgirlsex.xxx',
        # ~ 'https://www.tgirlsfuck.com',
        # ~ 'https://www.tgirlx.com',
        # ~ 'https://www.transexpov.com',
        # ~ 'https://www.transgasm.com',
    ]

    selector_map = {
        'title': '//div[@class="trailerpage_info"]/p[contains(@class, "trailertitle")]/text()|//div[@class="trailer_toptitle_left"]//text()',
        'description': '//div[@class="trailerpage_info"]/p[not(contains(@class, "trailertitle"))]/text()|//div[@class="trailer_videoinfo"]/p[not(./b)]/text()',
        'image': '//div[@class="trailerdata"]/div[contains(@class, "trailerposter")]/img/@src0_2x|//div[@class="trailerdata"]/div[contains(@class, "trailerposter")]/img/@src0_1x|//div[@class="videohere"]/img[contains(@src,".jpg")]/@src',
        'performers': '//div[@class="trailerpage_info"]//a[contains(@href, "/models/")]/text()|//div[@class="trailer_videoinfo"]//a[contains(@href, "/models/")]/text()',
        'tags': '//div[@class="set_tags"]/ul/li/a/text()',
        'trailer': '//div[@class="trailerdata"]/div[contains(@class, "trailermp4")]/text()',
        'external_id': r'.*/(.*?)\.htm',
        'pagination': '/tour/categories/movies/%s/latest/'
    }

    def get_scenes(self, response):
        meta = response.meta
        scenes = response.xpath('//div[contains(@class,"sexyvideo")]')
        for scene in scenes:
            scenedate = scene.xpath('.//i[contains(@class, "fa-calendar")]/following-sibling::text()')
            if scenedate:
                scenedate = scenedate.get().lower().replace("added", "").strip()
                meta['date'] = self.parse_date(scenedate, date_formats=['%d %b %Y']).isoformat()
            else:
                scenedate = scene.xpath('.//p[@class="dateadded"]')
                if scenedate:
                    scenedate = scenedate.get()
                    scenedate = re.search(r'(\d{1,2}[sthndr]+? \[a-zA-Z]+ \d{4})', scenedate)
                    if scenedate:
                        meta['date'] = self.parse_date(scenedate.group(1), date_formats=['%d %b %Y']).isoformat()

            title = scene.xpath('.//h4/a/text()')
            if title:
                meta['title'] = self.cleanup_title(title.get())

            site = scene.xpath('./div/div[@class="sitename"]//text()')
            if site:
                site = site.getall()
                site = self.cleanup_title("".join(site).strip())
                if site.lower() == "uk-tgirls.com":
                    site = "UK TGirls"
                meta['site'] = site
                meta['parent'] = site

            scene = scene.xpath('.//h4/a/@href|.//div[@class="videohere"]/a/@href').get()
            scene = self.format_link(response, scene)
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        meta = response.meta
        tags = super().get_tags(response)

        if "Trans" not in tags:
            tags.append("Trans")

        if "transexpov" in response.url:
            tags.append("POV")
        if "asian" in response.url:
            tags.append("Asian")
        if "japan" in response.url:
            tags.append("Asian")
        if "ladyboy" in response.url:
            tags.append("Asian")
        if "canada" in response.url:
            tags.append("Canada")
        if "brazil" in response.url:
            tags.append("Latin American")
        if "transgasm" in response.url:
            tags.append("Orgasm")
        if "site" in meta:
            if "euro" in meta['site'].lower():
                tags.append("European")
            if "canada" in meta['site'].lower():
                tags.append("Canada")
            if "bbw" in meta['site'].lower():
                tags.append("BBW")
            if "uk" in meta['site'].lower():
                tags.append("British")
            if "russian" in meta['site'].lower():
                tags.append("Russian")
            if "40" in meta['site'].lower():
                tags.append("Older / Younger")

        tags2 = []
        for tag in tags:
            if "photo" not in tag.lower():
                tags2.append(tag)

        return tags2

    def get_site(self, response):
        site = super().get_site(response)
        if ".tgirls.porn" in response.url:
            site = "tgirlsporn"
        if ".femoutsex.xxx" in response.url:
            site = "femoutsexxxx"
        if ".femout.xxx" in response.url:
            site = "femoutxxx"
        if ".ladyboy.xxx" in response.url:
            site = "ladyboyxxx"
        if ".realtgirls.com" in response.url:
            site = "realtgirls"
        if ".tgirljapan.com" in response.url:
            site = "tgirljapancom"
        if ".tgirls.xxx" in response.url:
            site = "tgirlsxxx"
        if ".tgirlx.com" in response.url:
            site = "tgirlx"
        return match_site(site)

    def get_parent(self, response):
        site = super().get_site(response)
        if ".tgirls.porn" in response.url:
            site = "tgirlsporn"
        if ".femoutsex.xxx" in response.url:
            site = "femoutsexxxx"
        if ".femout.xxx" in response.url:
            site = "femoutxxx"
        if ".ladyboy.xxx" in response.url:
            site = "ladyboyxxx"
        if ".realtgirls.com" in response.url:
            site = "realtgirls"
        if ".tgirljapan.com" in response.url:
            site = "tgirljapancom"
        if ".tgirls.xxx" in response.url:
            site = "tgirlsxxx"
        if ".tgirlx.com" in response.url:
            site = "tgirlx"
        return match_site(site)

    def get_date(self, response):
        scenedate = response.xpath('//div[@class="trailer_video"]//comment()[contains(., "Added")]')
        if not scenedate:
            scenedate = response.xpath('//b[contains(text(), "Added")]/following-sibling::text()')

        if scenedate:
            scenedate = scenedate.get()
            scenedate = scenedate.replace("  ", " ")
            scenedate = re.search(r'([a-zA-Z]+ \d{1,2}, \d{4})', scenedate).group(1)
            return self.parse_date(scenedate, date_formats=['%B %d, %Y']).isoformat()

        return self.parse_date('today').isoformat()

    def get_title(self, response):
        if 'title' in self.get_selector_map():
            title = self.get_element(response, 'title', 're_title')
            if title:
                if isinstance(title, list):
                    title = " ".join(title)
                return string.capwords(self.cleanup_text(title))
        return ''

    def get_image(self, response):
        image = super().get_image(response)
        if "jpg" not in image:
            image = response.xpath('//script[contains(text(), "jwplayer") and not(contains(text(), ".key"))]/text()')
            if image:
                image = image.get()
                image = re.search(r'image:\s+?\"(.*)?\"', image)
                if image:
                    return self.format_link(response, image.group(1))
        if not image:
            image = response.xpath('//meta[@property="og:image"]/@content')
            if image:
                return self.format_link(response, image.get())
        return image

    def get_trailer(self, response):
        trailer = super().get_trailer(response)
        if "mp4" not in trailer:
            trailer = response.xpath('//script[contains(text(), "jwplayer") and not(contains(text(), ".key"))]/text()')
            if trailer:
                trailer = trailer.get()
                trailer = re.search(r'file:\s+?\"(.*)?\"', trailer)
                if trailer:
                    trailer = self.format_link(response, trailer.group(1))
                    return trailer
        if trailer:
            return trailer
        return None
