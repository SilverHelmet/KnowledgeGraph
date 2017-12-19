urls=" \
baike.so.com/doc/1731826-1830977.html \
baike.so.com/doc/3611440-3796872.html \
baike.so.com/doc/1187735-1256389.html
"

sample_dir="result/samples"
baike_doc_path="result/rel_extraction/baike_doc.json"
filename=$(basename $baike_doc_path)
for url in $urls
do
    grep -m 1 ${url} ${baike_doc_path} >> ${sample_dir}/${filename}
    
done



