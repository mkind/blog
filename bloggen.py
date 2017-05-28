#!/usr/bin/env python3
# coding: utf8

from datetime import datetime
import json
import sys
import os
import re

TITLE_LEN = 100
RSS_DAYS_MAX = 30
BLOG_DAYS_MAX = 25
SOURCE_DIR = "raw"
DEST_DIR = "entries"
BLOG_DOMAIN = "https://blog.mknd.net"

files = []

TAG_RE = re.compile(r'<[^>]+>')

__author__ = "mkind"


def remove_tags(text):
    res = TAG_RE.sub('', text)
    res = res.replace("&", "&amp;")
    return res


with open("templates/entry.tmpl") as f:
    ENTRY_HTML = f.read()

with open("templates/day.tmpl") as f:
    DAY_HTML = f.read()

with open("templates/body.tmpl") as f:
    BODY_HTML = f.read()

with open("templates/meta.tmpl") as f:
    META_HTML = f.read()

with open("templates/all.tmpl") as f:
    ALL_HTML = f.read()

with open("templates/rss_item.tmpl") as f:
    RSS_ITEM_XML = f.read()

with open("templates/rss.tmpl") as f:
    RSS_XML = f.read()

for dirname, dirnames, filenames in os.walk(SOURCE_DIR):
    for filename in sorted(filenames, reverse=True):
        if ".swp" in filename:
            continue
        files.append(os.path.join(dirname, filename))
all_days = dict()

jsondecoder = json.JSONDecoder(strict=False)

for fileentry in files:
    content = open(fileentry, "rt", encoding="utf-8", errors="replace").read()
    json_data = jsondecoder.decode(content)
    date = datetime.strptime(json_data["date"], "%Y-%m-%d %H:%M:%S")
    author = json_data["author"]
    entry = json_data["entry"]
    path = "{year}/{month}/{day}".format(
                year=date.year,
                month=date.month,
                day=date.day
            )
    fn = date.strftime("%H%M%S") + ".html"
    day = date.strftime("%d %b %Y")
    article_link = "/" + path + "/" + fn

    sys.stdout.write("file %s.." % (fn))

    # create entry html
    entry_html = ENTRY_HTML.format(entry=entry, article_link=article_link)

    # create rss item
    article_link_total = BLOG_DOMAIN + article_link
    rss_item_xml = RSS_ITEM_XML.format(
        title=remove_tags(entry)[:TITLE_LEN] + "..",
        link=article_link_total,
        author=author,
        description=entry,
        guid=article_link_total,
        date=date.strftime("%a, %d %b %Y %H:%M:%S +0100")
    )

    # associate entry with
    d = date.strftime("%Y%m%d")
    if d in all_days:
        all_days[d]['html'].append(entry_html)
        all_days[d]['rss'].append(rss_item_xml)
    else:
        all_days[d] = {
                    "html": [entry_html],
                    "rss": [rss_item_xml],
                    "day": day
                    }

    # if entry is shown as single article (e.g. by requesting article URI),
    # use day template with only the requested article
    day_html = DAY_HTML.format(date=day, entries=entry_html)

    # body html
    body_html = BODY_HTML.format(content=day_html)

    # overall page
    header_html = META_HTML.format(
                    last_modified=date.strftime("%a, %d %b %Y %H:%M:%S GMT")
                  )
    all_html = ALL_HTML.format(header=header_html, body=body_html)

    # store entry html files
    abs_path = DEST_DIR + "/" + path + "/" + fn
    os.makedirs(DEST_DIR + "/" + path, exist_ok=True)

#    if os.path.isfile(abs_path):
#        continue

    with open(abs_path, "bw") as f:
        f.write(all_html.encode("utf-8", "replace"))
        sys.stdout.write("written\n")

days_html_for_one_page = []


def write_page(days_html_for_one_page, fn):
    days_html = "\n".join(days_html_for_one_page)

    # body html
    body_html = BODY_HTML.format(content=days_html)

    # overall page
    date = datetime.now()
    header_html = META_HTML.format(
                    last_modified=date.strftime("%a, %d %b %Y %H:%M:%S GMT")
                  )
    all_html = ALL_HTML.format(header=header_html, body=body_html)

    # store entry html files
    abs_path = DEST_DIR + "/" + fn + ".html"

    with open(abs_path, "bw") as f:
        sys.stdout.write("%s (entries:%d).." % (
            abs_path,
            len(days_html_for_one_page)))
        f.write(all_html.encode("utf-8", "replace"))
        sys.stdout.write("written\n")


count = 0
rss_xml_all_items = ""
for day in sorted(iter(all_days), reverse=True)[:100]:
    entries = all_days[day]
    entries_html = "\n".join(entries["html"])
    rss_items_per_day = "\n".join(entries["rss"])
    day_html = DAY_HTML.format(date=entries["day"], entries=entries_html)

    if len(days_html_for_one_page) < BLOG_DAYS_MAX:
        days_html_for_one_page.append(day_html)

    else:
        write_page(days_html_for_one_page, str(count))
        count += 1
        days_html_for_one_page = []

    # adding item to rss
    if count < RSS_DAYS_MAX:
        rss_xml_all_items += rss_items_per_day

if days_html_for_one_page:
    write_page(days_html_for_one_page, str(count))

# build rss
rss_xml = RSS_XML.format(
        lastbuild=datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
        item=rss_xml_all_items)

rss_path = DEST_DIR + "/rss.xml"

with open(rss_path, "bw") as f:
    sys.stdout.write("%s.." % (abs_path))
    f.write(rss_xml.encode("utf-8", "replace"))
    sys.stdout.write("written\n")
