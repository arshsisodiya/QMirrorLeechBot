# Implemented by https://github.com/junedkh

import random

from pyshorteners import Shortener as pyShortener
from requests import get as rget, post as rpost
from base64 import b64encode
from urllib.parse import quote
from urllib3 import disable_warnings

from bot import LOGGER, SHORTENER, SHORTENER_API

def short_url(longurl, spes=None):
    tempvar = spes or SHORTENER
    if not tempvar: return longurl
    elif ("v.gd" in tempvar) or ("is.gd" in tempvar):
        try:
            url = quote(longurl)
            response = rget(f"https://{tempvar}/create.php?format=json&url={url}&logstats=1")
            if response.ok:
                if 'shorturl' in response.json(): return response.json()['shorturl']
            else:
                LOGGER.error("response was not ok")
                return longurl
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "da.gd" in tempvar:
        try: return pyShortener().dagd.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "ttm.sh" in tempvar:
        try: return pyShortener(domain='ttm.sh').nullpointer.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "clck.ru" in tempvar:
        try: return pyShortener().clckru.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "chilp.it" in tempvar:
        try: return pyShortener().chilpit.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "osdb" in tempvar:
        try: return pyShortener().osdb.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "owly" in tempvar:
        try: return pyShortener().owly.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            return longurl
    elif "tinyurl" in tempvar:
        try:
            link = pyShortener().tinyurl.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl

    # requires shortener api

    if not SHORTENER_API: return longurl
    elif "shorte.st" in tempvar:
        disable_warnings()
        link = rget(f'http://api.shorte.st/stxt/{SHORTENER_API}/{longurl}', verify=False).text
    elif "bc.vc" in tempvar: # sample SHORTENER_API 2dgdg5f1fgag7cg6f0622&uid=45634
        url = quote(b64encode(longurl.encode("utf-8")))
        try:
            link = rget(f"https://bc.vc/api.php?key={SHORTENER_API}&url={url}", verify=False).text
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "pubiza" in tempvar:
        try:
            url = quote(b64encode(longurl.encode("utf-8")))
            key, tip = SHORTENER_API.split(' ')
            link = rget(f"http://pubiza.com/api.php?token={key}&url={url}&ads_type={tip}", verify=False).text
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "linkvertise" in tempvar:
        url = quote(b64encode(longurl.encode("utf-8")))
        linkvertise = [
            f"https://link-to.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}",
            f"https://up-to-down.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}",
            f"https://direct-link.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}",
            f"https://file-link.net/{SHORTENER_API}/{random.random() * 1000}/dynamic?r={url}"]
        link = random.choice(linkvertise)
    elif "bitly.com" in tempvar:
        try:
            shorten_url = "https://api-ssl.bit.ly/v4/shorten"
            params = {"long_url": longurl}
            headers = {"Authorization": f"Bearer {SHORTENER_API}"}
            response = rpost(shorten_url, json=params, headers=headers).json()
            link = response["link"]
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "post" in tempvar:
        try:
            s = pyShortener(api_key=SHORTENER_API)
            link = s.post.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "cutt.ly" in tempvar:
        try:
            s = pyShortener(api_key=SHORTENER_API)
            link = s.cuttly.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "adf.ly" in tempvar:
        try:
            key, uid = SHORTENER_API.split(' ')
            s = pyShortener(api_key=key,user_id=uid)
            link = s.adfly.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "shortcm" in tempvar:
        try:
            api_key, domain = SHORTENER_API.split(' ')
            s = pyShortener(api_key=api_key, domain=domain)
            link = s.shortcm.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "tinycc" in tempvar:
        try:
            api_key, login = SHORTENER_API.split(' ')
            s = pyShortener(api_key=api_key, login=login)
            link = s.tinycc.short(longurl)
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    elif "ouo.io" in tempvar:
        disable_warnings()
        try: link = rget(f'http://ouo.io/api/{SHORTENER_API}?s={longurl}', verify=False).text
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    else:
        try: link = rget(f'https://{tempvar}/api?api={SHORTENER_API}&url={quote(longurl)}&format=text').text
        except Exception as e:
            LOGGER.error(e)
            link = longurl
    if len(link) == 0:
        LOGGER.error("Something is Wrong with the url shortener")
        return longurl
    return link
