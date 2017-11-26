from .collect_team_suffix import load_team_suffix, try_get_str_suffix
from ..extract_team_extra_name import is_team
from src.extractor.resource import Resource
import os
from src.IOUtil import Print, extra_name_dir
from src.extractor.resource import Resource


class TeamDicts:
    def __init__(self, suffixes):
        self.dicts = {}
        for suf in suffixes:
            self.dicts[suf] = {}

    def add_url(self, bk_url, suffix):
        self.dicts[suffix][bk_url] = []

    def add_name(self, bk_url, name, suffix):
        team_dict = self.dicts[suffix]
        # if not bk_url in team_dict:
        #     team_dict[bk_url] = []
        if not name in team_dict[bk_url]:
            team_dict[bk_url].append(name)

    def save(self, filepath):
        Print("save team dict to [%s]" %filepath)
        outf = file(filepath, 'w')
        for suffix in self.dicts:
            team_dict = self.dicts[suffix]
            for bk_url in team_dict:
                out = "%s\t%s\t%s" %(suffix, bk_url, "\t".join(team_dict[bk_url]))
                outf.write(out.rstrip() + '\n')
        outf.close()

        
class SuffixDicts:
    def __init__(self):
        self.dicts = {}
        self.suffixes = set()
        self.activated_suffixes = set()
        self.url2suffix = {}

    def add_name_with_suffix(self, bk_url, name, suffix):
        self.url2suffix[bk_url] = suffix
        if not suffix in self.dicts:
            self.dicts[suffix] = {}
            self.suffixes.add(suffix)
        team_dict = self.dicts[suffix]
        if not name in team_dict:
            team_dict[name] = []
        team_dict[name].append(bk_url)

    @classmethod 
    def load_from_file(filepath):
        Print('load team\'s dict from [%s]' %filepath)
        team_dicts = SuffixDicts()
        for line in file(filepath):
            p = lien.strip().split('\t')
            suffix = p[0]
            bk_url = p[1]
            names = p[2:]
            for name in names:
                team_dicts.add_name_with_suffix(bk_url, name, suffix)

        return team_dicts

    def refresh(self):
        self.activated_suffixes.clear()

    def search_name(self, name):
        urls = []
        for suffix in self.activated_suffixes:
            suf_dict = self.dicts[suffix]
            urls.extend(suf_dict.get(name, []))
        return urls






        

def gen_team_suffix_dict(suffixes):
    suffixes = set(suffixes)
    outpath = os.path.join(extra_name_dir, 'extra_team_name_dict.tsv')
    resource = Resource.get_singleton()
    baike_info_map = resource.get_baike_info()
    ename_title_map = resource.get_baike_ename_title()
    url2names = resource.get_url2names()

    team_dicts = TeamDicts(suffixes)
    for bk_url in baike_info_map:
        types = baike_info_map[bk_url].types
        if not is_team(types):
            continue

        ori_names = set(url2names[bk_url])

        enames = ename_title_map[bk_url]
        for ename in enames:
            suffix = try_get_str_suffix(ename, suffixes)
            if len(suffix) == 0:
                continue  
            team_dicts.add_url(bk_url, suffix)
            new_name = ename[:len(ename) - len(suffix)]

            if not new_name in ori_names:
                team_dicts.add_name(bk_url, new_name, suffix)

            new_name = new_name + "队"
            if not new_name in ori_names:
                team_dicts.add_name(bk_url, new_name, suffix)
                
    team_dicts.save(outpath)


    


if __name__ == "__main__":
    suffixes = load_team_suffix()
    gen_team_suffix_dict(suffixes)



    