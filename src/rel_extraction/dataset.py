#encoding:utf-8
from ..IOUtil import result_dir, rel_ext_dir, classify_dir, Print, cache_dir
from .util import load_mappings
from ..mapping.fb_date import FBDatetime
import os
from tqdm import tqdm
import json

class DatasetFinder:
    def __init__(self, load = True):
        if load:
            self.name2fb_map = self.load_name2fb()
            fb_uris = set()
            for key in self.name2fb_map:
                fb_uris.update(self.name2fb_map[key])
            self.fb_ttls_map = self.load_fb_ttls(fb_uris)

    
    def load_name2bk(self, bk_urls):
        name2baike_path = os.path.join(rel_ext_dir, 'baike_names.tsv')
        name2bk_map = {}
        Print("gen name2baike map from [%s] with #bk_urls is %d" %(name2baike_path, len(bk_urls)) )
        hit = 0
        for line in tqdm(file(name2baike_path), total = 21710208):
            p = line.strip().decode('utf-8').split('\t')
            bk_url = p[0]
            
            if not bk_url in bk_urls:
                continue
            hit += 1

            for idx in range(1, len(p)):
                name = p[idx]
                if not name in name2bk_map:
                    name2bk_map[name] = []
                name2bk_map[name].append(bk_url)
        Print("name2baike size = %d, #hit = %d" %(len(name2bk_map), hit) )
        return name2bk_map

    def load_name2fb(self):
        Print("generate name -> freebase")
        bk2fb = load_mappings()
        bk_urls = set(bk2fb.keys())
        name2bk_map = self.load_name2bk(bk_urls)
        name2fb_map = {}
        for name in name2bk_map:
            fbs = [bk2fb[bk_url] for bk_url in name2bk_map[name]]
            fbs = list(set(fbs))
            name2fb_map[name] = fbs
        return name2fb_map

    def load_fb_ttls(self, fb_uris):
        filepath = os.path.join(classify_dir, 'mapped_fb_entity_info.json')
        Print('load fb ttls from [%s]' %filepath)

        fb_ttls_map = {}
        for line in tqdm(file(filepath), total = 6282988):
            p = line.split('\t')
            fb_uri = p[0].decode('utf-8')
            if fb_uri not in fb_uris:
                continue
            ttls = json.loads(p[1])
            entity_ttls = []
            time_ttls = []
            for prop, value in ttls:
                if value.startswith('fb:m'):
                    entity_ttls.append((prop, value))
                else:
                    time_obj = FBDatetime.parse_fb_datetime(value)
                    if time_obj:
                        time_ttls.append((prop, value))
            fb_ttls_map[fb_uri] = (entity_ttls, time_ttls)
        return fb_ttls_map 

    def save(self, name2fb_path, fb_ttls_path):
        outf = file(name2fb_path, 'w')
        json.dump(self.name2fb_map, outf)
        outf.close()

        outf = file(fb_ttls_path, 'w')
        json.dump(self.fb_ttls_map, outf)
        outf.close()

    @staticmethod
    def load_from_cache(name2fb_path, fb_ttls_path):
        obj = DatasetFinder(load = False)
        Print("load DatasetFinder from cache")
        inf = file(name2fb_path)
        obj.name2fb_map = json.load(inf)
        inf.close()

        inf = file(fb_ttls_path)
        obj.fb_ttls_map = json.load(inf)
        inf.close()
        Print("load finished")
        return obj


if __name__ == "__main__":
    # finder = DatasetFinder()
    # fb_uris = finder.name2fb_map[u'刘德华']
    # print fb_uris
    # for fb_uri in fb_uris:
    #     print fb_uri, finder.fb_ttls_map[fb_uri]

    name2fb_path = os.path.join(cache_dir, 'DatasetFinder.name2fb.cache')
    fb_ttls_path = os.path.join(cache_dir, 'DatasetFinder.fb_ttls.cache')
    # finder.save(name2fb_path, fb_ttls_path)

    finder = DatasetFinder.load_from_cache(name2fb_path, fb_ttls_path)
    fb_uris = finder.name2fb_map[u'刘德华']
    print fb_uris

                


        

        



