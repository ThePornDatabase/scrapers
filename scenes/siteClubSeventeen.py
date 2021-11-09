import re
import warnings
import dateparser
import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper

# Ignore dateparser warnings regarding pytz
warnings.filterwarnings(
    "ignore",
    message="The localize method is no longer necessary, as this time zone supports the fold attribute",
)


class ClubseventeenSpider(BaseSceneScraper):
    name = 'ClubSeventeen'
    network = 'ClubSeventeen'
    parent = 'ClubSeventeen'

    start_urls = [
        'https://www.clubseventeen.com',
        # 'https://www.clubsweethearts.com'
    ]

    selector_map = {
        'title': "//div[@class='top']/h3[@class='dvd-title mb-0 mt-0']/span/text()",
        'description': ".video-info > .bottom > p::text",
        'date': "//div[@class='video-info']//p[contains(@class,'letter-space-1') and contains(@class, 'mt-10')]/b/following-sibling::text()",
        'performers': "//div[@class='video-info']/div[@class='middle']/p[@class='mt-10']/a/text()",
        'tags': "//div[@class='top']/div[@class='item-tag mt-5']/a/span/text()",
        'image': ".static-video-wrapper .video-item::attr(data-image)",
        'external_id': 'slug=(.+)',
        'pagination': '/videos.php?page=%s'
    }

    def get_scenes(self, response):
        """ Returns a list of scenes
        @url https://www.clubseventeen.com/videos.php?page=1
        @returns requests 50 150
        """
        scenes = response.css(
            '.list_item .thumb .video-link::attr(href)').getall()
        for link in scenes:
            if re.search(self.get_selector_map(
                    'external_id'), link) is not None:
                yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene)

    def get_date(self, response):
        date = self.process_xpath(response, self.get_selector_map('date')).get()
        if re.search(r'\d{2}-\d{2}-\d{4}', date):
            datereg = re.search(r'(\d{2})-(\d{2})-(\d{4})', date)
            date = datereg.group(3) + "-" + datereg.group(2) + "-" + datereg.group(1)
        else:
            date = "1970-01-01"
        return dateparser.parse(date.strip()).isoformat()
