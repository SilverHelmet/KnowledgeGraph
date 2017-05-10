from .query_util import call, parse_single_simple_ret, parse_single_json
from ..fb_process.extract_util import encode, get_domain
from ..IOUtil import write_strs
import urllib2
import json

def query_count(query):
    ret = "count(*)"
    result = call(ret, query, format = 'json')
    result = parse_single_json(result, 'callret-0')
    return int(result[0])

def query_all_domains():
    domain_uris = set()
    cnt = 0
    success_domains = {}
    for line in file('result/old_freebase/schema_type.txt', 'r'):
        line = line.strip()
        if line == "":
            continue
        ret = "?domain"
        query = "%s fb:type.type.domain ?domain" %line
        result = call(ret, query)
        uris = parse_single_simple_ret(result)
        
        for uri in uris:
            fb_uri = encode(uri)
            if fb_uri:
                domain = get_domain(line)
                if not domain in success_domains:
                    success_domains[domain] = fb_uri
                else:
                    if success_domains[domain] != fb_uri:
                        print fb_uri
                    assert success_domains[domain] == fb_uri
                domain_uris.add(fb_uri)

    return domain_uris

def query_domain_attrs(in_path, out_path):
    properties = ['fb:type.object.name', 'fb:common.topic.description', "fb:type.domain.types"]
    outf = file(out_path, 'w')
    for line in file(in_path, 'r'):
        domain = line.strip()
        attrs = {}
        for predicate in properties:
            query = '%s %s ?attr' %(domain, predicate)
            ret = "?attr"
            result = call(ret, query, format = 'json')
            result = parse_single_json(result, 'attr')
            result = [encode(x) for x in result]
            if len(result) > 0:
                attrs[predicate] = result
        outf.write(domain + "\t" + json.dumps(attrs) + "\n")
    outf.close()

def query_type_attrs(in_path, out_path):
    properties = ['fb:type.object.name', 'fb:common.topic.description', 
        'fb:freebase.type_hints.included_types', 'fb:type.type.properties',
        'fb:freebase.type_hints.mediator', 'fb:freebase.type_hints.enumeration',]
    outf = file(out_path, 'w')
    for cnt, line in enumerate(file(in_path, 'r')):
        if cnt % 100 == 0:
            print "cnt = %d" %cnt
        type = line.strip()
        ret = "?attr"
        attrs = {}
        
        for predicate in  properties:
            query = '%s %s ?attr' %(type, predicate)
            result = call(ret, query, format = 'json')
            result = parse_single_json(result, 'attr')
            result = [encode(x) for x in result]
            if len(result) > 0:
                attrs[predicate] = result
        
        attrs['count'] = query_count('?s fb:type.object.type %s' %type)
        outf.write(type + "\t" + json.dumps(attrs) + "\n")
    outf.close()

def query_property_attrs(in_path, out_path):
    attr_names = ['fb:type.object.name', 'fb:common.topic.description',
        'fb:type.property.expected_type', 'fb:type.property.schema',
        'fb:type.property.unique', 'fb:type.property.reverse_property', 'fb:type.property.master_property',
        'fb:freebase.property_hints.inverse_description', 'fb:freebase.property_hints.enumeration']
    outf = file(out_path, 'w')
    for cnt, property in enumerate(file(in_path, 'r')):
        domain = get_domain(property)
        if domain in ['fb:type', 'fb:common']:
            continue
        if cnt % 100 == 0:
            print "cnt = %d" %cnt
        ret = "?attr"
        attrs = {}
        property = property.strip()
        for attr_property in  attr_names:
            query = "%s %s ?attr" %(property, attr_property)
            result = call(ret, query, format = 'json')
            result = parse_single_json(result, 'attr')
            result = [encode(x) for x in result]
            if len(result) > 0:
                attrs[attr_property] = result
        
        attrs['count'] = query_count('?s %s ?p' %property)
        outf.write(property + '\t' + json.dumps(attrs) + "\n")
        
    outf.close()
    

    
if __name__ == "__main__":
    
    # query all domains by property fb:type.type.domain
    # domain_uris = query_all_domains()
    # write_strs('result/old_freebase/queried_domain.txt', domain_uris, sorted_flag = True)

    # query attributes of domains
    # in_path = 'result/old_freebase/queried_domain.txt'
    # out_path = 'result/old_freebase/queried_domain_attrs.json'
    # query_domain_attrs(in_path, out_path)

    #query attributes of types
    # in_path = 'result/old_freebase/queried_type.txt'
    # out_path = 'result/old_freebase/queried_type_attrs.json'
    # in_path = 'result/freebase_merged/type.txt'
    # out_path = 'result/freebase_merged/type_attrs.json'
    # query_type_attrs(in_path, out_path)

    #query attributes of properties
    # in_path = 'result/old_freebase/queried_property.txt'
    # out_path = 'result/old_freebase/queried_property_attrs.json'
    in_path = "result/freebase_merged/property.txt"
    out_path = 'result/freebase_merged/property_attrs.json'
    query_property_attrs(in_path, out_path)



    
        
    




