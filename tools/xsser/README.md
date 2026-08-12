  ![XSSer](https://xsser.03c8.net/xsser/blackswarm_banner.png "XSSer v1.9 - Bl4ck Swarm!")

----------

 + Web: https://xsser.03c8.net

----------

  Cross Site "Scripter" (aka XSSer) is an automatic -framework- to detect, exploit and report XSS vulnerabilities in web-based applications.

  It provides several options to try to bypass certain filters and various special techniques for code injection.

  Key features:

     - [ > 1500 ] pre-installed XSS attacking vectors (automatic fuzzing).
     - Validation: each finding is verified for real executability. A context-aware engine tells apart executable contexts (HTML, JS, event handlers, javascript:/data: URIs) from harmless reflections, with an optional headless-browser reverse connection (--reverse-check) to confirm findings and cut false positives.
     - Targeting: URL, file, stdin/pipe, raw HTTP request (-r), 'dorking' (multiple engines) and crawler.
     - Injection: GET/POST, Cookie/User-Agent/Referer, DOM and HTTP Response Splitting.
     - Evasion: per-WAF bypassers + character-encoding bypassers; proxy/Tor; client-certificate auth.
     - Reporting: PDF (professional), XML and JSON (for CI / pipelines).

  It can also bypass-exploit code on several WAFs:

     [Cloudflare]: Cloudflare WAF
     [Akamai]: Akamai (Kona / App & API Protector)
     [AWS]: AWS WAF
     [Azure]: Azure Front Door WAF
     [Imperva]: Imperva (Incapsula / Cloud WAF)
     [F5]: F5 BIG-IP ASM / Advanced WAF
     [Barracuda]: Barracuda WAF
     [ModSec]: Mod-Security + OWASP CRS v3
     [Wordfence]: Wordfence (WordPress)
     [Sucuri]: Sucuri (CloudProxy)
     [FortiWeb]: Fortinet FortiWeb
     [WebKnight]: AQTRONIX WebKnight

  ![XSSer](https://xsser.03c8.net/xsser/blackswarm_options.png "XSSer v1.9 - WAF Bypassers & Encoders")

----------

#### Installing:

XSSer runs on many platforms. It requires Python (3.x) and the following libraries:

    - python3-pycurl - Python bindings to libcurl (Python 3)
    - python3-bs4 - error-tolerant HTML parser for Python 3
    - python3-geoip - Python3 bindings for the GeoIP IP-to-country resolver library
    - python3-gi - Python 3 bindings for gobject-introspection libraries
    - python3-selenium - Python3 bindings for Selenium
    - firefoxdriver - Firefox WebDriver support
    - ddgs - DuckDuckGo search library (used by the 'dorking' engine)
    - fpdf2 - PDF generation library (used by the '--pdf' report exporter)

On Debian-based systems (ex: Ubuntu), run: 

    sudo apt-get install python3-pycurl python3-bs4 python3-geoip python3-gi python3-selenium firefoxdriver python3-fpdf2

On other systems such as: Kali, Ubuntu, ArchLinux, ParrotSec, Fedora, etc... also run:

    sudo pip3 install pycurl bs4 pygeoip PyGObject selenium ddgs fpdf2

####  Source libs:

   * Python: https://www.python.org/downloads/
   * PyCurl: http://pycurl.sourceforge.net/
   * PyBeautifulSoup4: https://pypi.org/project/beautifulsoup4/
   * PyGeoIP: https://pypi.org/project/pygeoip/
   * PyGObject: https://pypi.org/project/gobject/
   * PySelenium: https://pypi.org/project/selenium/
   * ddgs: https://pypi.org/project/ddgs/
   * fpdf2: https://pypi.org/project/fpdf2/

----------

####  License:

  XSSer is released under the GPLv3. You can find the full license text
in the [LICENSE](./docs/LICENSE) file.

----------

####  Screenshots:

  ![XSSer](https://xsser.03c8.net/xsser/blackswarm_shell.png "XSSer Shell")

  ![XSSer](https://xsser.03c8.net/xsser/blackswarm_dorking.png "XSSer Dorking (multiple engines)")

  ![XSSer](https://xsser.03c8.net/xsser/blackswarm_gui.png "XSSer GTK GUI")

  ![XSSer](https://xsser.03c8.net/xsser/blackswarm_gui_waf.png "XSSer GUI - Anti-antiXSS/IDS WAF Bypassers")

  ![XSSer](https://xsser.03c8.net/xsser/blackswarm_gui_bypasser.png "XSSer GUI - Encoders & Bypassers")

  ![XSSer](https://xsser.03c8.net/xsser/blackswarm_report.png "XSSer PDF Report")
  
  ![XSSer](https://xsser.03c8.net/xsser/blackswarm_map.png "XSSer GeoMap")

