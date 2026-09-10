import re
import string

import scrapy

from tpdb.BaseSceneScraper import BaseSceneScraper
from tpdb.items import SceneItem


class MoviesHotMoviesSpider(BaseSceneScraper):
    name = 'HotMovies'
    network = 'Hot Movies'

    # HotMovies has migrated onto the AdultEmpire platform.  Two consequences:
    #
    #  * Every page now redirects to /AgeConfirmation until the ageConfirmed cookie
    #    is set, which is why the old crawl saw HTTP 200 and parsed nothing.
    #  * The old ld+json VideoObject is gone; the product page publishes the same
    #    data through og: meta tags and a labelled attribute list instead.
    #
    # The previous 154 start_urls were all /studio/<id>/<name>/ listings, but
    # format_url() replaces the path with 'pagination', so all of them collapsed to
    # the same /new_release.php?page=1 request and Scrapy deduped them down to one.
    # Only that one listing ever ran, so it is now the only start URL.
    start_urls = [
        'https://www.hotmovies.com',
    ]

    cookies = [{"name": "ageConfirmed", "value": "true"}]

    selector_map = {
        'title': '',
        'description': '',
        'date': '',
        'image': '',
        'performers': '',
        'tags': '',
        'duration': '',
        'trailer': '',
        'external_id': r'/(\d+)/',
        'pagination': '/new_release.php?page=%s'
    }

    def get_scenes(self, response):
        meta = self.copy_meta(response)
        scenes = response.xpath(
            '//div[contains(@class, "product-container")]//a[contains(@href, "-porn-video.html")]/@href').getall()
        for scene in dict.fromkeys(scenes):
            if re.search(self.get_selector_map('external_id'), scene):
                yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene,
                                     meta=meta, headers=self.headers, cookies=self.cookies)

    def parse_scene(self, response):
        movie = SceneItem()

        title = response.xpath('//h1/text()').get()
        if not title or not title.strip():
            return
        movie['title'] = self.cleanup_title(title)
        movie['description'] = self.cleanup_description(
            ' '.join(response.xpath('//div[contains(@class, "movie__synopsis")]//p//text()').getall()))
        movie['image'] = response.xpath('//meta[@property="og:image"]/@content').get() or ''
        movie['image_blob'] = self.get_image_blob_from_link(movie['image'])
        # The boxcover anchor points at the full sleeve scan (front and back)
        movie['back'] = response.xpath('//a[contains(@href, "imgs1cdn.adultempire.com/products/")]/@href').get() or ''
        movie['back_blob'] = self.get_image_blob_from_link(movie['back'])
        movie['trailer'] = self.get_hls_trailer(response)
        movie['type'] = 'Movie'
        movie['duration'] = self.get_movie_duration(response)
        movie['date'] = self.get_movie_date(response)
        movie['director'] = ''
        movie['tags'] = self.cleantags(
            response.xpath('//div[contains(@class, "movie__content-meta__cats")]/a/text()').getall())
        movie['performers'] = [string.capwords(x.strip()) for x in
                               response.xpath('//div[contains(@class, "movie__content-meta__stars")]/a/text()').getall()
                               if x.strip()]
        movie['id'] = re.search(self.get_selector_map('external_id'), response.url).group(1)

        site = self.get_studio(response)
        movie['site'] = site
        movie['parent'] = site
        movie['network'] = "Hot Movies"
        movie['url'] = response.url
        movie['scenes'] = []

        scenes = response.xpath('//h3[contains(@class, "movie__scenes__scene__scene-title")]/parent::div')
        for scenecount, scene in enumerate(scenes, start=1):
            link = scene.xpath('.//h3/a/@href').get() or ''
            sceneid = re.search(r'/adult-clips/(\d+)', link)
            if not sceneid:
                continue

            item = SceneItem()
            item['id'] = sceneid.group(1)
            item['title'] = movie['title'] + f" - Scene {scenecount}"
            item['url'] = self.format_link(response, link)
            item['description'] = movie['description']
            item['site'] = movie['site']
            item['parent'] = movie['parent']
            item['network'] = movie['network']
            item['date'] = movie['date']
            item['image'] = scene.xpath('.//div[@class="scene-screenshot-container"]/img/@src').get() or ''
            item['image_blob'] = self.get_image_blob_from_link(item['image'])
            item['trailer'] = movie['trailer']
            item['director'] = ''
            item['type'] = 'Scene'

            # The heading badge carries the running time, e.g. "24 min"
            duration = scene.xpath('.//h3/small[contains(@class, "badge")]/text()').get() or ''
            duration = re.search(r'(\d+)\s*min', duration)
            item['duration'] = str(int(duration.group(1)) * 60) if duration else None

            item['performers'] = [string.capwords(x.strip()).replace(" (Trans)", "") for x in
                                  scene.xpath('.//div[contains(@class, "scene__stars")]/a/text()').getall()
                                  if x.strip()]
            # The per-scene attributes block is present but always empty on the new
            # platform, so the movie's categories are the only tags available.
            item['tags'] = self.cleantags(
                scene.xpath('.//div[contains(@class, "scene__attributes")]/a/text()').getall()) or movie['tags']

            movie['scenes'].append({'site': movie['site'], 'external_id': item['id']})
            yield self.check_item(item, self.days)

        # The old scraper only emitted the movie when it broke into more than one
        # scene, so single-scene and scene-less releases were silently dropped.
        yield self.check_item(movie, self.days)

    def get_hls_trailer(self, response):
        """Read contentUrl out of the JSON-LD VideoObject.

        The block cannot go through json.loads(): the site embeds an unescaped HTML
        description containing raw newlines, so the JSON is invalid.
        """
        trailer = re.search(r'"contentUrl"\s*:\s*"(https?://[^"]+)"', response.text)
        return trailer.group(1) if trailer else ''

    def get_studio(self, response):
        """The studio doubles as site and parent, as it did on the previous site."""
        site = response.xpath('//strong[contains(text(), "Studio:")]/following-sibling::a/text()').get()
        if not site or not site.strip():
            return self.name
        site = site.strip()
        if ".com" in site.lower():
            site = re.search(r'^(.*?)\.com', site.lower()).group(1)
        return self.cleanup_title(site)

    def get_movie_date(self, response):
        """Prefer the release year when the site dates a re-issue later than it.

        This keeps the behaviour of the old copyrightYear/dateCreated comparison.
        """
        released = response.xpath('//meta[@property="og:video:release_date"]/@content').get()
        if not released:
            released = response.xpath('//strong[contains(text(), "Released:")]/following-sibling::text()').get()
        if not released or not released.strip():
            return None

        released = self.parse_date(released.strip())
        if not released:
            return None

        year = response.xpath('//strong[contains(text(), "Release Year:")]/following-sibling::text()').get()
        year = re.search(r'(\d{4})', year) if year else None
        if year and int(year.group(1)) < released.year:
            return year.group(1) + "-01-01"
        return released.isoformat()

    def get_movie_duration(self, response):
        """og:video:duration is already in seconds; "3 hrs. 15 mins." is the fallback."""
        duration = response.xpath('//meta[@property="og:video:duration"]/@content').get()
        if duration and duration.strip().isdigit() and int(duration) > 0:
            return duration.strip()

        runtime = response.xpath('//strong[contains(text(), "Run Time:")]/following-sibling::text()').get() or ''
        hours = re.search(r'(\d+)\s*hrs?', runtime)
        minutes = re.search(r'(\d+)\s*mins?', runtime)
        if hours or minutes:
            return str(int(hours.group(1) if hours else 0) * 3600 + int(minutes.group(1) if minutes else 0) * 60)
        return None

    def cleantags(self, taglist):
        tags = []
        for tag in taglist:
            tag = tag.lower().strip()
            if not tag:
                continue
            if "/" in tag:
                tag = re.search(r'(.*)/', tag).group(1)
            if "masturbation" in tag:
                tag = "masturbation"
            if "undressing" in tag:
                tag = "undressing"
            if "spooning" in tag:
                tag = "spooning"
            if "standing" in tag:
                tag = "standing sex"
            if "cowgirl" in tag:
                tag = "cowgirl"
            if "doggy" in tag:
                tag = "doggystyle"
            if "tribbing" in tag:
                tag = "tribbing"
            if "rimming" in tag:
                tag = "rimming"
            if "cunnilingus" in tag:
                tag = "cunnilingus"
            if "anal creampie" in tag:
                tag = "Anal Creampie"
            if "creampie" in tag:
                tag = "creampie"
            if "deep throating" in tag:
                tag = "deepthroat"
            if "anal" in tag:
                tag = "anal"
            tags.append(self.cleanup_title(tag).strip())
        return tags
