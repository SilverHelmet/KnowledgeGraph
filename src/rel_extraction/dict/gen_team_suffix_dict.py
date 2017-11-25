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

    def add_name(self, bk_url, name, suffix):
        team_dict = self.dicts[suffix]
        if not bk_url in team_dict:
            team_dict[bk_url] = []
        if not name in team_dict[bk_url]:
            team_dict[bk_url].append(name)

    def save(self, filepath):
        Print("save team dict to [%s]" %filepath)
        outf = file(filepath, 'w')
        for suffix in self.dicts:
            team_dict = self.dicts[suffix]
            for bk_url in team_dict:
                outf.write("%s\t%s\t%s\n" %(suffix, bk_url, "\t".join(team_dict[bk_url])))
        outf.close()

        

def gen_team_suffix_dict(suffixes):
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



    