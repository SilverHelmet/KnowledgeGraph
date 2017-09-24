from ..IOUtil import rel_ext_dir, Print 

def load_mappings(filepath = None):
    if filepath is None:
        filepath = os.path.join(rel_ext_dir, 'mapping_result.tsv')
    Print('load mappings from [%s]' %filepath)
    bk2fb = {}
    for line in file(filepath):
        bk_url, fb_uri = line.strip().decode('utf-8'). split('\t')
        bk2fb[bk_url] = fb_uri
    return bk2fb


