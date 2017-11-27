urls=" \
baike.so.com/doc/1287918-1361771.html \
baike.so.com/doc/2526484-2669235.html \
baike.so.com/doc/5382393-5618748.html \
baike.so.com/doc/4835393-5052275.html \
baike.so.com/doc/6662392-6876216.html
"

sample_dir="result/samples"
baike_doc_path="result/rel_extraction/baike_doc.json"
filename=$(basename $baike_doc_path)
for url in $urls
do
    grep -m 1 ${url} ${baike_doc_path} >> ${sample_dir}/${filename}
    
done



