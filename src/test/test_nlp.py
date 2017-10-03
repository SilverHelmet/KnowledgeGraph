#encoding: utf-8
from nltk.tokenize.stanford_segmenter import StanfordSegmenter
from ..IOUtil import Print
import os

base_dir = 'lib/stanfordNLTK'
segmenter = StanfordSegmenter(
    path_to_jar = os.path.join(base_dir, 'stanford-segmenter.jar'),
    path_to_slf4j = os.path.join(base_dir, 'slf4j-api.jar'),
    path_to_sihan_corpora_dict = os.path.join(base_dir, 'data'),
    path_to_model = os.path.join(base_dir, 'data/pku.gz'),
    path_to_dict = os.path.join(base_dir, 'data/dict-chris6.ser.gz')
)

res = segmenter.segment(u"刘德华是一个演员")
Print(res)
res = segmenter.segment(u"刘德华是一个演员")
Print(res)
res = segmenter.segment(u"刘德华是一个演员")
Print(res)
res = segmenter.segment(u"刘德华是一个演员")
Print(res)
res = segmenter.segment(u"刘德华是一个演员")
Print(res)
res = segmenter.segment(u"刘德华是一个演员")
Print(res)
