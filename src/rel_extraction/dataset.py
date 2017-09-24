from ..IOUtil import result_dir, rel_ext_dir
from .util import load_mappings()
import os
from tqdm import tqdm

class Dataset:
    def __init__(self, bk_urls = None):
        self.name2fb_map = self.load_name2fb()
        fb_uris = set()
        for key in self.name2fb_map:
            fb_uris.update(self.name2fb_map[key])
        self.fb_ttls_map = self.load_fb_ttls(fb_uris)

    
    def load_name2bk(self, bk_urls):
        name2baike_path = os.path.join(rel_ext_dir, 'baike_names.tsv')
        name2bk_map = {}
        Print("gen name2baike map from [%s]" %name2baike_path)
        for line in tqdm(file(filepath), total = 21710208):
            p = line.strip().decode('utf-8').split('\t')
            bk_url = p[0]
            if bk_urls is not None and not bk_url in bk_urls:
                continue
            for idx in range(1, len(p)):
                name = p[idx]
                if not name in name2bk_map:
                    name2bk_map[name] = {}
                name2bk_map[name].append(bk_url)
        return name2bk_map

    def load_name2fb(self):
        Print("generate name -> freebase")
        bk2fb = load_mappings()
        bk_urls = set(bk2fb.keys())
        name2bk_map = self.load_name2bk(self, bk_urls)
        name2fb_map = {}
        for name in name2bk_map:
            fbs = [bk2fb[bk_url] for bk_url in name2bk_map[name]]
            fbs = list(set(fbs))
            name2fb_map[name] = fbs
        return name2fb_map

    def load_fb_ttls(self, fb_uris):
        
                


        

        



