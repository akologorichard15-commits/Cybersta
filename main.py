"""
CYBERSTAR LIVE PLATFORM EDITION
Compact, responsive, scroll-friendly public-web research application.

Designed for Android/Pydroid 3 with Kivy.
Public-source research only. No bypassing private access controls.
"""

import re
import html
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import webbrowser
import urllib.parse
import urllib.request
from collections import OrderedDict

try:
    import requests
except Exception:
    requests = None

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from kivy.graphics import Color, RoundedRectangle
from kivy.utils import get_color_from_hex


# ----------------------------- THEME -----------------------------

BG = get_color_from_hex("#EAF5FB")
PANEL = get_color_from_hex("#D7EAF7")
CARD = get_color_from_hex("#FFFFFF")
CARD2 = get_color_from_hex("#B9D7EC")
CYAN = get_color_from_hex("#087F9B")
BLUE = get_color_from_hex("#2B8BE8")
WHITE = get_color_from_hex("#17324D")
MUTED = get_color_from_hex("#58758C")
GREEN = get_color_from_hex("#159B70")
YELLOW = get_color_from_hex("#C47B00")

SEARCH_ENGINES = {
    "DuckDuckGo": "https://html.duckduckgo.com/html/?q={}",
    "Bing": "https://www.bing.com/search?q={}",
    "Google": "https://www.google.com/search?q={}",
    "Brave": "https://search.brave.com/search?q={}",
}

PLATFORM_DOMAINS = [
    # Major/current social platforms
    ("Facebook", "facebook.com"),
    ("Instagram", "instagram.com"),
    ("WhatsApp", "whatsapp.com"),
    ("TikTok", "tiktok.com"),
    ("YouTube", "youtube.com"),
    ("X/Twitter", "x.com"),
    ("LinkedIn", "linkedin.com"),
    ("Snapchat", "snapchat.com"),
    ("Threads", "threads.net"),
    ("Telegram", "t.me"),
    ("Reddit", "reddit.com"),
    ("Pinterest", "pinterest.com"),
    ("Discord", "discord.com"),
    ("Twitch", "twitch.tv"),
    ("Quora", "quora.com"),
    ("Medium", "medium.com"),
    ("Tumblr", "tumblr.com"),
    ("Bluesky", "bsky.app"),
    ("Mastodon", "mastodon.social"),
    ("Behance", "behance.net"),
    ("Dribbble", "dribbble.com"),
    ("SoundCloud", "soundcloud.com"),
    ("Vimeo", "vimeo.com"),
    ("Flickr", "flickr.com"),
    ("Spotify", "spotify.com"),
    ("Substack", "substack.com"),
    ("Patreon", "patreon.com"),
    ("GitLab", "gitlab.com"),
    ("Stack Overflow", "stackoverflow.com"),
    ("Kwai", "kwai.com"),
    ("Likee", "likee.video"),
    ("WeChat", "wechat.com"),
    ("Weibo", "weibo.com"),
    ("VK", "vk.com"),
    ("LINE", "line.me"),
    ("Lemon8", "lemon8-app.com"),
    ("Kick", "kick.com"),
    ("Rumble", "rumble.com"),
    ("Dailymotion", "dailymotion.com"),
 ]

# Native public search destinations used when a platform index returns no
# directly parsed result. These are real platform URLs, not fake result cards.
PLATFORM_SEARCH_URLS = {
    "facebook.com": "https://www.facebook.com/search/top/?q={}",
    "instagram.com": "https://www.instagram.com/explore/search/keyword/?q={}",
    "whatsapp.com": "https://www.google.com/search?q=site%3Awhatsapp.com+{}",
    "tiktok.com": "https://www.tiktok.com/search?q={}",
    "youtube.com": "https://www.youtube.com/results?search_query={}",
    "x.com": "https://x.com/search?q={}",
    "twitter.com": "https://x.com/search?q={}",
    "linkedin.com": "https://www.linkedin.com/search/results/all/?keywords={}",
    "snapchat.com": "https://www.google.com/search?q=site%3Asnapchat.com+{}",
    "threads.net": "https://www.threads.net/search?q={}",
    "t.me": "https://www.google.com/search?q=site%3At.me+{}",
    "reddit.com": "https://www.reddit.com/search/?q={}",
    "pinterest.com": "https://www.pinterest.com/search/pins/?q={}",
    "discord.com": "https://www.google.com/search?q=site%3Adiscord.com+{}",
    "twitch.tv": "https://www.twitch.tv/search?term={}",
    "quora.com": "https://www.quora.com/search?q={}",
    "medium.com": "https://medium.com/search?q={}",
    "tumblr.com": "https://www.tumblr.com/search/{}",
    "bsky.app": "https://bsky.app/search?q={}",
    "mastodon.social": "https://mastodon.social/search?q={}",
    "behance.net": "https://www.behance.net/search/projects?search={}",
    "dribbble.com": "https://dribbble.com/search/{}",
    "soundcloud.com": "https://soundcloud.com/search?q={}",
    "vimeo.com": "https://vimeo.com/search?q={}",
    "flickr.com": "https://www.flickr.com/search/?text={}",
    "spotify.com": "https://open.spotify.com/search/{}",
    "github.com": "https://github.com/search?q={}&type=users",
    "gitlab.com": "https://gitlab.com/search?search={}",
    "stackoverflow.com": "https://stackoverflow.com/search?q={}",
    "kwai.com": "https://www.google.com/search?q=site%3Akwai.com+{}",
    "likee.video": "https://www.google.com/search?q=site%3Alikee.video+{}",
    "wechat.com": "https://www.google.com/search?q=site%3Awechat.com+{}",
    "weibo.com": "https://s.weibo.com/weibo?q={}",
    "vk.com": "https://vk.com/search?c%5Bq%5D={}",
    "line.me": "https://www.google.com/search?q=site%3Aline.me+{}",
    "lemon8-app.com": "https://www.google.com/search?q=site%3Alemon8-app.com+{}",
    "kick.com": "https://kick.com/search?query={}",
    "rumble.com": "https://rumble.com/search/video?q={}",
    "dailymotion.com": "https://www.dailymotion.com/search/{}",
}


# ----------------------------- HELPERS -----------------------------

def clean(value):
    return (value or "").strip()


def quote(value):
    return urllib.parse.quote_plus(value)


def make_url(template, query):
    return template.format(quote(query))


def get_page(url, timeout=5):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 12) AppleWebKit/537.36 "
            "Chrome/120 Mobile Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.8",
    }

    try:
        if requests:
            response = requests.get(url, headers=headers, timeout=timeout)
            return response.text

        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def strip_tags(text):
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def parse_duckduckgo(page):
    output = []
    if not page:
        return output

    pattern = re.compile(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
        re.I | re.S
    )

    for url, title in pattern.findall(page):
        url = html.unescape(url)
        title = strip_tags(title)

        if url.startswith("//"):
            url = "https:" + url

        if "uddg=" in url:
            try:
                url = urllib.parse.parse_qs(
                    urllib.parse.urlparse(url).query
                ).get("uddg", [url])[0]
            except Exception:
                pass

        if title and url.startswith("http"):
            output.append({
                "title": title,
                "url": url,
                "snippet": "",
                "engine": "DuckDuckGo",
            })

    return output[:15]


def parse_bing(page):
    output = []
    if not page:
        return output

    pattern = re.compile(
        r'<li class="b_algo".*?<h2><a href="([^"]+)".*?>(.*?)</a></h2>'
        r'(.*?)(?=<li class="b_algo"|</ol>)',
        re.I | re.S
    )

    for url, title, block in pattern.findall(page):
        title = strip_tags(title)
        snippet = strip_tags(block)[:300]

        if title and url.startswith("http"):
            output.append({
                "title": title,
                "url": html.unescape(url),
                "snippet": snippet,
                "engine": "Bing",
            })

    return output[:15]


def parse_generic(page, engine):
    output = []
    if not page:
        return output

    pattern = re.compile(
        r'<a[^>]+href=["\'](https?://[^"\']+)["\'][^>]*>(.*?)</a>',
        re.I | re.S
    )

    seen = set()
    for url, title in pattern.findall(page):
        title = strip_tags(title)
        if (
            url not in seen
            and title
            and len(title) > 3
            and "search" not in url.lower()
        ):
            seen.add(url)
            output.append({
                "title": title[:140],
                "url": html.unescape(url),
                "snippet": "",
                "engine": engine,
            })

    return output[:12]


def native_platform_url(query):
    """Return a real platform destination for a site: query."""
    if not query.startswith("site:"):
        return None
    domain = query.split("site:", 1)[1].split()[0].lower()
    name_match = re.search(r'"(.*?)"', query)
    name = name_match.group(1) if name_match else query
    template = PLATFORM_SEARCH_URLS.get(domain)
    if template:
        return template.format(quote(name))
    return "https://www.google.com/search?q=" + quote(query)


def search_engine(engine, query):
    url = make_url(SEARCH_ENGINES[engine], query)
    page = get_page(url)

    if engine == "DuckDuckGo":
        results = parse_duckduckgo(page)
    elif engine == "Bing":
        results = parse_bing(page)
    else:
        results = parse_generic(page, engine)

    if not results:
        fallback_url = native_platform_url(query) or url
        if query.startswith("site:"):
            domain = query.split("site:", 1)[1].split()[0]
            name_match = re.search(r'"(.*?)"', query)
            person = name_match.group(1) if name_match else query
            title = f"{domain} public search for {person}"
            snippet = f"Open the actual {domain} search destination or inspect indexed public references."
        else:
            title = f"Open {engine} results for: {query}"
            snippet = "The search page is available for manual review."
        results = [{
            "title": title,
            "url": fallback_url,
            "snippet": snippet,
            "engine": engine,
        }]

    return results


# ----------------------------- UI COMPONENTS -----------------------------

def platform_from_query(query):
    if not query or not query.startswith("site:"):
        return None
    return query.split("site:", 1)[1].split()[0]



class RoundedPanel(BoxLayout):
    def __init__(self, fill=PANEL, radius=15, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(*fill)
            self.shape = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(radius)]
            )
        self.bind(pos=self._sync, size=self._sync)

    def _sync(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size


class ResultCard(BoxLayout):
    def __init__(self, result, owner, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(4),
            padding=[dp(11), dp(9)],
            size_hint_y=None,
            height=dp(178),
            **kwargs
        )

        with self.canvas.before:
            Color(*CARD)
            self.shape = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[dp(12)]
            )
        self.bind(pos=self._sync, size=self._sync)

        title = result.get("title", "Untitled public result")
        url = result.get("url", "")
        snippet = result.get("snippet", "") or "Public source available for review."
        engine = result.get("engine", "Web")
        platform = platform_from_query(result.get("query", ""))
        display_source = platform or "Public Web"
        matches = result.get("matches", [])

        top = BoxLayout(size_hint_y=None, height=dp(28))

        title_label = Label(
            text=title[:115],
            color=WHITE,
            bold=True,
            font_size="12sp",
            halign="left",
            valign="middle",
        )
        title_label.bind(size=lambda obj, *_: setattr(
            obj, "text_size", (obj.width, None)
        ))
        top.add_widget(title_label)

        badge = Label(
            text=f"{len(matches)} CLUES" if matches else "REVIEW",
            color=GREEN if len(matches) >= 2 else YELLOW,
            bold=True,
            font_size="9sp",
            size_hint_x=None,
            width=dp(72),
        )
        top.add_widget(badge)
        self.add_widget(top)

        source = Label(
            text=f"{display_source}  •  {url[:130]}",
            color=CYAN,
            font_size="9sp",
            halign="left",
            valign="middle",
            size_hint_y=None,
            height=dp(22),
        )
        source.bind(size=lambda obj, *_: setattr(
            obj, "text_size", (obj.width, None)
        ))
        self.add_widget(source)

        snippet_label = Label(
            text=snippet[:220],
            color=MUTED,
            font_size="9sp",
            halign="left",
            valign="top",
            size_hint_y=None,
            height=dp(34),
        )
        snippet_label.bind(size=lambda obj, *_: setattr(
            obj, "text_size", (obj.width, None)
        ))
        self.add_widget(snippet_label)

        clue_text = (
            "Matched: " + " • ".join(matches)
            if matches else "Matched: not confirmed in available text"
        )
        clue_label = Label(
            text=clue_text,
            color=GREEN if len(matches) >= 2 else YELLOW,
            font_size="9sp",
            halign="left",
            size_hint_y=None,
            height=dp(20),
        )
        clue_label.bind(size=lambda obj, *_: setattr(
            obj, "text_size", (obj.width, None)
        ))
        self.add_widget(clue_label)

        buttons = BoxLayout(size_hint_y=None, height=dp(31), spacing=dp(5))

        open_btn = Button(
            text="OPEN",
            background_normal="",
            background_color=BLUE,
            color=WHITE,
            font_size="9sp",
        )
        open_btn.bind(on_release=lambda *_: webbrowser.open(url))

        copy_btn = Button(
            text="COPY",
            background_normal="",
            background_color=CARD2,
            color=WHITE,
            font_size="9sp",
        )
        copy_btn.bind(on_release=lambda *_: self.copy_url(url, owner))

        search_btn = Button(
            text="SEARCH",
            background_normal="",
            background_color=CARD2,
            color=WHITE,
            font_size="9sp",
        )
        search_btn.bind(on_release=lambda *_: owner.open_query(
            result.get("query", title)
        ))

        buttons.add_widget(open_btn)
        buttons.add_widget(copy_btn)
        buttons.add_widget(search_btn)
        self.add_widget(buttons)

    def _sync(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size

    @staticmethod
    def copy_url(url, owner):
        Clipboard.copy(url)
        owner.set_status("Source link copied.")


# ----------------------------- MAIN APP -----------------------------

class CyberstarRoot(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            spacing=dp(7),
            padding=[dp(10), dp(8)],
            **kwargs
        )

        self.results = []
        self.searching = False
        self.stop_event = threading.Event()
        self.current_filter = "ALL"

        # One main scroll view: the complete page scrolls naturally.
        self.page_scroll = ScrollView(
            do_scroll_x=False,
            bar_width=dp(4),
            scroll_type=["bars", "content"],
        )

        self.page = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=[0, 0, 0, dp(12)],
            size_hint_y=None,
        )
        self.page.bind(minimum_height=self.page.setter("height"))
        self.page_scroll.add_widget(self.page)
        self.add_widget(self.page_scroll)

        self.build_header()
        self.build_search_panel()
        self.build_action_bar()
        self.build_status()
        self.build_filter_bar()
        self.build_results_area()

    def text_label(self, text, size=11, color=MUTED, bold=False, **kwargs):
        return Label(
            text=text,
            color=color,
            font_size=f"{size}sp",
            bold=bold,
            **kwargs
        )

    def build_header(self):
        header = RoundedPanel(
            orientation="vertical",
            size_hint_y=None,
            height=dp(68),
            padding=[dp(16), dp(8)],
        )

        row = BoxLayout(size_hint_y=None, height=dp(39))
        brand = self.text_label("CYBERSTAR", 23, CYAN, True, halign="center")
        brand.bind(size=lambda obj, *_: setattr(obj, "text_size", (obj.width, None)))
        row.add_widget(brand)
        header.add_widget(row)

        header.add_widget(self.text_label(
            "PUBLIC WEB INTELLIGENCE  •  MOBILE RESEARCH",
            9, MUTED, True,
            size_hint_y=None, height=dp(20)
        ))

        self.page.add_widget(header)

    def make_input(self, hint):
        return TextInput(
            hint_text=hint,
            multiline=False,
            size_hint_y=None,
            height=dp(34),
            background_normal="",
            background_active="",
            background_color=CARD2,
            foreground_color=WHITE,
            hint_text_color=MUTED,
            cursor_color=CYAN,
            padding=[dp(10), dp(8)],
            font_size="11sp",
        )

    def build_search_panel(self):
        panel = RoundedPanel(
            orientation="vertical",
            size_hint_y=None,
            height=dp(150),
            padding=[dp(10), dp(9)],
            spacing=dp(5),
        )

        title_row = BoxLayout(size_hint_y=None, height=dp(23))
        title_row.add_widget(self.text_label(
            "RESEARCH CLUES", 13, CYAN, True
        ))
        title_row.add_widget(self.text_label(
            "Use any combination", 9, MUTED, False,
            halign="right"
        ))
        panel.add_widget(title_row)

        # Compact 2-column field grid.
        grid = GridLayout(
            cols=2,
            spacing=dp(6),
            size_hint_y=None,
            height=dp(105),
        )

        self.name = self.make_input("Name / username")
        self.country = self.make_input("Country")
        self.region = self.make_input("Region / city")
        self.institution = self.make_input("School / university")

        for field in [
            self.name, self.country, self.region, self.institution
        ]:
            grid.add_widget(field)

        panel.add_widget(grid)
        self.page.add_widget(panel)

    def build_action_bar(self):
        # No engine settings exposed to the user. Cyberstar performs its own
        # broad public-web sweep behind the scenes.
        bar = BoxLayout(
            size_hint_y=None,
            height=dp(40),
            spacing=dp(6),
        )

        self.search_button = Button(
            text="⚡ START BROAD SEARCH",
            background_normal="",
            background_color=BLUE,
            color=WHITE,
            bold=True,
            font_size="10sp",
        )
        self.search_button.bind(on_release=self.start_search)
        bar.add_widget(self.search_button)

        self.stop_button = Button(
            text="■ STOP",
            background_normal="",
            background_color=get_color_from_hex("#D9534F"),
            color=WHITE,
            bold=True,
            font_size="10sp",
            size_hint_x=0.25,
            disabled=True,
        )
        self.stop_button.bind(on_release=self.stop_search)
        bar.add_widget(self.stop_button)

        clear = Button(
            text="CLEAR",
            background_normal="",
            background_color=CARD2,
            color=WHITE,
            font_size="10sp",
            size_hint_x=0.22,
        )
        clear.bind(on_release=self.clear_all)
        self.clear_button = clear
        bar.add_widget(clear)

        self.page.add_widget(bar)

    def build_status(self):
        self.status = self.text_label(
            "Ready. Enter a name and optional clues.",
            10, MUTED, False,
            size_hint_y=None, height=dp(22),
            halign="left",
        )
        self.status.bind(size=lambda obj, *_: setattr(
            obj, "text_size", (obj.width, None)
        ))
        self.page.add_widget(self.status)

        self.progress = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(4),
        )
        self.page.add_widget(self.progress)

    def build_filter_bar(self):
        bar = BoxLayout(
            size_hint_y=None,
            height=dp(32),
            spacing=dp(5),
        )

        self.filter_buttons = {}
        for text, value in [
            ("ALL", "ALL"),
            ("STRONG", "STRONG"),
            ("SOCIAL", "PLATFORMS"),
        ]:
            button = Button(
                text=text,
                background_normal="",
                background_color=BLUE if value == "ALL" else CARD2,
                color=WHITE,
                font_size="9sp",
                bold=True,
            )
            button.bind(on_release=lambda _, v=value: self.set_filter(v))
            self.filter_buttons[value] = button
            bar.add_widget(button)

        top = Button(
            text="TOP",
            background_normal="",
            background_color=CARD2,
            color=WHITE,
            font_size="9sp",
            size_hint_x=0.20,
        )
        top.bind(on_release=lambda *_: self.go_top())
        bar.add_widget(top)

        self.page.add_widget(bar)

    def build_results_area(self):
        self.results_title = self.text_label(
            "RESEARCH LEADS  •  0 RESULTS",
            12, CYAN, True,
            size_hint_y=None, height=dp(25),
        )
        self.page.add_widget(self.results_title)

        self.platform_hint = self.text_label(
            "AUTOMATIC BROAD SWEEP: Facebook • Instagram • WhatsApp • TikTok • YouTube • X/Twitter • LinkedIn • Telegram • Pinterest • Reddit • Discord • and more",
            8, MUTED, False,
            size_hint_y=None, height=dp(18),
            halign="left",
        )
        self.platform_hint.bind(size=lambda obj, *_: setattr(
            obj, "text_size", (obj.width, None)
        ))
        self.page.add_widget(self.platform_hint)

        self.result_box = GridLayout(
            cols=1,
            spacing=dp(7),
            size_hint_y=None,
        )
        self.result_box.bind(
            minimum_height=self.result_box.setter("height")
        )
        self.page.add_widget(self.result_box)
        self.show_empty()

    def show_empty(self):
        self.result_box.clear_widgets()
        self.result_box.add_widget(self.text_label(
            "Your public research leads will appear here.\n"
            "Cyberstar will collect source links and show matching clues.",
            11, MUTED, False,
            halign="center",
            valign="middle",
            size_hint_y=None,
            height=dp(62),
        ))

    def get_clues(self):
        return {
            "Name": clean(self.name.text),
            "Country": clean(self.country.text),
            "Region": clean(self.region.text),
            "Institution": clean(self.institution.text),
        }

    def build_queries(self):
        clues = self.get_clues()
        name = clues["Name"]

        if not name:
            return []

        queries = [f'"{name}"']

        extras = [
            value for key, value in clues.items()
            if key != "Name" and value
        ]

        for value in extras:
            queries.append(f'"{name}" "{value}"')

        if len(extras) >= 2:
            queries.append(
                '"' + name + '" "' + '" "'.join(extras[:2]) + '"'
            )

        if len(extras) >= 3:
            queries.append(
                '"' + name + '" "' + '" "'.join(extras[:3]) + '"'
            )

        if clues["Institution"]:
            queries.append(
                f'"{name}" "{clues["Institution"]}"'
            )

        # Platform-specific public searches. These are normal public-web
        # queries; the app does not bypass logins, private profiles, or blocks.
        for _, domain in PLATFORM_DOMAINS:
            queries.append(f'site:{domain} "{name}"')

        unique = []
        for item in queries:
            if item not in unique:
                unique.append(item)

        return unique

    def calculate_matches(self, result):
        clues = self.get_clues()
        combined = (
            result.get("title", "") + " " +
            result.get("snippet", "") + " " +
            result.get("query", "") + " " +
            result.get("url", "")
        ).lower()

        matches = []
        for key, value in clues.items():
            if value and value.lower() in combined:
                matches.append(key)
        return matches

    def start_search(self, *_):
        if self.searching:
            return

        queries = self.build_queries()
        if not queries:
            self.popup("Missing name", "Enter at least a name or username.")
            return

        self.results = []
        self.refresh_results()
        self.searching = True
        self.stop_event.clear()
        self.progress.value = 0
        self.search_button.disabled = True
        self.stop_button.disabled = False
        self.clear_button.disabled = True
        self.set_status(
            f"Fast broad search started • {len(queries)} targets queued..."
        )

        threading.Thread(
            target=self.worker,
            args=(queries,),
            daemon=True
        ).start()

    def stop_search(self, *_):
        if not self.searching:
            return
        self.stop_event.set()
        self.set_status("Stopping search safely... Keeping results already collected.")

    def worker(self, queries):
        """Fast concurrent public-web sweep.

        The old version ran every engine one after another, so dozens of
        platform targets multiplied into a very slow serial queue. This
        version keeps the same architecture but runs a controlled number of
        requests concurrently and uses short network timeouts.
        """
        internal_engines = ["Bing", "DuckDuckGo", "Google", "Brave"]
        normal_queries = [q for q in queries if not q.startswith("site:")]
        social_queries = [q for q in queries if q.startswith("site:")]

        # General discovery gets all providers. For the large social sweep,
        # two providers are enough to reduce duplicate work and latency.
        jobs = (
            [(q, e) for q in normal_queries for e in internal_engines] +
            [(q, e) for q in social_queries for e in ["Bing", "DuckDuckGo"]]
        )
        total = max(1, len(jobs))
        collected = []
        completed = 0
        lock = threading.Lock()

        def run_job(job):
            query, engine = job
            if self.stop_event.is_set():
                return query, engine, []
            try:
                return query, engine, search_engine(engine, query)
            except Exception:
                return query, engine, []

        # Eight workers is responsive on a phone without creating hundreds
        # of simultaneous connections.
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(run_job, job) for job in jobs]
            for future in as_completed(futures):
                if self.stop_event.is_set():
                    # Do not wait for new work; already completed results stay.
                    for f in futures:
                        f.cancel()
                    break

                query, engine, found = future.result()
                completed += 1
                self.ui_progress(completed / total * 100)
                self.ui_status(
                    f"Fast public sweep • {completed}/{total} • {self.platform_label(query)}"
                )

                batch = []
                for result in found:
                    result["query"] = query
                    result["matches"] = self.calculate_matches(result)
                    result["platform"] = self.platform_label(query)
                    batch.append(result)
                    collected.append(result)

                if batch:
                    self.ui_add_results(batch)

        unique = OrderedDict()
        for result in collected:
            url = result.get("url", "")
            if url and url not in unique:
                unique[url] = result

        self.results = list(unique.values())
        stopped = self.stop_event.is_set()
        Clock.schedule_once(lambda *_: self.finish_search(len(self.results), stopped))

    def platform_label(self, query):
        if query.startswith("site:"):
            return query.split("site:", 1)[1].split()[0]
        return "General Web"

    def ui_add_results(self, batch):
        def add(_dt):
            # Deduplicate against currently displayed results while searching.
            existing = {r.get("url") for r in self.results}
            for item in batch:
                if item.get("url") not in existing:
                    self.results.append(item)
                    existing.add(item.get("url"))
            self.refresh_results()
        Clock.schedule_once(add)

    def ui_progress(self, value):
        Clock.schedule_once(lambda *_: setattr(
            self.progress, "value", min(100, value)
        ))

    def ui_status(self, text):
        Clock.schedule_once(lambda *_: self.set_status(text))

    def finish_search(self, count, stopped=False):
        self.searching = False
        self.search_button.disabled = False
        self.stop_button.disabled = True
        self.clear_button.disabled = False
        if stopped:
            self.set_status(f"Search stopped • {count} public leads preserved and displayed.")
        else:
            self.progress.value = 100
            self.set_status(f"Broad research completed • {count} public leads collected.")
        self.refresh_results()

    def set_filter(self, value):
        self.current_filter = value
        for key, button in self.filter_buttons.items():
            button.background_color = BLUE if key == value else CARD2
        self.refresh_results()

    def refresh_results(self):
        self.result_box.clear_widgets()

        visible = []
        for result in self.results:
            matches = len(result.get("matches", []))
            query = result.get("query", "")

            if self.current_filter == "STRONG" and matches < 2:
                continue
            if self.current_filter == "PLATFORMS" and "site:" not in query:
                continue

            visible.append(result)

        self.results_title.text = (
            f"RESEARCH LEADS  •  {len(visible)} RESULTS"
        )

        if not visible:
            if self.results:
                self.result_box.add_widget(self.text_label(
                    "No leads match this filter.",
                    11, MUTED, False,
                    halign="center",
                    size_hint_y=None,
                    height=dp(70),
                ))
            else:
                self.show_empty()
            return

        for result in visible:
            self.result_box.add_widget(ResultCard(result, self))

    def open_query(self, query):
        # Open a broad Google query for manual review from a result card.
        webbrowser.open(make_url(SEARCH_ENGINES["Google"], query))

    def clear_all(self, *_):
        if self.searching:
            return
        self.stop_event.clear()
        for field in [
            self.name, self.country, self.region, self.institution
        ]:
            field.text = ""

        self.results = []
        self.progress.value = 0
        self.current_filter = "ALL"
        for key, button in self.filter_buttons.items():
            button.background_color = BLUE if key == "ALL" else CARD2

        self.set_status("Ready. Enter a name and optional clues.")
        self.refresh_results()
        self.go_top()

    def go_top(self):
        self.page_scroll.scroll_y = 1

    def set_status(self, text):
        self.status.text = text

    def popup(self, title, message):
        content = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10),
        )
        content.add_widget(self.text_label(
            message, 11, WHITE, False,
            halign="center", valign="middle"
        ))
        close = Button(
            text="OK",
            size_hint_y=None,
            height=dp(40),
            background_normal="",
            background_color=BLUE,
        )
        content.add_widget(close)

        pop = Popup(
            title=title,
            content=content,
            size_hint=(0.88, 0.30),
            separator_color=CYAN,
        )
        close.bind(on_release=pop.dismiss)
        pop.open()


class CyberstarApp(App):
    def build(self):
        self.title = "Cyberstar"
        Window.clearcolor = BG
        return CyberstarRoot()


if __name__ == "__main__":
    CyberstarApp().run()
