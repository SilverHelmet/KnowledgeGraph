urls = " \
baike.so.com/doc/6707957-6921972.html \
baike.so.com/doc/5382393-5618748.html \
baike.so.com/doc/5348516-5583969.html \
baike.so.com/doc/1287918-1361771.html \
baike.so.com/doc/4835393-5052275.html \
baike.so.com/doc/5385244-5621690.html \
baike.so.com/doc/1957541-2071736.html \
baike.so.com/doc/5344366-5579811.html \
baike.so.com/doc/574984-608736.html \
baike.so.com/doc/5329601-5564775.html \
baike.so.com/doc/3433066-3613205.html
"

sample_dir="result/samples"
baike_doc_path="result/rel_extraction/baike_doc.json"
filename=$(basename $baike_doc_path)
for url in $urls
do
    grep -m 1 ${url} ${path} >> ${sample_dir}/${filename}
    
done



