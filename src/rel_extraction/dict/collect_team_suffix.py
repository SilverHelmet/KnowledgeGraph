from src.extractor.util import get_domain
from src.extractor.resource import Resource
from src.IOUtil import dict_dir, rel_ext_dir, Print, load_file
import os
from tqdm import tqdm
import re 

org_types = ['fb:sports.sports_team']
def is_org(e_types):
    global org_types
    for org_type in org_types:
        if org_type in e_types:
            return True
    return False

def collect_team_suffix(suffix_out_path):
    Print("collect team suffix, write to [%s]" %suffix_out_path)

    ename_title_map = Resource.get_singleton().get_baike_ename_title()
    baike_info_map = Resource.get_singleton().get_baike_info()
    ltp = Resource.get_singleton().get_ltp()
    suffix_cnt = {}

    Print("collect suffix")
    for bk_url in tqdm(baike_info_map, total = len(baike_info_map)):
        e_types = baike_info_map[bk_url].types
        if not is_org(e_types):
            continue
        enames = ename_title_map[bk_url]

        for name in enames:
            words = ltp.cut(name)
            ed = len(words)
            for st in range(1, ed):
                suffix = "".join(words[st:])
                if not suffix in suffix_cnt:
                    suffix_cnt[suffix] = 0
                suffix_cnt[suffix] += 1
        
    threshold = 10
    outf = file(suffix_out_path, 'w')
    for key in sorted(suffix_cnt, key = lambda x: suffix_cnt[x], reverse = True):
        cnt = suffix_cnt[key]
        if cnt < threshold:
            continue
        outf.write("%s\t%d\n" %(key, cnt))
    outf.close()

re_eng_digit = re.compile(r'[0-9a-zA-Z]')
def has_eng_digit(name):
    global re_eng_digit
    return re_eng_digit.search(name) is not None

def load_team_suffix():
    inpath = os.path.join(dict_dir, 'team_suffix_cnt.tsv')
    error_suffix_path = os.path.join(dict_dir, 'team_error_suffix.txt')
    suffixes = set()
    for line in file(inpath):
        suffixes.add(line.split('\t')[0])
    error_suf = set(load_file(error_suffix_path))
    good_suf = set([suf for suf in suffixes if not suf in error_suf])
    return good_suf
        
    


if __name__ == "__main__":
    suffix_out_path = os.path.join(dict_dir, 'team_suffix_cnt.tsv')
    # summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary.json')

    # collect_team_suffix(suffix_out_path)
    load_team_suffix()
