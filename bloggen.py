#!/usr/bin/env python3
# coding: utf8

from datetime import datetime
import json
import sys
import os
import re

__author__ = "mkind"

TITLE_LEN = 100
RSS_ENTRIES_MAX = 30
BLOG_ENTRIES_MAX = 1000
SOURCE_DIR = "raw"
DEST_DIR = "entries"
BLOG_DOMAIN = "https://blog.mknd.net"
TAG_RE = re.compile(r'<[^>]+>')

files = []
all_entries = dict()
jsondecoder = json.JSONDecoder(strict=False)


def remove_tags(text):
    res = TAG_RE.sub('', text)
    res = res.replace("&", "&amp;")
    return res


with open("templates/entry.tmpl") as f:
    ENTRY_HTML = f.read()

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


def get_files(sources):
    """
    get a list of all files. ignore temporary files.
    """
    for dirname, dirnames, filenames in os.walk(sources):
        for filename in sorted(filenames, reverse=True):
            if ".swp" in filename or ".bak" in filename:
                continue
            files.append(os.path.join(dirname, filename))
    return files


def extract_blog_data(content):
    """
    gets blog data
    """
    json_data = jsondecoder.decode(content)
    date = datetime.strptime(json_data["date"],
                            "%Y-%m-%d %H:%M:%S")
    path = "{year}/{month}/{day}".format(
                    year=date.year,
                    month=date.month,
                    day=date.day
                )
    fn = date.strftime("%H%M%S") + ".html"

    entry = {
            "date": date,
            "author": json_data["author"],
            "entry": json_data["entry"],
            "title": json_data["title"],
            "day": date.strftime("%d %b %Y"),
            "fn": fn,
            "path": path,
            "article_link": "/" + path + "/" + fn
            }

    sys.stdout.write("file %s.." % (entry["article_link"]))
    return entry


def build_single_page_html(entry):
    entry_html = ENTRY_HTML.format(
                    title=entry["title"],
                    entry=entry["entry"],
                    date=entry["date"],
                    day=entry["day"],
                    article_link=entry["article_link"]
                )

    # body html
    body_html = BODY_HTML.format(content=entry_html)

    # overall page
    header_html = META_HTML.format(
                    last_modified=entry["date"].strftime("%a, %d %b %Y %H:%M:%S GMT")
                  )
    all_html = ALL_HTML.format(header=header_html, body=body_html)

    # store entry html files
    abs_path = DEST_DIR + "/" + entry["path"] + "/" + entry["fn"]
    os.makedirs(DEST_DIR + "/" + entry["path"], exist_ok=True)

    with open(abs_path, "bw") as f:
        f.write(all_html.encode("utf-8", "replace"))
        sys.stdout.write("written\n")


def build_all_page_html(all_entries):
    """
    Build a html page containing multiple entries.
    """
    count = 0
    entries_html_for_one_page = []

    for timestamp in sorted(iter(all_entries), reverse=True)[:100]:
        entry = all_entries[timestamp]
        entry_html = ENTRY_HTML.format(
                    title=entry["title"],
                    entry=entry["entry"],
                    date=entry["date"],
                    day=entry["day"],
                    article_link=entry["article_link"]
                )

        if len(entries_html_for_one_page) < BLOG_ENTRIES_MAX:
            entries_html_for_one_page.append(entry_html)

        else:
            write_page(entries_html_for_one_page, str(count))
            count += 1
            entries_html_for_one_page = []

    write_page(entries_html_for_one_page, str(count))


def build_all_page_rss(all_entries):
    """
    Build a rss page for multiple entries.
    """
    count = 0
    rss_xml_all_items = ""

    for timestamp in sorted(iter(all_entries), reverse=True)[:100]:
        entry = all_entries[timestamp]
        article_link_total = BLOG_DOMAIN + entry["article_link"]
        rss_item_xml = RSS_ITEM_XML.format(
            title=entry["title"],
            link=article_link_total,
            author=entry["author"],
            description=entry["entry"],
            guid=article_link_total,
            date=entry["date"].strftime("%a, %d %b %Y %H:%M:%S +0100")
        )

        # adding item to rss
        if count < RSS_ENTRIES_MAX:
            rss_xml_all_items += rss_item_xml
            count += 1

    # build rss
    rss_xml = RSS_XML.format(
            lastbuild=datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT"),
            item=rss_xml_all_items)

    rss_path = DEST_DIR + "/rss.xml"
    with open(rss_path, "bw") as f:
        sys.stdout.write("%s.." % (rss_path))
        f.write(rss_xml.encode("utf-8", "replace"))
        sys.stdout.write("written\n")


def write_page(entries_html_for_one_page, fn):
    entry_html = "\n".join(entries_html_for_one_page)

    # body html
    body_html = BODY_HTML.format(content=entry_html)

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
            len(entries_html_for_one_page)))
        f.write(all_html.encode("utf-8", "replace"))
        sys.stdout.write("written\n")


def process(files):
    """
    extract content of files and create corresponding blog
    html
    """

    for fileentry in files:
        with open(fileentry, "rt", encoding="utf-8", errors="replace")  as f:
            content = f.read()

        entry = extract_blog_data(content)
        build_single_page_html(entry)

        # store all blog entries here. this allows us, to
        # add them chronologically in a single page
        d = entry["date"].strftime("%Y%m%d%H%M%S")
        all_entries[d] = entry

    build_all_page_html(all_entries)
    build_all_page_rss(all_entries)

if __name__ == "__main__":
   process(get_files(SOURCE_DIR))
