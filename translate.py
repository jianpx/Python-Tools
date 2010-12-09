#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib
from BeautifulSoup import BeautifulSoup
from sys import argv
import re

__doc__ = '''
@desc: simply print the chinese meaning of english word, mainly for self usage. ^_^
@requirement: BeautifulSoup . you can run 'sudo apt-get install python-beautifulsoup' to install it.
@usage : python translate.py word
@memo: for convinience, you can put the script to your bin directory or to make alias command
'''

class Translate(object):
    def __init__(self):
        self.api = 'http://dict.baidu.com/s?'
        self.q = {
            'wd': '',
            'tn': 'dict',
        }

    def run(self, word):
        self._get_html_sourse(word)
        self._get_content("enc")
        self._remove_tag()
        self.print_result()

    def _get_html_sourse(self, word):
        self.q['wd'] = word
        #not support post method!
        url = self.api + urllib.urlencode(self.q)
        c = urllib.urlopen(url).read()
        self.htmlsourse = unicode(c, "gb2312","ignore").encode("utf-8","ignore")

    def _get_content(self,div_id):
        soup = BeautifulSoup("".join(self.htmlsourse))
        self.data = str(soup.find("div",{"id":div_id}))

    def _remove_tag(self):
        soup = BeautifulSoup(self.data)
        self.outtext = ''.join([element  for element in soup.recursiveChildGenerator() if isinstance(element,unicode)])

    def print_result(self):
        '''
        format and print the result
        '''
        #find the \d\. out
        p = re.compile('(\d\.[^\.])')
        self.outtext = p.sub('\n\g<1>', self.outtext)

        #find below names out
        names = [u'及物动词 vt\.', u'不及物动词 vi\.', u'名词 n\.', u'缩写词 abbr\.', \
                u'形容词 a\.', u'代词 pron\.', u'副词 ad\.', u'冠词 art\.', u'介词 prep\.']
        pt = '(%s)' % '|'.join(names)
        p = re.compile(pt)
        self.outtext = p.sub('\n\n\g<1>', self.outtext)

        #delete all the url
        url_pattern = 'https?://([-\w\.]+)+(:\d+)?(/([\w/_\.]*(\?\S+)?)?)?\.*'
        p = re.compile(url_pattern)
        self.outtext = p.sub('', self.outtext)
        print self.outtext

def usage():
    print 'Usage: python %s word' % __file__

if __name__ == "__main__":
    if len(argv) == 2 and argv[1]:
        Translate().run(argv[1])
    else:
        usage()
