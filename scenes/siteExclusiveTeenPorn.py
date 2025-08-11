import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class SiteExclusiveTeenPornSpider(BaseSceneScraper):
    name = 'ExclusiveTeenPorn'
    network = 'Exclusive Teen Porn'
    parent = 'Exclusive Teen Porn'
    site = 'Exclusive Teen Porn'

    start_urls = [
        'https://exclusiveteenporn.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/videos_%s.html',
        'type': 'Scene',
    }

    def get_next_page_url(self, base, page):
        pagination = self.get_selector_map('pagination') % page
        if page == 1:
            return "https://exclusiveteenporn.com/videos.html"
        return self.format_url(base, pagination)

    def get_scenes(self, response):
        scenes = response.xpath('//table[@class="maindata"]//img[contains(@src, "full-movie")]//ancestor::table[@class="phcover"]')
        for scene in scenes:
            item = self.init_scene()

            item['title'] = string.capwords(scene.xpath('.//td[@class="setdescr"]/a[1]/text()').get())

            duration = scene.xpath('.//td[@class="setdescr"]//text()[contains(., "MIN VIDEO")]')
            if duration:
                item['duration'] = self.duration_to_seconds(re.sub(r'[^0-9:]+', '', duration.get()))

            tags = scene.xpath('.//a[contains(@href, "niche")]/text()')
            if tags:
                tags = tags.getall()
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags))

            image = scene.xpath('.//div[@class="phcoversub"]/a[1]/@href')
            if image:
                image = self.format_link(response, image.get())
                item['image'] = image
                item['image_blob'] = self.get_image_blob_from_link(image)
                item['id'] = re.search(r'.*_(\d+)', image).group(1)

            performers = scene.xpath('.//table[@class="setmodels"]//a')
            item['performers'] = []
            if performers:
                for performer in performers:
                    name = performer.xpath('./text()').get()
                    perf_id = performer.xpath('./@href').get()
                    perf_id = re.search(r'(\d+)', perf_id).group(1)
                    item['performers'].append(string.capwords(f"{name.strip()} {perf_id}"))

            item['site'] = "Exclusive Teen Porn"
            item['parent'] = "Exclusive Teen Porn"
            item['network'] = "Exclusive Teen Porn"
            item['type'] = "Scene"
            yield item
