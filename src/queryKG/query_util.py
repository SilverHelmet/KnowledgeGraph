import urllib2
import urllib
import json

fb_prefix = "http://rdf.freebase.com/ns/"
query_format = ' \
PREFIX fb: <http://rdf.freebase.com/ns/> \
SELECT {ret} \
WHERE \
{{ \
 {query} \
}} \
{opt} \
'
url_format = "http://dlib:3093/sparql?query={query}&format={format}"

def make_query(ret, query, opt = ""):
    global query_format
    query = query_format.format(ret = ret, query = query, opt = opt)
    return query

def call(ret, query, opt = "", format = 'csv'):
    global url_format
    query_str = make_query(ret, query, opt)
    query_str = urllib.quote(query_str)

    url = url_format.format(query = query_str, format = format)
    result = urllib2.urlopen(url).read()
    return result
    
def parse_single_simple_ret(result):
    global fb_prefix
    uris = []
    for idx, line in enumerate(result.split("\n")):
        if idx == 0:
            continue
        line = line.strip().strip('"')
        if line == "":
            continue
        if line.startswith(fb_prefix):
            line = "<" + line + ">"
        uris.append(line)
    return uris


def parse_json_binding(one_result):
    obj_type = one_result['type']
    value = one_result['value'].encode('utf-8')
    if obj_type == 'uri':
        return "<" + value + ">"
    elif obj_type == "literal":
        if "xml:lang" in one_result:
            lang = one_result['xml:lang'].encode('utf-8')
            return value + "@" + lang
        else:
            return value
    else:
        return value
    

def parse_json_ret(result, names):
    ret = []
    obj = json.loads(result)
    results = obj['results']
    bindings = results['bindings']
    for binding in bindings:
        result = {}
        for name in names:
            value = parse_json_binding(binding[name])
            result[name] = value
        ret.append(result)
    return ret


def parse_single_json(result, name):
    ret = parse_json_ret(result, [name])
    ret = [one_ret[name] for one_ret in ret]
    return ret    
        

def get_unique_attr():
    return set([
        "fb:type.property.expected_type",
        "fb:type.property.schema",
        'fb:type.property.unique',
        "fb:type.property.reverse_property",
        'fb:type.property.master_property',
    ])
