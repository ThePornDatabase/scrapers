import re
import scrapy
import tldextract

from tpdb.BaseSceneScraper import BaseSceneScraper


class LetsDoeItSpider(BaseSceneScraper):
    name = 'LetsDoeIt'
    network = "LetsDoeIt"

    start_urls = [
        'https://www.letsdoeit.com',
        'https://amateureuro.com',
        'https://mamacitaz.com/',
        # ~ # 'https://dirtycosplay.com/',  Paywalled
        'https://transbella.com/',
        'https://vipsexvault.com',
    ]

    selector_map = {
        'title': '//div[contains(@class,"module-video-details")]//h1/text()',
        'description': '//meta[@name="description"]/@content',
        'date': '//meta[@itemprop="uploadDate"]/@content',
        're_date': r'(\d{4}-\d{2}-\d{2})',
        'image': '//meta[@itemprop="thumbnailUrl"]/@content|//img[@class="-vcc-img"]/@src',
        'performers': '//div[@class="-mvd-grid-actors"]/span/a[contains(@href, "/models/")]/text()',
        'tags': "//a[contains(@href,'/tags/') or contains(@href,'/categories/')]/text()",
        'duration': '//meta[@itemprop="duration"]/@content',
        'external_id': r'/watch/(.*)/',
        'trailer': '//meta[@itemprop="contentURL"]/@content',
        'pagination': '/videos.en.html?order=-recent&page=%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        responsetext = response.xpath('//*').getall()
        responsetext = "".join(responsetext)
        scenes = re.findall(r'a\ target=\"_self\" class=\"-g-vc-fake\"\ href=\"(.*?.html)\"', responsetext)
        for scene in scenes:
            if re.search(self.get_selector_map('external_id'), scene):
                meta['id'] = re.search(r'/watch/(.*)/', scene).group(1)
                meta['url'] = self.format_link(response, scene)
                yield scrapy.Request(meta['url'], callback=self.parse_scene, meta=meta)

    def get_site(self, response):
        site = response.xpath('//div[@class="-mvd-grid-actors"]/span[1]/a[1]/text()').get().strip()
        return site

    def get_parent(self, response):
        if "amateureuro" in response.url:
            return "Amateur Euro"
        if "letsdoeit" in response.url:
            return "LetsDoeIt"
        if "vipsexvault" in response.url:
            return "VIP Sex Vault"
        if "mamacitaz" in response.url:
            return "MamacitaZ"
        if "transbella" in response.url:
            return "Trans Bella"
        if "dirtycosplay" in response.url:
            return "Dirty Cosplay"

        return tldextract.extract(response.url).domain

    def get_description(self, response):
        xpathtext = response.xpath('//meta[@itemprop="description"]/@content')
        if not xpathtext:
            xpathtext = response.xpath(self.get_selector_map('description'))

        description = xpathtext.getall()
        description = " ".join(description)
        return description

    def get_duration(self, response):
        duration = response.xpath(self.get_selector_map('duration'))
        if duration:
            duration = duration.get()
            if "M" in duration:
                minutes = (int(re.search(r'(\d+)M', duration).group(1)) * 60)
                seconds = int(re.search(r'(\d+)M', duration).group(1))
                if "H" in duration:
                    hours = (int(re.search(r'(\d+)M', duration).group(1)) * 3600)
                    return str(hours + minutes + seconds)
                return str(minutes + seconds)
        return None

    def get_date(self, response):
        scenedate = super().get_date(response)
        if scenedate:
            return scenedate

        # ~ scenedate = response.xpath('//div[contains(@class,"video-top-details")]//div[contains(@class,"mvd-grid-stats")]//text()')
        scenedate = response.xpath('//div[contains(text(), "Views")]/text()')
        if scenedate:
            scenedate = scenedate.get()
            scenedate = re.search(r'(\w+ \d{2}, \d{4})', scenedate)
            if scenedate:
                scenedate = scenedate.group(1)
                return self.parse_date(scenedate, date_formats=['%b %d, %Y']).strftime('%Y-%m-%d')

        return None
