"""Runtime lookup of a NATS CMS block id.

These tours (Aziani, the islanddollars sites and others) are driven by
tour_api.php, where the catalogue lives behind a numeric cms_block_id. That id
belongs to a block on a page of the tour's layout, so it changes whenever the
tour is re-laid-out -- at which point the API starts answering

    {"error":"cms_block_id <id> not found","success":false,...}

and the spider quietly yields nothing, with no exception to show for it. That
failure has already taken out several scrapers, and it is invisible except as a
spider that stops producing.

resolve_block_id() walks the same chain the tour's own front end uses:

    <site>/natscms-app/config.json  -> natsUrl + cms_area_id
    <natsUrl>/tour_api.php/content/config   -> the tour's pages
    <natsUrl>/tour_api.php/content/page     -> a page's layout blocks
                                            -> the first set-backed block

It is deliberately forgiving: any failure at all returns the caller's existing
hardcoded id, so adding this can only ever help. It runs once per crawl.
"""

import re

import requests

_VIDEO_PAGE = re.compile(r'^/(videos?|[a-z0-9-]*videos)(/.*)?$')
_TIMEOUT = 20


def _get_json(url, headers):
    response = requests.get(url, headers=headers, timeout=_TIMEOUT)
    if not response.ok:
        return None
    return response.json()


def resolve_block_id(site_url, fallback, page_slug=None):
    """Return the tour's current cms_block_id, or `fallback` if anything fails.

    site_url  -- the tour's own origin, e.g. https://www.thaiswinger.com
    fallback  -- the id currently hardcoded in the spider
    page_slug -- pin a particular page (e.g. '/videos') instead of guessing
    """
    try:
        config = _get_json('%s/natscms-app/config.json' % site_url.rstrip('/'), {})
        if not config:
            return fallback
        nats_url = (config.get('natsUrl') or '').rstrip('/')
        area_id = config.get('cms_area_id') or ''
        if not nats_url or not area_id:
            return fallback

        headers = {'X-NATS-cms-area-id': area_id,
                   'X-nats-entity-decode': '1',
                   'Accept': 'application/json'}

        cms = _get_json('%s/tour_api.php/content/config?cms_area_id=%s' % (nats_url, area_id), headers)
        if not cms:
            return fallback

        slugs = [page_slug] if page_slug else [
            p.get('slug') for p in cms.get('pages') or []
            if isinstance(p, dict) and _VIDEO_PAGE.match(p.get('slug') or '')]

        for slug in slugs:
            if not slug:
                continue
            page = _get_json('%s/tour_api.php/content/page?slug=%s' % (nats_url, slug), headers)
            for block in (page or {}).get('blocks') or []:
                if (block.get('settings') or {}).get('ds_source') in ('sets', 'set') and block.get('cms_block_id'):
                    return str(block['cms_block_id'])
    except Exception as error:                                  # noqa: BLE001
        print('*** NATS block lookup failed for %s (%s); using %s'
              % (site_url, type(error).__name__, fallback))
    return fallback
