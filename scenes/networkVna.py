import re
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper


class VnaNetworkSpider(BaseSceneScraper):
    name = 'VnaNetwork'
    network = 'vna'

    start_urls = [
        'https://www.allanalallthetime.com',    #Rip
        'https://angelinacastrolive.com',       #Rip
        'https://www.blownbyrone.com',              #Rip
        'https://carmenvalentina.com',          #Rip
        'https://charleechaselive.com',         #Rip
        'https://foxxedup.com',                 #Rip
        'https://fuckedfeet.com',
        'https://gabbyquinteros.com',           #Rip
        'https://girlgirlmania.com',            #Rip
        'https://itscleolive.com',              #Rip
        'https://jelenajensen.com',             #Rip
        'https://juliaannlive.com',             #Rip
        'https://kaylapaigelive.com',           #Rip
        'https://kendrajames.com',              #Rip
        'https://kimberleelive.com',            #Rip
        'https://kink305.com',                  #Rip
        'https://maggiegreenlive.com',          #Rip
        'https://maxinex.com',
        'https://nataliastarr.com',             #Rip
        'https://ninakayy.com',                 #Rip
        'https://pennypaxlive.com',             #Rip
        'https://povmania.com',                 #Rip
        'https://pumaswedexxx.com',             #Rip
        'https://romemajor.com',                #Rip
        'https://rubberdoll.net',               #Rip
        'https://www.samanthagrace.net',            #Rip
        'https://sarajay.com',                  #Rip
        'https://sexmywife.com',                #Rip
        'https://shandafay.com',                #Rip
        'https://siripornstar.com',             #Rip
        'https://sophiedeelive.com',            #Rip
        'https://sunnylanelive.com',            #Rip
        'https://tashareign.com',               #Rip
        'https://vnavickie.com',              #Rip
        'https://vickyathome.com',              #Rip
        'https://womenbyjuliaann.com',
        'https://wydesyde.com',

        # Invalid VNA Sites, here for reference
        # Can't be scraped for various reasons...  Locked, no pagination, no video page, etc
        # 'https://alexlegend.com',               #New Site, standalone scraper
        # ~ https://bobbiedenlive.com
        # ~ https://deauxmalive.com
        # ~ https://nataliastarr.com            #Rip
        # ~ https://nikkibenz.com               #Rip
        # ~ https://rachelstormsxxx.com

    ]

    selector_map = {
        'title': '//h1[@class="customhcolor"]/text()',
        'description': '//*[@class="customhcolor2"]/text()',
        'date': '//*[@class="date"]/text()',
        'image': '//center//img/@src',
        'performers': '//h3[@class="customhcolor"]/text()',
        'tags': '//h4[@class="customhcolor"]/text()',
        'external_id': r'videos/(\d+)/(.+)',
        'trailer': '',

        'pagination': '/videos/page/%s'
    }

    def get_scenes(self, response):
        meta = response.meta
        # ~ if "romemajor" in response.url:
        scenes = response.xpath('//div[contains(@class, "videoarea clear")]|//div[contains(@class, "updatedVideo")]|//div[contains(@class,"videoPics clear")]|//div[contains(@class, "vid-block")]|//div[contains(@class, "videos clear")]|//div[@class="video-thumb"]')
        for scene in scenes:
            scenelink = scene.xpath('.//h3/a/@href|.//div[@class="videoPic"][1]/a/@href')
            if scenelink:
                scenelink = scenelink.get()
            if not scenelink:
                scenelink = scene.xpath('.//div[contains(@class,"wrap-video-thumb")]/a/@href')
                if scenelink:
                    scenelink = scenelink.get()
            if not scenelink:
                scenelink = scene.xpath('./div[contains(@class,"block-title")]/p/a/@href')
                if scenelink:
                    scenelink = scenelink.get()
            if not scenelink:
                scenelink = scene.xpath('./ul[1]/a[1]/@href')
                if scenelink:
                    scenelink = scenelink.get()
            if scenelink:
                image = scene.xpath('.//img[contains(@src, "thumb_2")]/@src|.//img[contains(@src, "thumb")]/@src')
                if image:
                    meta['image_blob'] = self.get_image_blob_from_link(self.format_link(response, image.get()))
                    meta['image'] = self.format_link(response, image.get()).replace("sd3.php?show=file&path=/", "")

                if "join" in scenelink or not scenelink:
                    scenelink = scene.xpath('./div[1]/div[1]/a[1]/@href').get()

                if scenelink:
                    scene = scenelink
                    scene = self.format_link(response, scene)
                    if re.search(self.selector_map['external_id'], scene):
                        yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene, meta=meta)

    def get_tags(self, response):
        taglink = self.process_xpath(
            response, self.get_selector_map('tags')).get()
        tags = []
        for tag in taglink.strip().split(','):
            if tag.strip():
                tags.append(tag.strip().title())
        return tags

    def get_performers(self, response):
        performerlink = self.process_xpath(
            response, self.get_selector_map('performers')).get()

        performers = []
        for performer in performerlink.replace('&nbsp', '').split(','):
            if performer.strip():
                performers.append(performer.strip())

        if 'shandafay' in response.url:
            performers.append('Shanda Fay')
        if 'vnavickie' in response.url and not performers:
            performers.append('Vickie Jay')
        if 'sexmywife' in response.url:
            performers.append('Mandy Tyler')

        return performers

    def get_next_page_url(self, base, page):
        if "vickyathome" in base:
            return self.format_url(base, "/milf-videos/page/%s" % page)
        return self.format_url(base, self.get_selector_map('pagination') % page)

    def get_image(self, response):
        meta = response.meta
        image = super().get_image(response)
        image = image.replace("sd3.php?show=file&path=/", "")
        if not re.search(r'\.com/(.*)', image) or (".jpg" not in image.lower()):
            return None
        return image
