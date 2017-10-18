#encoding: utf-8
import sys
from .parse import parse_text, strip_url
from ..IOUtil import Print
import json

end_puncs = set([u'。', u'？',u'?', u'!', u'！', u';', u'；'])
def split_sentences(text):
    global end_puncs
    lines = []
    st = 0
    pos = 0
    ed = len(text)
    while pos < ed:
        if text[pos] in end_puncs or pos - st >= 150:
            lines.append((text[st:pos+1]))
            st = pos+1
        pos += 1
    if st < ed:
        lines.append(text[st:])
    return lines

def work(inpath, sentence_out_path, docuemnt_out_path):
    Print('process page information')
    doc_outf = file(docuemnt_out_path, 'w')
    sentence_outf = file(sentence_out_path, 'w')
    for line in file(inpath):
        p = line.strip().split('\t')
        url = strip_url(p[0])
        b64content = p[1]
        texts = parse_text(url, b64content)
        sentences = []
        for _, text in texts:
            for paragraph in text:
                sentences.extend(split_sentences(paragraph))
        obj = {
            'url': url,
            'sentences': sentences,
        }

        doc_outf.write(json.dumps(obj, ensure_ascii=False))
        doc_outf.write('\n')

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

