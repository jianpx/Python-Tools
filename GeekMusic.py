#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib, urllib2
from sys import argv
import re, time

#constants start
DOMAIN = 'http://www.google.cn/'
SEARCH_SUFFIX = 'music/search'
ALBUM_SUFFIX = 'music/album'
DOWNLOAD_SUFFIX = 'music/top100/musicdownload'
#to control not to get angry with google(don't want to get captcha_image)
SLEEP_TIME = 0.5
#constants end

def log(msg):
    print msg

#GeekMusic Library starts
class GeekMusic(object):
    '''
    Google music Searcher, you can get google songs download url at one time
    expose api: search_song and search_album and search_url
    '''
    def __init__(self,
            domain=DOMAIN,
            search_suffix=SEARCH_SUFFIX,
            album_suffix=ALBUM_SUFFIX,
            download_suffix=DOWNLOAD_SUFFIX):

        self.domain = domain
        self.search_url = domain + search_suffix
        self.album_url = domain + album_suffix
        self.download_url = domain + download_suffix
        self.category = set(['album', 'song', 'artist'])
        #匹配网页上的song id，匹配出来的格式是类似：S76601ee8f92a3fc8
        #%3D是=号的quote之后的值
        self.re_songid = re.compile(r'/html/download\.html\?id%3D(?P<id>\w+)\\x26resnum')
        self.re_songurl = re.compile(r'http://.*\.mp3')
        #self.cache = {}

    def _extract_songid(self, html):
        return self.re_songid.findall(html)

    def _get_songurl(self, html):
        songurl = self.re_songurl.findall(html)
        if not songurl:
            return ''
        elif len(songurl) == 1:
            return urllib.unquote(urllib.unquote(songurl[0]))
        #TODO
        else:
            raise Exception('Unexpected more than 2 songs')

    def _fetch_songs(self, song_html_src, interval=1):
        songs = []
        id_list = self._extract_songid(song_html_src)
        for songid in id_list:
            url = self._make_url(self.download_url, {'id':songid})
            html = self._fetch_url(url)
            if html:
                song_url = self._get_songurl(html)
                if song_url:
                    song = {'id': songid, 'url': song_url}
                    songs.append(song)
                    time.sleep(interval)
        return songs

    def _make_url(self, url, req_data={}):
        return '%s?%s' % (url, urllib.urlencode(req_data))

    def _fetch_url(self, url):
        try:
            opener = urllib2.urlopen(url)
            c = opener.read()
            return c
        except IOError,e:
            #TODO: log
            log('url: %s , error: %s' % (url, str(e)))
            return None

    def search_album(self, album_id):
        req_url = self._make_url(self.album_url, {'id': album_id})
        songs = self.search_songurl(req_url)
        return songs

    def search_song(self, q):
        req_url = self._make_url(self.search_url, {'q': q, 'cat': 'song'})
        songs = self.search_songurl(req_url)
        return songs

    def search_songurl(self, req_url):
        songlist_html = self._fetch_url(req_url)
        if not songlist_html:
            return None
        songs = self._fetch_songs(songlist_html, interval=SLEEP_TIME)
        return songs


#GeekMusic Library ends

#Application starts
global_options = [
    [('-s', '--song'), {'type': 'string', 'dest': 'songname', 'help': 'name of song'}],
    [('-a', '--album'), {'type': 'string', 'dest': 'albumid', 'help': 'id of album'}],
    [('-u', '--url'), {'type': 'string', 'dest': 'songurl', 'help': 'url of song'}],
]

def get_options(args, options=global_options):
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options]")
    for opt in options:
        parser.add_option(*opt[0], **opt[1])

    opts, ret_args = parser.parse_args(args)
    return opts

def format_options(options=global_options):
    s = 'Options Syntax:\n%s'
    options_list = []
    for args, kwargs in options:
        temp = '\t%s\n\t%s\n\t\t%s' % (args[0], args[1], kwargs['help'])
        options_list.append(temp)
    return s % '\n'.join(options_list)

def usage():
    from os.path import basename
    print 'Usage: python %s [options]\n%s' % (basename(__file__), format_options())

def print_result(songs):
    if not songs:
        print 'no songs found!'
    else:
        for s in songs:
            print '%(url)s' % s

def main():
    if len(argv) == 1:
        usage()
    else:
        opts = get_options(argv[1:])
        gm = GeekMusic()
        songs = None
        print 'Searching ...'
        if opts.songname:
            songs = gm.search_song(opts.songname)
        elif opts.albumid:
            songs = gm.search_album(opts.albumid)
        elif opts.songurl:
            songs = gm.search_songurl(opts.songurl)
        print_result(songs)

def _test():
    q = argv[1]
    gm = GeekMusic()
    from time import time as now
    st = now()
    songs = gm.search_song(q)
    #songs = gm.search_album(q)
    et = now()
    print 'cost :%d seconds' % int(et - st)
    if songs:
        for s in songs:
            print 'id: %(id)s    url:%(url)s' % s

#Application ends

if __name__ == '__main__':
    main()
