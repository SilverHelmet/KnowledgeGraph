urls="\
baike.so.com/doc/4391556-4598176.html \
baike.so.com/doc/6707957-6921972.html \
baike.so.com/doc/6724155-6938295.html \
baike.so.com/doc/6411356-6625024.html \
baike.so.com/doc/24678290-25575214.html \
baike.so.com/doc/5344366-5579811.html \
baike.so.com/doc/3074939-3240918.html \
baike.so.com/doc/1957541-2071736.html \
baike.so.com/doc/6143842-6357018.html \
baike.so.com/doc/6741534-6956052.html \
baike.so.com/doc/8619623-24185478.html \
ke.so.com/doc/5382393-5618748.html \
baike.so.com/doc/5348516-5583969.html \
baike.so.com/doc/1287918-1361771.html \
baike.so.com/doc/4835393-5052275.html \
baike.so.com/doc/5385244-5621690.html \
baike.so.com/doc/574984-608736.html \
baike.so.com/doc/5329601-5564775.html \
baike.so.com/doc/3433066-3613205.html \
baike.so.com/doc/4972129-5194758.html \
baike.so.com/doc/4972129-5194925.html
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
    rm ${path}.sample

    for url in $urls
    do
        grep -m 1 ${url} ${path} >> ${path}.sample
    done
done