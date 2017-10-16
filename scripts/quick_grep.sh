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
baike.so.com/doc/9237659-9570996.html \
baike.so.com/doc/23961448-24530363.html \
baike.so.com/doc/8972750-9301011.html \
baike.so.com/doc/9142666-9475814.html \
baike.so.com/doc/6900892-10434866.html \
baike.so.com/doc/6900892-25003153.html \
baike.so.com/doc/7953997-8238479.html \
baike.so.com/doc/6900892-7121579.html \
baike.so.com/doc/6900892-10493334.html \
baike.so.com/doc/6900892-10511247.html \
baike.so.com/doc/6900892-24932290.html \
baike.so.com/doc/6900892-24967609.html \
baike.so.com/doc/5488058-13772750.html \
baike.so.com/doc/5488058-5725970.html \
baike.so.com/doc/131616-138996.html \
baike.so.com/doc/7324655-7554297.html \
baike.so.com/doc/4280208-4483441.html \
baike.so.com/doc/6120709-6333858.html \
baike.so.com/doc/5978224-6191185.html \
baike.so.com/doc/7129291-7352593.html \
baike.so.com/doc/6742319-6956844.html \
baike.so.com/doc/6492878-24791255.html \
baike.so.com/doc/5349374-5584830.html \
baike.so.com/doc/8433713-8753584.html \
baike.so.com/doc/2785795-7624588.html \
baike.so.com/doc/7208864-7433553.html \
baike.so.com/doc/7099759-7322726.html \
baike.so.com/doc/5666247-5878906.html \
baike.so.com/doc/7014276-7237163.html \
baike.so.com/doc/7014582-7237469.html \
baike.so.com/doc/9883253-10230368.html \
baike.so.com/doc/2582857-2727470.html \
baike.so.com/doc/8736542-9059519.html \
baike.so.com/doc/125863-132966.html \
baike.so.com/doc/3688690-3876616.html \
baike.so.com/doc/4391556-4598176.html \
baike.so.com/doc/6707957-6921972.html
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