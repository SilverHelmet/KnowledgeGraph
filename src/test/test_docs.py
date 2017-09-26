from ..IOUtil import rel_ext_dir
import os
import json
def del_space(text):
    return text.replace(u'\xa0', '').replace(u'\u200b', '')

if __name__ == "__main__":
    baike_url = 'baike.so.com/doc/4786705-5002701.html'
    for line in file(os.path.join(rel_ext_dir, 'baike_doc.json')):
        p = line.split("\t")
        if p[0] != baike_url:
            continue
        for title, content in json.loads(p[1]):
            print title, del_space(content)