import os
import sys

class Extractor:
    def __init__(self, schema_filepath, inpath, outdir):
        self.out_map = {}
        self.ban_objs = set()
        self.inpath = inpath
        self.init(schema_filepath, os.path.basename(inpath), outdir)

    def init(self, schema_filepath, infile, outdir):
        for line in file(schema_filepath):
            line = line.rstrip()
            if line.startswith("#") or line == "":
                continue
            if line.startswith('+'):
                line = line[1:]
                self.register(line, self.infer_outpath(infile, line, outdir))
            elif line.startswith('-'):
                line = line[1:]
                self.ban(line[1:])

    def infer_outpath(self, infile, predicate, outdir):
        name = predicate[predicate.find(":")+1:]
        out_filepath = os.path.join(outdir, name)
        if not os.path.exists(out_filepath):
            os.makedirs(out_filepath)

        out_filepath = os.path.join(out_filepath, infile)
        return out_filepath

    def decode_uri(self, uri):
        uri = uri.replace("fb:", "http://rdf.freebase.com/ns/")
        uri = uri.replace("rdf:", "http://www.w3.org/2000/01/rdf-schema#")
        return uri

    def register(self, predicate, out_filepath):
        predicate = "<" + self.decode_uri(predicate) + ">"
        self.out_map[predicate] = file(out_filepath, 'w')
    
    def ban(self, obj):
        obj = self.decode_uri(obj)
        print obj
        self.ban_objs.add(obj)

    def extract(self):
        cnt = 0
        ratio = 0
        ban_cnt = 0
        for line in file(self.inpath):
            cnt += 1
            if cnt % 200000 == 0:
                ratio += 1
                print "ratio = %d%% cnt = %d ban_cnt = %d" %(ratio, cnt, ban_cnt) 
            p = line.rstrip().split("\t")
            if p[2] in self.ban_objs:
                ban_cnt += 1
                continue
            out_f = self.out_map.get(p[1], None)
            if out_f:
                out_f.write(line)

    def finish(self):
        for out_f in self.out_map.values():
            out_f.close()
        

if __name__ == "__main__":
    in_filepath = sys.argv[1]
    out_dir = sys.argv[2]
    schema_filepath = "docs/fb_old_schema.txt"
    extractor = Extractor(schema_filepath, in_filepath, out_dir)
    extractor.extract()
    extractor.finish()


