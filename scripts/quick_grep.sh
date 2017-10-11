urls="\
baike.so.com/doc/1287918-1361771.html \
baike.so.com/doc/1287918-24956577.html \
baike.so.com/doc/1287918-10571130.html \
baike.so.com/doc/2526484-2669235.html \
baike.so.com/doc/6149264-6362453.html \
baike.so.com/doc/3433066-3613205.html \
baike.so.com/doc/6505742-10476925.html \
baike.so.com/doc/6505742-10476751.html \
baike.so.com/doc/6505742-6719462.html \
baike.so.com/doc/6305282-7592385.html \
baike.so.com/doc/6305282-7592390.html \
baike.so.com/doc/6305282-7592392.html \
baike.so.com/doc/6305282-7592397.html \
baike.so.com/doc/8782863-9106966.html \
baike.so.com/doc/4119730-4318978.html \
baike.so.com/doc/7953662-8238058.html \
baike.so.com/doc/6305282-6518809.html \
baike.so.com/doc/7047282-7270188.html \
baike.so.com/doc/6305282-24643457.html \
baike.so.com/doc/9318082-9653967.html \
baike.so.com/doc/9145755-9478904.html \
baike.so.com/doc/8719264-9041748.html \
"
paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result_rel_extraction/baike_summary.json \
result/360/360_entity_info_processed.json \
"
for path in $paths
do
    
    echo ${path}.sample
    rm ${path}.sample

    for url in $urls
    do
        grep ${url} ${path} >> ${path}.sample
    done
done