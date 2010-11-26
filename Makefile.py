# -*- coding: utf-8 -*-

import re
import time
import sys
import codecs
from os.path import expanduser, basename, splitext

from mklib.common import MkError
from mklib import Task, mk
from mklib import sh

sys.path.insert(0, expanduser("~/tm/python-markdown2/lib"))
import markdown2


class render(Task):
    """render no.de.markdown"""
    default = True
    def make(self):
        path = "examples/no.de.markdown"
        markdown = codecs.open(path, 'r', 'utf-8').read()
        metadata = {}
        if markdown.startswith("---"):
            _, metastr, markdown = re.compile(r"^---[ \t]*$", re.M).split(
                markdown, 2)
            for line in metastr.strip().splitlines(False):
                line = line.strip()
                if not line:
                    continue
                k, v = line.split(':', 1)
                metadata[k.strip()] = v.strip()
        if "title" not in metadata:
            metadata["title"] = splitext(basename(path))[0] + " API"
        html = restdown(metadata, markdown)
        codecs.open("foo.html", "w", "utf-8").write(html)
        self.log.info("wrote 'foo.html'")

opts = {
    "extras": {
        "toc": True,
        "markdown-in-html": True,
    }
}


class Markdown(markdown2.Markdown):
    _seen_first_h1 = False
    def header_id_from_text(self, text, prefix, n):
        if n == 1 and not self._seen_first_h1:
            self._seen_first_h1 = True
        elif n in (1, 2):
            return super(Markdown, self).header_id_from_text(text, prefix, n)

    _endpoint_header_re = re.compile(
        r'''^(<h2 id=".*?">)([A-Z]+\s+.*?)(</h2>)$''', re.M)
    _pre_command_block_re = re.compile(r'<pre><code>\$ (.*?)</code></pre>', re.S)
    def postprocess(self, text):
        # Add markup to endpoint h2's for styling.
        text = self._endpoint_header_re.sub(
            r'\1<span>\2</span>\3', text)
        # Add "req" class and sexify pre-blocks starting with '$'.
        text = self._pre_command_block_re.sub(
            r'<pre class="shell"><code class="prompt">\1</code></pre>', text)
        return text

    _endpoint_re = re.compile(r'^([A-Z]+)(\s+)(.*?)$')
    def _toc_add_entry(self, level, id, name):
        if level == 2:
            name = self._endpoint_re.sub(
                r'<span class="verb">\1</span>\2<span>\3</span>', name)
        super(Markdown, self)._toc_add_entry(level, id, name)


def restdown(metadata, markdown):
    #TODO: START HERE
    # - "endpoint" JS. Does the new markup and lack of "enpoint fixed" work?
    # - fill in content

    html = Markdown(**opts).convert(markdown)
    metadata["toc_html"] = html.toc_html

    print html.toc_html
    print html._toc

    bits = []
    bits.append(u"""<!DOCTYPE html>
<html lang="en">
<head>
    <title>%(title)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <link rel="stylesheet" type="text/css" href="restdown.css">
</head>
<body>
    <div id="header">
        <h1>%(title)s Documentation</h1>
    </div>
    <div id="sidebar">
%(toc_html)s
    </div>
    <div id="content">
""" % metadata)
    bits.append(html)
    bits.append(u"""
    </div>
</body>
</html>""")
    return u''.join(bits)
