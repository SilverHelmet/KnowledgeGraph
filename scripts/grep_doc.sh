urls=" \
baike.so.com/doc/3056594-3221987.html
"

sample_dir="result/samples"
baike_doc_path="result/rel_extraction/baike_doc.json"
filename=$(basename $baike_doc_path)
for url in $urls
do
    grep -m 1 ${url} ${baike_doc_path} >> ${sample_dir}/${filename}
    
done



