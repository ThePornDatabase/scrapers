import re
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class NubilesSpider(BaseSceneScraper):
    name = 'Nubiles'
    network = 'nubiles'

    custom_settings = {'CONCURRENT_REQUESTS': '1'}

    start_urls = [
        "https://anilos.com",
        "https://badteenspunished.com",
        "https://bountyhunterporn.com",
        "https://brattysis.com",
        "https://cumswappingsis.com",
        "https://daddyslilangel.com",
        "https://deeplush.com",
        "https://detentiongirls.com",
        "https://driverxxx.com",
        "https://familyswap.xxx",
        "https://momsteachsex.com",
        "https://myfamilypies.com",
        "https://nfbusty.com",
        "https://nubilefilms.com",
        "https://nubiles-casting.com",
        "https://nubiles-porn.com",
        "https://nubiles.net",
        "https://nubileset.com",
        "https://nubilesunscripted.com",
        "https://petitehdporn.com",
        "https://petiteballerinasfucked.com",
        "https://princesscum.com",
        "https://stepsiblingscaught.com",
        "https://teacherfucksteens.com",
        "https://thatsitcomshow.com",
    ]

    selector_map = {
        'title': '//*[contains(@class, "content-pane-title")]/h2/text()',
        'description': '.row .collapse::text',
        'date': '//span[@class="date"]/text()',
        'image': '//video/@poster|//img[@class="fake-video-player-cover"]/@src',
        'performers': '//a[@class="content-pane-performer model"]/text()',
        'tags': '//*[@class="categories"]//a/text()',
        'external_id': '(\\d+)',
        'trailer': '',
        'pagination': '/video/gallery/%s'
    }

    def get_scenes(self, response):
        scenes = response.xpath('//figcaption')
        for scene in scenes:
            link = scene.xpath('./div/span/a/@href').get()
            if re.search(r'video/watch', link) is not None:
                scenedate = response.xpath('.//span[@class="date"]/text()').get()
                meta = {
                    'title': scene.xpath('./div/span/a/text()').get().strip(),
                    'date': dateparser.parse(scenedate, date_formats=['%b %d, %Y']).isoformat(),
                }
                if "brattysis" in response.url:
                    meta['site'] = "Bratty Sis"
                    meta['parent'] = "Bratty Sis"
                if "cumswappingsis" in response.url:
                    meta['site'] = "Cum Swapping Sis"
                    meta['parent'] = "Cum Swapping Sis"
                elif "anilos" in response.url:
                    meta['site'] = "Anilos"
                    meta['parent'] = "Anilos"
                elif "deeplush" in response.url:
                    meta['site'] = "Deep Lush"
                    meta['parent'] = "Deep Lush"
                elif "nfbusty" in response.url:
                    meta['site'] = "NF Busty"
                    meta['parent'] = "NF Busty"
                elif "nubiles.net" in response.url:
                    meta['site'] = "Nubiles"
                    meta['parent'] = "Nubiles"
                if 'site' not in meta or not meta['site']:
                    meta['site'] = scene.xpath('.//a[@class="site-link"]/text()').get()
                    meta['parent'] = scene.xpath('.//a[@class="site-link"]/text()').get()
                yield scrapy.Request(
                    url=self.format_link(response, link),
                    callback=self.parse_scene, meta=meta)

    def get_next_page_url(self, base, page):
        page = (page - 1) * 10
        return self.format_url(
            base, self.get_selector_map('pagination') % page)

    def get_description(self, response):
        if 'description' not in self.get_selector_map():
            return ''
        descriptionxpath = self.process_xpath(response, self.get_selector_map('description'))
        description = ''
        if descriptionxpath:
            descriptionxpath = descriptionxpath.getall()
            for descrow in descriptionxpath:
                descrow = descrow.replace("\n", "").replace("\r", "").replace("\t", "").strip()
                if descrow:
                    description = description + descrow

        if not description or (description and not description.strip()):
            description = response.xpath('//div[@class="col-12 content-pane-column"]/div//text()')
            description = description.getall()
            if description:
                description = " ".join(description)
        if description:
            return description.replace('Description:', '').strip()
        return ""
