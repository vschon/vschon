import urllib
import urllib2
import contextlib

def login():

    login_url = 'http://www.truefx.com/?page=logina'
    username = 'yangrucheng'
    password = '871108'
    cookies = urllib2.HTTPCookieProcessor()
    opener = urllib2.build_opener(cookies)
    urllib2.install_opener(opener)

    opener.open(login_url)
    try:
        token = [x.value for x in cookies.cookiejar if x.name == 'csrftoken'][0]
    except IndexError:
        return False, 'no csrftoken'
