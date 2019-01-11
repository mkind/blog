This little framework is the base for my static
[blog](https://blog.mknd.net).

The blogging script takes json entries and generates html blog entries
as well as an rss xml.

## USAGE

The directory structure is as following:

* **raw:** json files
* **entries:** generated blog entries
* **templates:** contains html and rss template files
* **new.sh:** generates a new raw json file, sets datetime and opens vim editor
* **bloggen.py** takes raw json files and generates static html entries

### Writing A Blog Entries

Blog entries are basically simple json files containing the following.

```json
{
 "author": "mkind",
 "date": "2017-05-28 01:51:12",
 "title": "Hello!",
 "entry": "
Hello World.
"}
```

Each file is positioned in _raw/YYYYmDD-HHMMSS.txt_. Instead of
manually creating those files, you can use the script `new.sh`. It
creates the corresponding file and opens the vim editor.

Note that the title of blog entries is generated automatically by taking
the first `TITLE_LEN` characters of the entry.

### Generating HTML

The second step merges the templates given in _templates/_ and the
raw json files in _raw/_ and builds html blog entries stores in
_entries/_.

To do so, just execute `bloggen.py`. Every blog entry is positioned in
a separate file in _entries/YYYY/m/D/_. There are also an overall html
files like _entries/0.html_, _entries/1.html_, ... which implement
pagination.

The html generation relies on the string replacement of python.

You might need to configure the script by setting variables.

## LICENSE

  GPLv3


