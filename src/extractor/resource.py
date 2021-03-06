#encoding: utf-8
from src.IOUtil import *
from ltp import LTP
from src.schema.schema import Schema
import os
import json
from tqdm import tqdm
from src.mapping.fb_date import FBDatetime
from src.mapping.one2one_mapping_cnt import load_baike_name_attrs


class Resource:
    singleton = None
    def __init__(self):
        self.dict = {}

    def get_important_domains(self):
        if not 'important_domains' in self.dict:
            self.dict['important_domains'] = load_important_domains()
        return self.dict['important_domains']

    def get_ltp(self):
        if not 'ltp' in self.dict:
            self.dict['ltp'] = LTP(None)
        return self.dict['ltp']

    def get_schema(self):
        if not 'schema' in self.dict:
            schema = Schema()
            schema.init(init_type_neighbor = True)
            self.dict['schema'] = schema
        return self.dict['schema']

    def get_baike_info(self):
        if not 'baike_info' in self.dict:
            path = os.path.join(rel_ext_dir, 'baike_static_info.tsv')
            extra_type_paths = [os.path.join(extra_type_dir, 'extra_type.tsv')]
            self.dict['baike_info'] = load_bk_static_info(path, extra_type_paths)
        return self.dict['baike_info']

    def load_baike_names(self, lowercase):
        path = os.path.join(rel_ext_dir, 'baike_names.tsv')
        extra_path = os.path.join(extra_name_dir, 'summary_extra_name.tsv')
        extra_bracket_path = os.path.join(extra_name_dir, 'summary_extra_bracket_name.tsv')
        extra_team_path = os.path.join(extra_name_dir, 'extra_team_name.tsv')
        
        name2bk, url2names = load_baike_names_resource([path, extra_path, extra_bracket_path, extra_team_path])

        self.dict['name2bk'] = name2bk
        self.dict['url2names'] = url2names

        if lowercase:
            lower_name2bk = gen_lowercase_name(name2bk)
            self.dict['lower_name2bk'] = lower_name2bk

    def get_name2bk(self, lowercase = False):
        if not 'name2bk' in self.dict:
            self.load_baike_names(lowercase)
        return self.dict['name2bk']

    def get_url2names(self, lowercase = False):
        if not 'url2names' in self.dict:
            self.load_baike_names(lowercase)
        return self.dict['url2names']

    def get_lower_name2bk(self):
        if not 'lower_name2bk' in self.dict:
            self.load_baike_names(lowercase = True)
        return self.dict['lower_name2bk']

    def get_summary_with_infobox(self):
        if not 'baike_summary_with_infobox' in self.dict:
            summary_path = os.path.join(rel_ext_dir, 'baike_filtered_summary_with_infobox.json')
            # infobox_path = os.path.join(result_dir, '360/360_entity_info_processed.json')
            self.dict['baike_summary_with_infobox'] = load_summary(summary_path)
        return self.dict['baike_summary_with_infobox']

    def get_predicate_map(self):
        if not "predicate_map" in self.dict:
            main_filepath = os.path.join(result_dir, '360/mapping/final_predicates_map.json')
            # dataset_path = os.path.join(dataset_dir, 'summary_dataset.tsv.v1.predicate_map.json')
            dataset_path = os.path.join(dataset_dir, 'doc_dataset.tsv.predicate_map.json')
            extra_path = os.path.join(doc_dir, 'human_add_predicate_map.json')
            
            self.dict['predicate_map'] = load_predicate_map([main_filepath, dataset_path], extra_path)
        return self.dict['predicate_map']

    def get_vertical_domain_baike_dict(self):
        if not "vt_domain_bk_dict" in self.dict:
            path = os.path.join(dict_dir, 'vertical_domain_baike_dict.txt')
            Print("load name dict from [%s]" %path)
            self.dict['vt_domain_bk_dict'] = set(load_file(path))
        return self.dict['vt_domain_bk_dict']

    def get_baike_ename_title(self):
        if not "baike_ename_title" in self.dict:
            self.dict['baike_ename_title'] = load_url2names(os.path.join(rel_ext_dir, 'baike_ename_title.tsv'))
        return self.dict['baike_ename_title']

    def get_location_dict(self):
        if not 'location_dict' in self.dict:
            dicts = ['province.txt', 'citytown.txt', 'nationality.txt']
            dicts_path = [os.path.join(dict_dir, x) for x in dicts]
            Print('load location dict from [%s]' %" ".join(dicts))
            self.dict['location_dict'] = load_dict(dicts_path)
        return self.dict['location_dict']

    def get_team_suffix_dict(self):
        if not "team_suffix_dict" in self.dict:
            self.dict['team_suffix_dict'] = load_extra_team_suffix_dict()
        return self.dict['team_suffix_dict']

    def get_half_named_fb_info(self):
        if not 'half_named_fb_info' in  self.dict:
            path = os.path.join(rel_ext_dir, 'mapped_fb_entity_info_processed.json')
            self.dict['half_named_fb_info'] = load_half_named_fb_info(path)
        return self.dict['half_named_fb_info']

    def get_table_parser(self, entity_linker, ner):
        if not 'table_parser' in self.dict:
            from src.extractor.table.table_rule_parser import TableParser
            table_parser = TableParser(entity_linker, ner)
            table_parser.init(None)
            table_parser.load_extra_table(None)
            table_parser.finish_load()
            self.dict['table_parser'] = table_parser
        return self.dict['table_parser']

    def get_title2url(self):
        if not "title2url" in self.dict:
            filepaths = [ os.path.join(dict_dir, 'nationality_url.txt'), os.path.join(dict_dir, 'full_profession_url.txt')]
            title2url = load_title2url(filepaths)
            self.dict['title2url'] = title2url
        return self.dict['title2url']

        

    @staticmethod
    def get_singleton():
        if Resource.singleton is None:
            Resource.singleton = Resource()
        return Resource.singleton

def load_name2baike(filepath = None):
    if filepath is None:
        filepath = os.path.join(rel_ext_dir, 'baike_names.tsv')
    total = nb_lines_of(filepath)
    name2bk = {}
    Print('load name -> baike from %s' %filepath)
    for line in tqdm(file(filepath), total = total):
        # p = line.strip().decode('utf-8').split('\t')
        p = line.strip().split('\t')
        bk_url = p[0]
        names = p[1:]
        for name in names:
            name = name.strip()
            if not name in name2bk:
                name2bk[name] = []
            name2bk[name].append(bk_url)
    return name2bk

def gen_lowercase_name(name2bk):
    lower_name2bk = {}
    for name in name2bk:
        if name.lower() != name:
            lower_name2bk[name.lower()] = name2bk[name]
    return lower_name2bk

def load_url2names(filepath):
    total = nb_lines_of(filepath)

    Print('load url -> names from [%s]' %filepath)

    url2names = {}
    for line in tqdm(file(filepath), total = total):
        p = line.strip().split('\t')
        bk_url = p[0]
        names = p[1:]
        url2names[bk_url] = p[1:]
    return url2names

def load_baike_names_resource(filepaths):
    url2names = {}
    name2bk = {}
    for filepath in filepaths:
        if not os.path.exists(filepath):
            assert False
            continue
        Print('generate url2names & name2baike from baike name file [%s]' %filepath)
        total = nb_lines_of(filepath)
        for line in tqdm(file(filepath, 'r'), total = total):
            p = line.strip().split('\t')
            bk_url = p[0]
            names = p[1:]
            if bk_url in url2names:
                url2names[bk_url].extend(names)
            else:
                url2names[bk_url] = names
            for name in names:
                if not name in name2bk:
                    name2bk[name] = []
                name2bk[name].append(bk_url)
    
    return name2bk, url2names

def load_important_domains():
    domains = set()
    for line in file(os.path.join(doc_dir, 'important_domains.txt')):
        line = line.strip()
        if line.startswith("#"):
            continue
        domains.add(line)
    return domains

def load_bk_static_info(filepath, extra_type_paths):
    total = nb_lines_of(filepath)
    info_map = {}
    Print("load baike static info from [%s]" %filepath)
    for line in tqdm(file(filepath), total = nb_lines_of(filepath)):
        p = line.strip().split('\t')
        bk_url = p[0]
        pop = int(p[2])
        if p[1] != "None":
            pop = pop + 5
        types = json.loads(p[3])
        info = BaikeInfo(pop, types, p[1])
        info_map[bk_url] = info

    for path in extra_type_paths:
        if not os.path.exists(path):
            assert False
            continue
        Print('load extra type from [%s]' %(path))
        for line in file(path):
            p = line.strip().split('\t')
            bk_url = p[0]
            types = p[1:]
            if not bk_url in info_map:
                continue
            info_map[bk_url].types.extend(types)

    return info_map

def set_prop(probs, fb_props, setted_prop):
    for prop in fb_props:
        probs[prop] = setted_prop

def adjust_predicate_map(predicate_map, k = 25):
    prop_predicate_scores = {}
    for predicate in predicate_map:
        prop_probs = predicate_map[predicate]
        for prop in prop_probs:
            prob = prop_probs[prop]
            if not prop in prop_predicate_scores:
                prop_predicate_scores[prop] = {}
            predicate_scores = prop_predicate_scores[prop]
            predicate_scores[predicate] = prob
    
    bad_mappings = {}
    for prop in prop_predicate_scores:
        predicate_scores = prop_predicate_scores[prop]
        predicates = sorted(predicate_scores.keys(), key = lambda x: predicate_scores[x][0], reverse = True)
        topk = k
        # if prop in ['fb:people.person.parents', 'fb:music.album.release_date',
        #      'fb:education.educational_institution.nickname', 'fb:film.producer.film', 
        #      'fb:organization.organization.founders', 'fb:organization.organization_founder.organizations_founded', 'fb:music.artist.track']:
        #     print prop
        #     Print(predicates)
        #     Print(predicates[:topk])
        good_verbs = set()
        for predicate in predicates[:topk]:
            good_verbs.add(predicate)
        for predicate in predicates[topk:]:
            if predicate.split("#")[0] in good_verbs:
                continue
            if not predicate in bad_mappings:
                bad_mappings[predicate] = []
            bad_mappings[predicate].append(prop)


    for predicate in predicate_map:
        bad_props = bad_mappings.get(predicate, [])
        prop_probs = predicate_map[predicate]
        for bad_prop in bad_props:
            prop_probs.pop(bad_prop)
            # Print("delete bad mapping %s -> %s" %(predicate, bad_prop))

    bad_predicates = set(load_baike_name_attrs())
    for predicate in bad_predicates:
        predicate = predicate.encode('utf-8')
        if predicate in predicate_map:
            predicate_map.pop(predicate)
            

def load_predicate_map(filepaths, extra_path = None):
    elimination_props = set(['fb:people.person.profession', 'fb:people.person.nationality', 'fb:music.artist.origin'])
    predicate_map  = {}
    for filepath in filepaths:
        if not os.path.exists(filepath):
            assert False
            continue
        Print('load predicate map from %s' %filepath)
        for line in file(filepath):
            p = line.split('\t')
            infobox_pred = p[0]
            mappings = json.loads(p[1])[:10]
            if not infobox_pred in predicate_map:
                predicate_map[infobox_pred] = {}
            probs = predicate_map[infobox_pred]
            total = None
            for prop, occur in mappings:
                if prop in elimination_props:
                    continue
                if not prop in probs:
                    probs[prop] = (0, 0)
                cnt, total = map(int, occur.split('/'))
                pre_cnt, pre_total = probs[prop]
                probs[prop] = (pre_cnt + cnt, pre_total)
            if total:
                for prop in probs:
                    cnt, pre_total = probs[prop]
                    probs[prop] = (cnt, pre_total + total)
            predicate_map[infobox_pred] = probs

    adjust_predicate_map(predicate_map)

    for infobox_pred in predicate_map:
        prop_probs = predicate_map[infobox_pred]
        error_prop = set()
        for fb_prop in prop_probs:
            cnt, total = prop_probs[fb_prop]
            if cnt >= 20 or cnt / (total + 0.0) >= 0.03:
                prop_probs[fb_prop] = cnt / (total + 3.0)
            else:
                error_prop.add(fb_prop)
        for prop in error_prop:
            prop_probs.pop(prop)


    if extra_path is not None:
        Print("load extra rule from [%s]" %extra_path)
        for line in file(extra_path):
            line = line.strip()
            if line == "":
                continue
            if line.startswith("#"):
                continue
            p = line.split('\t')

            infobox_pred = p[0]
            fb_props = json.loads(p[1])
            if len(p) == 2:
                setted_prop = 1
            else:
                setted_prop = float(p[2])
            if not "#" in infobox_pred:
                if not infobox_pred in predicate_map:
                    predicate_map[infobox_pred] = {}
                

                for predicate in predicate_map:
                    if predicate.split("#")[0] == infobox_pred:
                        # print 'add predicate %s -> %s, props %s' %(infobox_pred, predicate, fb_props)
                        set_prop(predicate_map[predicate], fb_props, setted_prop)
            else:
                env = infobox_pred.split("#")[1]
                for predicate in predicate_map:
                    if "#" in predicate and predicate.split("#")[1] == env:
                        # print 'add predicate %s -> %s, props %s' %(env, predicate, fb_props)
                        set_prop(predicate_map[predicate], fb_props, setted_prop)    

    # adjust time score
    schema = Resource.get_singleton().get_schema()
    for predicate in predicate_map:
        prop_probs = predicate_map[predicate]
        error_props = set()
        for prop in prop_probs:
            if schema.expected_type(prop) == 'fb:type.datetime' and prop_probs[prop] < 0.2:
                error_props.add(prop)
        for prop in error_props:
            prop_probs.pop(prop)
                  
    return predicate_map

def load_dict(dicts_path):
    dict_names = set()
    for dict_path in dicts_path:
        for line in file(dict_path):
            name = line.rstrip('\n')
            dict_names.add(name)
    return dict_names
        
def load_summary(summary_path):
    Print("load summary from [%s]" %summary_path)
    summary_map = {}
    for line in tqdm(file(summary_path), total = nb_lines_of(summary_path)):
        bk_url, summary = line.split('\t')
        summary = json.loads(summary)['summary'].encode('utf-8')
        summary_map[bk_url] = summary
    return summary_map

def load_extra_team_suffix_dict():
    team_suffix_dict_path = os.path.join(extra_name_dir, 'extra_team_name_dict.tsv')
    team_suffix_dicts = SuffixDicts.load_from_file(team_suffix_dict_path)
    return team_suffix_dicts


class BaikeInfo:
    def __init__(self, pop, types, fb_uri):
        self.pop = pop
        self.types = types
        self.fb_uri = fb_uri

class SuffixDicts:
    def __init__(self):
        self.dicts = {}
        self.suffixes = set()
        self.activated_suffixes = set()
        self.url2suffix = {}

    def add_url_with_suffix(self, bk_url, suffix):
        self.url2suffix[bk_url] = suffix

    def add_name_with_suffix(self, bk_url, name, suffix):
        if not suffix in self.dicts:
            self.dicts[suffix] = {}
            self.suffixes.add(suffix)
        team_dict = self.dicts[suffix]
        if not name in team_dict:
            team_dict[name] = []
        team_dict[name].append(bk_url)

    def search_name(self, name):
        urls = []
        for suffix in self.activated_suffixes:
            suf_dict = self.dicts[suffix]
            urls.extend(suf_dict.get(name, []))
        return urls

    def meet_url(self, bk_url):
        if bk_url in self.url2suffix:
            suffix = self.url2suffix[bk_url]
            # print 'add suffix', suffix, bk_url
            self.activated_suffixes.add(suffix)

    def refresh(self):
        self.activated_suffixes.clear()

    @staticmethod
    def load_from_file(filepath):
        Print('load team\'s dict from [%s]' %filepath)
        suf_dicts = SuffixDicts()
        for line in file(filepath):
            p = line.strip().split('\t')
            suffix = p[0]
            bk_url = p[1]
            suf_dicts.add_url_with_suffix(bk_url, suffix)
            names = p[2:]
            for name in names:
                suf_dicts.add_name_with_suffix(bk_url, name, suffix)
        return suf_dicts

def process_fb_date_values(values):
    fb_date_values = []
    for value in values:
        fb_date = FBDatetime.parse_fb_datetime(value)
        if fb_date:
            fb_date_values.append(fb_date.date_str().decode('utf-8'))
    return fb_date_values



def load_half_named_fb_info(path):
    Print('load half naemd fb info from [%s]' %os.path.basename(path))
    datetime_props = Resource.get_singleton().get_schema().get_datetime_properties()
    fb_info = {}
    for line in tqdm(file(path), total = nb_lines_of(path)):
        fb_uri, rels = line.split('\t')
        rels = json.loads(rels)
        total_names = set()
        for prop in rels:
            values = rels[prop]
            if prop in datetime_props:
                values = process_fb_date_values(values)
                rels[prop] = values
            total_names.update(values)
            
            if len(values) > 20:
                rels[prop] = set(values)
        rels['total'] = total_names
        fb_info[fb_uri] = rels
        
    return fb_info

def load_title2url(filepaths):
    title2url = {}
    for filepath in filepaths:
        for line in file(filepath):
            title, url = line.strip().split('\t')
            if title in title2url:
                # Print('error title %s' %title)
                continue            
            title2url[title] = url
    return title2url


if __name__ == "__main__":
    s1 = Resource.get_singleton()
    s2 = Resource.get_singleton()
    s1.get_predicate_map()



