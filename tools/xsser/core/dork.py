#!/usr/bin/env python
# -*- coding: utf-8 -*-"
# vim: set expandtab tabstop=4 shiftwidth=4:
"""
This file is part of the XSSer project, https://xsser.03c8.net

Copyright (c) 2010/2026 | psy <epsylon@riseup.net>

xsser is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free
Software Foundation version 3 of the License.

xsser is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with xsser; if not, write to the Free Software Foundation, Inc., 51
Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
........

List of search engines: https://en.wikipedia.org/wiki/List_of_search_engines

Currently supported: duck(default), bing, brave, mojeek, yahoo, startpage, ecosia

"""
import urllib.request, urllib.error, urllib.parse, traceback, re, random, time, ssl, base64, warnings
urllib.request.socket.setdefaulttimeout(5.0)

DEBUG = 0

class Dorker(object):
    def __init__(self, engine='duck'):
        self._engine = engine
        self.search_engines = [] # available dorking search engines
        self.search_engines.append('bing')
        self.search_engines.append('duck')
        self.search_engines.append('brave')
        self.search_engines.append('mojeek')
        self.search_engines.append('yahoo')
        self.search_engines.append('startpage')
        self.search_engines.append('ecosia')
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
        self.agents = [] # user-agents
        try:
            f = open("core/fuzzing/user-agents.txt").readlines() # set path for user-agents
        except:
            f = open("fuzzing/user-agents.txt").readlines() # set path for user-agents when testing
        for line in f:
            self.agents.append(line)

    def _query_string(self, search):
        return str(search), 'instreamset:(url):"' + str(search) + '"'

    def _fetch(self, url, headers, timeout=10):
        req = urllib.request.Request(url, None, headers)
        return urllib.request.urlopen(req, context=self.ctx, timeout=timeout).read().decode('utf-8', errors='replace')

    def _match(self, html, patterns):
        for pat in patterns:
            links = re.findall(pat, html)
            if links:
                return links
        return []

    def _import_ddgs(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            try:
                from ddgs import DDGS
                return DDGS
            except ImportError:
                try:
                    from duckduckgo_search import DDGS
                    return DDGS
                except ImportError:
                    pass
        try:
            from core._ensure import ensure
        except ImportError:
            return None
        if ensure('ddgs', 'ddgs') is None:
            return None
        try:
            from ddgs import DDGS
            return DDGS
        except ImportError:
            return None

    def _bing_decode(self, raw):
        raw = raw.replace('&amp;', '&')
        m = re.search(r'[?&]u=a1([^&]+)', raw)
        if not m:
            return raw
        token = m.group(1)
        try:
            b64 = token + '=' * ((4 - len(token) % 4) % 4)
            return base64.urlsafe_b64decode(b64).decode('utf-8', errors='replace')
        except Exception:
            return raw

    def _yahoo_decode(self, raw):
        if 'RU=' in raw:
            piece = raw.rsplit('RU=', 1)[1]
            piece = piece.split('/RK=', 1)[0]
            return urllib.parse.unquote(piece)
        return raw

    def dork(self, search):
        """
        Perform a search and return links.
        """
        engine = self._engine
        sep, q = self._query_string(search)
        user_agent = random.choice(self.agents).strip() # set random user-agent
        referer = '127.0.0.1' # set referer to localhost / WAF black magic!
        headers = {'User-Agent' : user_agent, 'Referer' : referer, 'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language' : 'en-US,en;q=0.5'}
        url_links = []
        if engine == 'bing':
            search_url = 'https://www.bing.com/search?' + urllib.parse.urlencode({'q' : q, 'first' : 0})
            print("\nSearching query:", urllib.parse.unquote(search_url))
            try:
                html_data = self._fetch(search_url, headers)
            except urllib.error.URLError:
                return self._cannot_connect()
            raw = self._match(html_data, [r'<a\s+class="tilk"[^>]*href="([^"]+)"', r'<h2><a[^>]+href="([^"]+)"[^>]*>'])
            url_links = [self._bing_decode(r) for r in raw]
        elif engine == 'duck':
            print("\nSearching query:", 'ddgs.DDGS().text(' + repr(q) + ')')
            DDGS = self._import_ddgs()
            if DDGS is None:
                print("\n[Error] Missing lib: 'ddgs'. Install it with: pip3 install ddgs\n")
                return []
            results = None
            attempt = 0
            while attempt < 3:
                try:
                    results = list(DDGS().text(q, safesearch='off', max_results=30))
                    break
                except Exception as e:
                    attempt = attempt + 1
                    if 'Ratelimit' in str(e) or '202' in str(e):
                        time.sleep(2 * attempt)
                        continue
                    if DEBUG:
                        traceback.print_exc()
                    return self._cannot_connect()
            if results is None:
                return self._cannot_connect()
            for r in results:
                if isinstance(r, dict) and r.get('href'):
                    url_links.append(r['href'])
        elif engine == 'brave':
            search_url = 'https://search.brave.com/search?' + urllib.parse.urlencode({'q' : q})
            print("\nSearching query:", urllib.parse.unquote(search_url))
            try:
                html_data = self._fetch(search_url, headers)
            except urllib.error.URLError:
                return self._cannot_connect()
            url_links = self._match(html_data, [r'<a\s+href="([^"]+)"[^>]*class="(?:h|result-header|snippet-title)"', r'<a class="(?:h|result-header|snippet-title)"\s+href="([^"]+)"', r'<a\s+href="(https?://[^"]+)"\s+rel="noopener'])
        elif engine == 'mojeek':
            search_url = 'https://www.mojeek.com/search?' + urllib.parse.urlencode({'q' : q})
            print("\nSearching query:", urllib.parse.unquote(search_url))
            try:
                html_data = self._fetch(search_url, headers)
            except urllib.error.URLError:
                return self._cannot_connect()
            url_links = self._match(html_data, [r'<a class="ob"\s+href="([^"]+)"', r'<a class="title"\s+href="([^"]+)"', r'<a\s+href="(https?://[^"]+)"[^>]*class="title"'])
        elif engine == 'yahoo':
            search_url = 'https://search.yahoo.com/search?' + urllib.parse.urlencode({'p' : q, 'b' : 1})
            print("\nSearching query:", urllib.parse.unquote(search_url))
            try:
                html_data = self._fetch(search_url, headers)
            except urllib.error.URLError:
                return self._cannot_connect()
            raw = self._match(html_data, [r'<a class="d-ib[^"]*"\s+href="([^"]+)"', r'<h3 class="title"[^>]*>\s*<a\s+href="([^"]+)"', r'<a\s+href="(https?://[^"]+RU=[^"]+)"'])
            url_links = [self._yahoo_decode(r) for r in raw]
        elif engine == 'startpage':
            search_url = 'https://www.startpage.com/do/search?' + urllib.parse.urlencode({'query' : q})
            print("\nSearching query:", urllib.parse.unquote(search_url))
            try:
                html_data = self._fetch(search_url, headers)
            except urllib.error.URLError:
                return self._cannot_connect()
            url_links = self._match(html_data, [r'<a class="w-gl__result-title result-link"\s+href="([^"]+)"', r'<a class="result-link"\s+href="([^"]+)"', r'<a\s+href="([^"]+)"\s+class="result-link"'])
        elif engine == 'ecosia':
            search_url = 'https://www.ecosia.org/search?' + urllib.parse.urlencode({'q' : q})
            print("\nSearching query:", urllib.parse.unquote(search_url))
            try:
                html_data = self._fetch(search_url, headers)
            except urllib.error.URLError:
                return self._cannot_connect()
            url_links = self._match(html_data, [r'<a class="result-title"\s+href="([^"]+)"', r'<a\s+href="([^"]+)"[^>]*class="result__title"', r'<a\s+data-test-id="result-link"\s+href="([^"]+)"'])
        else:
            print("\n[Error] This search engine is not being supported!\n")
            print('-'*25)
            print("\n[Info] Use one from this list:\n")
            for e in self.search_engines:
                print("+ "+e)
            print("\n ex: xsser -d 'profile.asp?num=' --De 'duck'")
            print(" ex: xsser -l --De 'startpage'")
            print("\n[Info] Or try them all:\n\n ex: xsser -d 'news.php?id=' --Da\n")
            return []
        print("\n[Info] Retrieving requested info...\n")
        found_links = []
        seen = set()
        for link in url_links:
            link = urllib.parse.unquote(link)
            if 'http' not in link:
                continue
            if engine == 'yahoo' and 'RU=https://www.yahoo.com/' in link:
                continue
            if search.upper() in link.upper(): # parse that search query is on url
                base = link.split(search, 1)[0]
                if base not in seen: # parse that target is not duplicated
                    seen.add(base)
                    found_links.append(link)
        if not found_links:
            print("\n[Error] Not any link found for that query!")
        return found_links

    def _cannot_connect(self):
        if DEBUG:
            traceback.print_exc()
        print("\n[Error] Cannot connect!")
        print("\n" + "-"*50)
        return []

if __name__ == '__main__':
    for a in ['bing', 'duck', 'brave', 'mojeek', 'yahoo', 'startpage', 'ecosia']:
        dork = Dorker(a)
        res = dork.dork("news.php?id=")
        if res:
            print("\n[+] Search Engine:", a, "| Found: ", len(res), "\n")
            for b in res:
                print(" *", b)
