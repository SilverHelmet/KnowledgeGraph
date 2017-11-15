urls="\
baike.so.com/doc/6707957-6921972.html \
baike.so.com/doc/5382393-5618748.html \
baike.so.com/doc/1287918-1361771.html \
baike.so.com/doc/4835393-5052275.html \
baike.so.com/doc/5385244-5621690.html \
baike.so.com/doc/1957541-2071736.html \
baike.so.com/doc/5344366-5579811.html \
baike.so.com/doc/574984-608736.html \
baike.so.com/doc/5329601-5564775.html \
baike.so.com/doc/3433066-3613205.html 
"
paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result/rel_extraction/baike_summary.json \
result/360/360_entity_info_processed.json \
"
for path in $paths
do
    
    echo ${path}.sample
    # rm ${path}.sample

    for url in $urls
    do
        grep -m 1 ${url} ${path} >> ${path}.sample
    done
done