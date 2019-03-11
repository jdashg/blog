#! /usr/bin/env python3
assert __name__ == '__main__'

import pathlib
import re
import string

class IndentedText(object):
   def __init__(self, per_indent):
      self.per_indent = per_indent
      self.cur_indent = ''
      self.lines = []

   def add(self, text):
      self.lines += (self.cur_indent + x for x in text.split('\n'))

   def indent(self, n=1):
      ret = IndentedText(self.per_indent)
      ret.cur_indent = self.cur_indent + n*self.per_indent
      ret.lines = self.lines
      return ret

   def __str__(self):
      return '\n'.join(self.lines)

# Posts

def glob_non_hidden(path):
   for sub in path.iterdir():
      if sub.name[0] == '.':
         continue
      if sub.is_dir():
         yield from glob_non_hidden(sub)
      else:
         yield sub

posts = glob_non_hidden(pathlib.Path('.'))
posts = (x for x in posts if x.suffix in ('.html', '.md'))

RE_DIGIT = re.compile('[0-9]')

def flip_digit(x):
   return chr(ord('0') + ord('9') - ord(x))

def blog_sort_key(path):
   key = ('\xff' + x for x in path.parts)
   key = '/'.join(key)
   key = RE_DIGIT.sub(flip_digit, key)
   key = key.lower()
   return key

posts = sorted(posts, key=blog_sort_key)


POSTS = IndentedText('   ').indent(2)
POSTS.add('<ul>')

POSTS_list = POSTS.indent()
for cur in posts:
   print(cur.as_posix())
   url_path = cur
   if cur.suffix == '.md':
      url_path = cur.with_suffix('.html')
   POSTS_list.add('<li><a href="{}">{}</a>'.format(url_path.as_posix(), cur.as_posix()))

POSTS.add('</ul>')


html_template = string.Template('''<!DOCTYPE html>
<html>
   <head>
      <meta charset='utf-8'>
      <title>Gen-Index</title>
   </head>
   <body>
      <style>
body {
   font-family: sans-serif;
}
li {
   margin-bottom: 4px;
}
      </style>
   <h1>Posts</h1>
$posts
   </body>
</html>
''')
html = html_template.substitute(posts=POSTS)
pathlib.Path('index.html').write_text(html)
