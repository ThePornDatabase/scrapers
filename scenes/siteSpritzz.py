import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

class SpritzzSpider(BaseSceneScraper):
    name = 'Spritzz'
    network = 'Spritzz'

    start_urls = [
        'https://spritzz.com/?videos'
    ]

    selector_map = {
        'title': 'h2::text',
        'description': '',  # Will be handled in get_description
        'performers': '',   # Will be handled in get_performers
        'date': '',         # Will be handled in get_date
        'duration': '',     # Will be handled in get_duration
        'image': '',        # Can be added if image selector is found
        'tags': '',
        'external_id': r'/video/.*?/(\d+)',
        'pagination': '/?videos&page=%s'
    }

    def get_scenes(self, response):
        # Match both 'video/' and '/video/' in href, deduplicate
        scenes = list(set(response.css('a[href*="video/"]::attr(href)').getall()))
        for scene in scenes:
            yield scrapy.Request(
                url=self.format_link(response, scene),
                callback=self.parse_scene
            )

    def get_title(self, response):
        # Only get the h2 inside .videonewinfo that is not part of a modal
        title = response.css('.videonewinfo h2::text').get()
        return title.strip() if title else ''

    def get_description(self, response):
        # Description is the first <p> under .videonewinfo that is not the cast
        desc = response.css('.videonewinfo > p::text').get()
        return desc.strip() if desc else ''

    def get_performers(self, response):
        # Cast is in <p> with 'Cast:'
        cast = response.css('.videonewinfo > p:contains("Cast:")::text').get()
        if cast:
            return [name.strip() for name in cast.replace('Cast:', '').split(',')]
        return []

    def get_date(self, response):
        # Date is in <h5> as 'Released: Month Day, Year'
        import re
        from dateutil import parser
        date_text = response.css('.videonewinfo h5::text').get()
        if date_text:
            match = re.search(r'Released:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4})', date_text)
            if match:
                return parser.parse(match.group(1)).date().isoformat()
        return None

    def get_duration(self, response):
        # Duration is in <h5> as 'Duration: mm:ss'
        import re
        duration_text = response.css('.videonewinfo h5::text').get()
        if duration_text:
            match = re.search(r'Duration:\s*([\d:]+)', duration_text)
            if match:
                return self.duration_to_seconds(match.group(1))
        return None

    def get_image(self, response):
        # Image is in the JW Player config as image: '...'
        import re
        match = re.search(r'image:\s*["\']([^"\']+)["\']', response.text)
        if match:
            image = match.group(1)
            if image.startswith('http'):
                return image
            else:
                return response.urljoin(image)
        return None

    def get_tags(self, response):
        # Tags are in the data-src attribute of #related_scenes as a comma-separated list of quoted strings
        import re
        tags_raw = response.css('#related_scenes::attr(data-src)').get()
        if tags_raw:
            tags = re.findall(r'"([^"]+)"', tags_raw)
            tags = [tag.replace('__', ' ').replace('_', ' ') for tag in tags]
            tags.append("Gay")
            return tags
        return ["Gay"]

    def get_performers_data(self, response):
        performers = self.get_performers(response)
        performers_data = []
        if len(performers):
            for performer in performers:
                perf = {}
                perf['name'] = performer
                perf['extra'] = {}
                perf['extra']['gender'] = "Male"
                perf['network'] = "Spritzz"
                perf['site'] = "Spritzz"
                performers_data.append(perf)
        return performers_data

    def parse(self, response):
        # Scrape scenes on the current page
        yield from self.get_scenes(response)

        # Find pagination links and follow them
        pagination_links = response.css('a.pagenumbers::attr(href)').getall()
        for link in pagination_links:
            url = self.format_link(response, link)
            if url != response.url:  # Avoid re-requesting the current page
                yield scrapy.Request(url, callback=self.parse)
