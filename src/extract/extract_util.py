
def get_domain(uri):
    fb_uri = encode(uri)
    if fb_uri is None:
        return None
    if fb_uri.startswith('fb:'):
        p = fb_uri.split('.')
        return p[0]
    else:
        raise Exception("error uri")

def get_type(uri):
    fb_uri = encode(uri)
    if fb_uri is None:
        return None

    if fb_uri.startswith('fb:'):
        p = fb_uri.split('.')
        return '.'.join(p[:2])
    else:
        raise Exception("error uri")

def encode(uri):
    
    if uri.startswith("<"):
        # uri
        if uri.startswith("<http://rdf.freebase.com/ns/") and uri.endswith('>'):
            uri = "fb:" + uri[len('<http://rdf.freebase.com/ns/'):-1]
            return uri
        else:
            return None
    elif uri.startswith('fb:'):
        # fb:xxx
        return uri
    else:
        # literal
        return uri
        


