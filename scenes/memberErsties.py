import scrapy
import re
from scrapy.http import FormRequest
from slugify import slugify
from tpdb.BaseSceneScraper import BaseSceneScraper
# Member site: call with "-a user=xxxxxxx -a password=xxxxxxxxx"


class siteErstiesSpider(BaseSceneScraper):
    name = 'Ersties'
    network = 'Ersties'
    start_urls = [
        'https://en.ersties.com/login.php',
    ]
    selector_map = {
        'image': '',
        'performers': '',
        'external_id': '',
        'description': '',
        'pagination': 'https://en.ersties.com/videos?p=%s',
        'date': '//p[@class="last-update"]/span//text()',
        'date_formats': ['%-d.%-m.%Y'],
    }

    def start_requests(self):
        user = self.user
        password = self.password
        frmheaders = {}
        frmheaders['Content-Type'] = 'application/x-www-form-urlencoded'
        frmdata = {"username": user, "password": password}
        url = "http://en.ersties.com/login.php"
        yield FormRequest(url, headers=frmheaders, formdata=frmdata, callback=self.start_requests_actual, cookies=self.cookies)

    def start_requests_actual(self, response):
        for link in self.start_urls:
            yield scrapy.Request(url=self.get_next_page_url(link, self.page),
                                 meta={'page': self.page},
                                 # headers=headers,
                                 callback=self.parse,
                                 cookies=self.cookies)

    def _get_video_div(self, response):
        return response.xpath('//div[@id="' + response.meta["video_id"] + '"]')

    def get_description(self, response):
        description = ""
        for gallery in response.xpath("//div[contains(@class,'gallery-item')]"):
            videos = gallery.xpath(".//div[contains(@class,'video-item')]/@id").getall()
            if response.meta["video_id"] in videos:
                description = gallery.xpath('.//div[@class="gallery-description"]//text()').getall()
                description = " ".join(description)
                break
        description = description.replace("\r\n", " ")
        description = description.split("Last update:")[0]
        description = description.strip()
        return description

    def get_title(self, response):
        return self._get_video_div(response).xpath('.//div[@class="title"]/div/p/text()').get()

    def get_image(self, response):
        return self._get_video_div(response).xpath('.//a[contains(@class, "player")]//@style').get().split("url(")[1][:-2]

    def get_id(self, response):
        return slugify(response.meta["video_id"].split("-")[-1])

    def get_performers(self, response):
        performers_str = response.xpath('//div[contains(@class, "model-list")]/h2/descendant-or-self::*/text()').getall()
        performers_str = " ".join([p.replace("\n", "").strip() for p in performers_str])
        performers_str = performers_str.replace("More from", "")
        performers = performers_str.split(",")
        if performers == ['']:
            performers = [response.xpath('//span[@class="model-name"]//text()').get()]
        performers = [re.sub(r'\([^)]*\)', '', p) for p in performers]
        performers = [p.strip() for p in performers]

        # If some performers are in the title, remove performers not mentioned in title
        # This elminitated incorrect authors in projects with multiple performers with their own video
        def filter_s(s):
            s = s.lower()
            s = s.replace(".", "")
            return s

        def filter_performer(s):
            s = filter_s(s)
            return s.split()[0]

        in_title = []
        for performer in performers:
            if filter_performer(performer) in filter_s(self.get_title(response)):
                in_title.append(performer)
        if len(in_title) != 0:
            performers = in_title
        return performers

    def get_tags(self, response):
        return response.meta["tags"]

    def get_scenes(self, response):
        for scene in response.xpath("//div[contains(@class,'video-item')]"):
            profile_page = scene.xpath(".//div/a/@href").get()
            video_id = scene.xpath('./@id').get()

            # Get tags
            tags = scene.xpath('.//span[contains(@class, "tag")]//text()').getall()
            tags = [t.replace("\n", " ").replace("\r", " ").strip() for t in tags]
            try:
                tags.remove("...")
            except:
                pass
            try:
                tags.remove("All Tags")
            except:
                pass

            yield scrapy.Request(
                url="https://en.ersties.com" + profile_page + "#" + video_id,
                meta={"video_id": video_id, "tags": tags},
                callback=self.parse_scene,
                dont_filter=True,
                cookies=self.cookies)
