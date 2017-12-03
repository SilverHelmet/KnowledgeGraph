#encoding: utf-8
import sys
from .parse import parse_text, strip_url
from ..IOUtil import Print, nb_lines_of
import json
from tqdm import tqdm

end_puncs = set([u'。', u'？',u'?', u'!', u'！', u';', u'；'])
def split_sentences(text, max_length = 150):
    global end_puncs
    lines = []
    st = 0
    pos = 0
    ed = len(text)
    while pos < ed:
        if text[pos] in end_puncs or pos - st >= max_length:
            lines.append((text[st:pos+1]))
            st = pos+1
        pos += 1
    if st < ed:
        lines.append(text[st:])
    return lines

def work(inpath, docuemnt_out_path):
    Print('process page information')
    doc_outf = file(docuemnt_out_path, 'w')
    for line in tqdm(file(inpath), total = nb_lines_of(inpath)):
        p = line.strip().split('\t')
        url = strip_url(p[0])
        b64content = p[1]
        texts = parse_text(url, b64content, ignore_table = True)
        sentences = []
        obj = {
            'url': url,
            'chapters': texts
        }
        # for _, text in texts:
        #     for paragraph in text:
        #         sentences.extend(split_sentences(paragraph))
        # obj = {
        #     'url': url,
        #     'sentences': sentences,
        # }

        doc_outf.write("%s\n" %(json.dumps(obj, ensure_ascii=False)))

        for sentence in sentences:
            sentence_outf.write(sentence + '\n')    
    doc_outf.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "need inpath page_document_out_path"
    else:
        inpath = sys.argv[1]
        document_out_path = sys.argv[2]
        work(inpath, document_out_path)

