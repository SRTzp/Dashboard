"""TS1 — tests never touch the network.
Import this once (after `from playwright.sync_api import ...`). Every browser context / page gets a LOW-priority catch-all
route for http(s): anything a suite did not stub itself (page.route registered later wins) is answered locally with an
empty 200, so the app's external iframe / fonts / APIs can no longer produce 403 / blocked-frame console errors."""
import re
from playwright.sync_api import Browser, BrowserContext

_BODY = {"document": ("text/html", "<!doctype html><title>stub</title>"), "script": ("application/javascript", ""),
         "stylesheet": ("text/css", ""), "fetch": ("application/json", "{}"), "xhr": ("application/json", "{}")}


def _handler(route):
    ct, body = _BODY.get(route.request.resource_type, ("text/plain", ""))
    route.fulfill(status=200, content_type=ct, body=body)


def _arm(ctx):
    if not getattr(ctx, "_ts1_net_stub", False):
        ctx.route(re.compile(r"^https?://"), _handler)
        ctx._ts1_net_stub = True
    return ctx


if not getattr(Browser, "_ts1_patched", False):
    _nc, _np = Browser.new_context, Browser.new_page
    _cp = BrowserContext.new_page
    Browser.new_context = lambda self, *a, **k: _arm(_nc(self, *a, **k))
    def _new_page(self, *a, **k):
        p = _np(self, *a, **k); _arm(p.context); return p
    Browser.new_page = _new_page
    Browser._ts1_patched = True
