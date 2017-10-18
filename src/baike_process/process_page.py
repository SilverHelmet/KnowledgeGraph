import sys
from .parse import parse_text, strip_url
from ..IOUtil import Print
import json

def work(inpath, sentence_out_path, docuemnt_out_path):
    Print('process page information')
    doc_outf = file(docuemnt_out_path, 'w')
    sentence_outf = file(sentence_out_path, 'w')
    for line in file(inpath):
        p = line.strip().split('\t')
        url = strip_url(p[0])
        b64content = p[1]
        texts = parse_text(url, b64content)
        obj = {
            'url': url,
            'texts': texts,
        }

        doc_outf.write(json.dumps(obj, ensure_ascii=False))
        doc_outf.write('\n')

        for title, sentences in texts:
            for sentence in sentences:
                sentence_outf.write(sentence + '\n')    
    doc_outf.close()
    sentence_outf.close()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "need inpath sentence_out_path page_document_out_path"
    else:
        inpath = sys.argv[1]
        sentence_out_path = sys.argv[2]
        document_out_path = sys.argv[3]
        work(inpath, sentence_out_path, document_out_path)

