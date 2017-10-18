urls="\
baike.so.com/doc/6305282-24835378.html \
baike.so.com/doc/9490464-9833465.html \
baike.so.com/doc/8519496-8839967.html \
baike.so.com/doc/6305282-7592386.html \
baike.so.com/doc/6305282-7592387.html \
baike.so.com/doc/6305282-7592388.html \
baike.so.com/doc/6305282-7592389.html \
baike.so.com/doc/6305282-7592391.html \
baike.so.com/doc/6305282-7592393.html \
baike.so.com/doc/6305282-7592394.html \
baike.so.com/doc/6305282-7592395.html \
baike.so.com/doc/6305282-7592396.html \
baike.so.com/doc/6305282-7592398.html \
baike.so.com/doc/6305282-7592399.html \
baike.so.com/doc/6305282-8926666.html \
baike.so.com/doc/9099646-9431854.html \
baike.so.com/doc/7953660-8238056.html \
baike.so.com/doc/7017186-7240075.html \
baike.so.com/doc/6305282-24642639.html \
baike.so.com/doc/6305282-24643495.html \
baike.so.com/doc/9523019-9867145.html \
baike.so.com/doc/6305282-24922778.html \
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
baike.so.com/doc/6505742-10476751.html \
baike.so.com/doc/6505742-10476925.html \
baike.so.com/doc/6505742-6719462.html
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