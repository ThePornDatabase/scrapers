import re
from PIL import Image
import base64
from io import BytesIO
from tpdb.BasePerformerScraper import BasePerformerScraper
from tpdb.items import PerformerItem


class SiteNaughtyAmericaPerformerSpider(BasePerformerScraper):
    selector_map = {
        'pagination': '/pornstars/top-rated?page=%s',
        'external_id': r'model/(.*)/'
    }

    name = 'NaughtyAmericaPerformer'
    network = 'Naughty America'

    start_urls = [
        'https://www.naughtyamerica.com',
    ]

    def get_performers(self, response):
        performers = response.xpath('//div[@class="performer-block"]')
        for performer in performers:
            item = PerformerItem()
            item['url'] = performer.xpath('.//a[contains(@class, "performer-name")]/@href').get()
            slug = re.search(r'.*/(.*?)$', item['url']).group(1)
            item['name'] = self.cleanup_title(performer.xpath('.//a[contains(@class, "performer-name")]/text()').get())
            image = performer.xpath('.//img/@data-srcset|.//source[contains(@srcset, ".jpg")]/@srcset')
            if image:
                image = image.get()
                if re.search(r' \dx', image):
                    image = image.split(",")
                    if len(image) > 1:
                        image = image[1]
                    image = re.search(r'//(.*?\.jpg)', image).group(1)
                image = "https://" + image.replace("//", "")
            if image:
                item['image'] = image
                # ~ item['image_blob'] = self.get_image_blob_from_link(item['image'], f"images/NaughtyAmericaSlugs/{slug}.jpg")
                item['image_blob'] = self.get_image_blob_from_link(item['image'])
            else:
                item['image'] = None
                item['image_blob'] = None
            item['bio'] = ''
            item['gender'] = 'Female'
            item['astrology'] = ''
            item['birthday'] = ''
            item['birthplace'] = ''
            item['cupsize'] = ''
            item['ethnicity'] = ''
            item['eyecolor'] = ''
            item['fakeboobs'] = ''
            item['haircolor'] = ''
            item['height'] = ''
            item['measurements'] = ''
            item['nationality'] = ''
            item['piercings'] = ''
            item['tattoos'] = ''
            item['weight'] = ''
            item['network'] = 'Naughty America'

            yield item

    # ~ def get_image_blob_from_link(self, image, filename):
        # ~ if image:
            # ~ data = self.get_image_from_link(image)
            # ~ if data:
                # ~ try:
                    # ~ img = BytesIO(data)
                    # ~ img = Image.open(img)
                    # ~ width, height = img.size
                    # ~ if height > 1080 or width > 1920:
                        # ~ img.thumbnail((1920, 1080))
                        # ~ buffer = BytesIO()
                        # ~ img.save(buffer, format="JPEG")
                        # ~ data = buffer.getvalue()
                # ~ except:
                    # ~ print(f"Could not decode image for evaluation: '{image}'")
                # ~ with open(filename, 'wb') as handler:
                    # ~ handler.write(data)
                # ~ return base64.b64encode(data).decode('utf-8')
        # ~ return None
