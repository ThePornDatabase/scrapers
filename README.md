# Scrapers for ThePornDB

These are scrapers used by ThePornDB, written in Python using Scrapy.

## Writing a scraper

Most of the hard work is abstracted away from each scraper, making writing a new scraper quite simple.

We'll use ``AmateurBoxxx`` as an example.

```Python
import scrapy
from tpdb.BaseSceneScraper import BaseSceneScraper

class AmatuerBoxxxSpider(BaseSceneScraper):
    name = 'AmateurBoxxx'
    network = 'Amateur Boxxx'
```

First we import the BaseSceneScraper which has all of our helper methods, you can see this in our [scraper](https://github.com/ThePornDatabase/scrapy) repository.

Name is the name of this scraper, used when running it, this scraper is called AmateurBoxxx so we would run it like `scrapy crawl AmateurBoxxx`

Network is what network this site or group of sites belong to. We do this to group sites, scenes and performers together. AmataeurBoxxx is a one of site as far as we know, so we'll just leave it apart of it's own Network.

```Python
    start_urls = [
        'https://tour.amateurboxxx.com'
    ]
```

Start urls is a require property that will list our all urls that our scraper will start scraping. For a general purpose scraper that may all belongs to a single Network may have the same Xpath for every single site, so we can just list all URLs here and it will loop over them.

```Python
    selector_map = {
        'title': 'span.update_title::text',
        'description': 'span.latest_update_description::text',
        'performers': 'span.tour_update_models a::text',
        'date': 'span.availdate::text',
        'image': 'img.large_update_thumb::attr(src)',
        'tags': '',
        'trailer': '',
        'external_id': 'updates/(.+).html',
        'pagination': '/categories/updates_%s_d.html'
    }
```

The selector map property is the main part of the scraper you'll be working with. `title`, `description`, `performers`, `date`, `image`, `tags` and `trailer` are all the selectors for extracting the actual data from the page. They can be either CSS selectors or Xpath selectors. For this specific scraper i have opted to use CSS selectors. If the select starts with `/` it will translate to Xpath, otherwise CSS.

All selectors are required, except for `tags` and `trailer`. You can read more about writing Scrapy selectors [here](https://docs.scrapy.org/en/latest/topics/selectors.html)

The `external_id` selector is RegEx for extracting the ID of the scene from the URL, this is also a required field and must include a single extraction for the ID. If the ID is not in the url, you can override what's returned by implementing the `get_id` function. 

```Python
    def get_id(self, response):
        return slugify(self.get_title(response))
```

Finally `pagination` is a string that we format with the page number, so the scraper knows how to loop over pages getting a list of Scenes.

Additionally if you're scraping a network site that has multiple subsites, you can return the site for that specific scene by implementing the `get_site` function.

If you look at the base scraper, every data point has a corresponding function eg. `get_title` and just grabs the `title` from `selector_map` returning that data. If you have data on a page that can not be extracted with just a Xpath selector, you can override the `get_title` function, which is provided with the raw scrapy object which includes the raw HTML so you can extract the data however you want. You can see how it is done in the `Scrapy` repository.

For example this is how we get the images from PornPros:

```Python
    def get_image(self, response):
        if response.xpath('//meta[@name="twitter:image"]').get() is not None:
            return response.xpath('//meta[@name="twitter:image"]/@content').get()

        if response.xpath('//video').get() is not None:
            if response.xpath('//video/@poster').get() is not None:
                return response.xpath('//video/@poster').get()

        if response.xpath('//img[@id="no-player-image"]') is not None:
            return response.xpath('//img[@id="no-player-image"]/@src').get()
```

If the data required is missing from this page, but it's on the pagination page, you can see how to use that data below.

```Python
    def get_scenes(self, response):
        scenes = response.css('.updateItem h4 a::attr(href)').getall()
        for scene in scenes:
            yield scrapy.Request(url=self.format_link(response, scene), callback=self.parse_scene)
```

Finally we have the `get_scenes` function, this is a required function which yields the links to scenes from the paginated pages.

Scrapy will loop over each pagination page eg. `https://amateurboxxx.com/categories/updates_1_d.html` and pass the raw html instance to `get_scenes` where you must loop over the list of scenes passing them back to the main scrapy instance using yield.

`format_link` is a handy helper which will format the URL found on the page to make sure it's a FQDN.

The request must be yielded as a `scrapy.Request`, and must pass the callback to `self.parse_scene`

If there is data on these paginated pages that you want to pass into the scraper, you can pass the meta object through. Here's an example from PornPros;

```Python
    def get_scenes(self, response):
        scenes = response.xpath("//div[contains(@class, 'video-releases-list')]//div[@data-video-id]")
        for scene in scenes:
            link = scene.css('a::attr(href)').get()
            meta = {}

            if scene.css('div::attr(data-date)').get() is not None:
                meta['date'] = dateparser.parse(
                    scene.css('div::attr(data-date)').get()).isoformat()

            if scene.css('div::attr(data-video-id)').get() is not None:
                meta['id'] = scene.css('div::attr(data-video-id)').get()

            yield scrapy.Request(url=self.format_link(response, link), callback=self.parse_scene, meta=meta)
```

If the site you're scraping doesn't have a standard pagination listing page, or is an API, all functions can be overwritten to work for your specific case. Check out our [MetArt](scenes/networkMetArt.py) or [ProjectOneService](./scenes/networkProjectOneService.py) scrapers
