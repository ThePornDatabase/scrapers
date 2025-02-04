import re
import string
from tpdb.BaseSceneScraper import BaseSceneScraper


class NetworkApolloCashFaceSittingMomsSpider(BaseSceneScraper):
    name = 'ApolloCashFaceSittingMoms'
    network = 'Apollo Cash'

    start_urls = [
        'https://www.facesittingmoms.com',
    ]

    selector_map = {
        'external_id': r'',
        'pagination': '/index.php?updates=1&page=%s',
        'type': 'Scene',
    }

    def get_scenes(self, response):
        scenes = response.xpath('//h1/ancestor::table[1]')
        for scene in scenes:
            item = self.init_scene()

            title = scene.xpath('.//h1/text()')
            if title:
                item['title'] = self.cleanup_title(title.get())

            description = scene.xpath('.//text()[contains(., "Tags:")]')
            if description:
                description = description.get()
                description = re.search(r'(.*)Tags:', description).group(1)
                item['description'] = self.cleanup_description(description.strip())

            tags = scene.xpath('.//text()[contains(., "Tags:")]')
            if tags:
                tags = tags.get()
                tags = re.search(r'Tags:(.*)', tags).group(1)
                item['tags'] = list(map(lambda x: string.capwords(x.strip()), tags.split(",")))

            performers = scene.xpath('.//td[@align="center"]/font[1]/text()[contains(., ",")]')
            if performers:
                performers = performers.getall()
                performers = "".join(performers)
                performers = performers.replace("\r", "").replace("\n", "").replace("\t", "").strip()
                if performers:
                    if "," in performers:
                        performers = re.search(r'(.*),', performers).group(1)
                    item['performers'] = [performers]

            image = scene.xpath('.//img[contains(@alt, "FaceSittingMoms")]/@src')
            if image:
                item['image'] = self.format_link(response, image.get())
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
                item['id'] = re.search(r'.*/(.*?)_free', item['image']).group(1)
                if ".com" in item['id'].lower():
                    item['id'] = re.search(r'\.com_(.*)', item['id'].lower()).group(1)

            item['site'] = "Face Sitting Moms"
            item['parent'] = "Face Sitting Moms"
            item['network'] = "Apollo Cash"
            item['url'] = response.url

            yield item
