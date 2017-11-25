urls="\
baike.so.com/doc/10002015-10349837.html \
baike.so.com/doc/10039831-10518959.html \
baike.so.com/doc/10796041-11321408.html \
baike.so.com/doc/10922791-11449622.html \
baike.so.com/doc/1287918-1361771.html \
baike.so.com/doc/1303554-1378305.html \
baike.so.com/doc/1329102-1405117.html \
baike.so.com/doc/1907411-2018222.html \
baike.so.com/doc/1924517-2036078.html \
baike.so.com/doc/1939057-2051423.html \
baike.so.com/doc/1957541-2071614.html \
baike.so.com/doc/1957541-2071736.html \
baike.so.com/doc/2395509-2532834.html \
baike.so.com/doc/24057343-24640596.html \
baike.so.com/doc/24095892-24681185.html \
baike.so.com/doc/24150249-24735565.html \
baike.so.com/doc/2448276-2588126.html \
baike.so.com/doc/2510451-2652822.html \
baike.so.com/doc/3433066-3613205.html \
baike.so.com/doc/3450004-3630414.html \
baike.so.com/doc/3518333-3700879.html \
baike.so.com/doc/3842047-4034216.html \
baike.so.com/doc/4088529-4287339.html \
baike.so.com/doc/41377-43258.html \
baike.so.com/doc/4170124-4370438.html \
baike.so.com/doc/4237218-4439330.html \
baike.so.com/doc/4237218-4439337.html \
baike.so.com/doc/4360390-4565950.html \
baike.so.com/doc/4691276-11489453.html \
baike.so.com/doc/4691276-4905274.html \
baike.so.com/doc/4786053-5002045.html \
baike.so.com/doc/4788532-5004544.html \
baike.so.com/doc/4802566-5018824.html \
baike.so.com/doc/4807897-5024301.html \
baike.so.com/doc/4810769-5027181.html \
baike.so.com/doc/4835038-5051941.html \
baike.so.com/doc/4835393-5052275.html \
baike.so.com/doc/4967800-5190172.html \
baike.so.com/doc/4972129-5194758.html \
baike.so.com/doc/5127203-5356541.html \
baike.so.com/doc/5329601-5564775.html \
baike.so.com/doc/5341986-5577429.html \
baike.so.com/doc/5341986-7572116.html \
baike.so.com/doc/5344366-5579811.html \
baike.so.com/doc/5344897-5580342.html \
baike.so.com/doc/5348516-5583969.html \
baike.so.com/doc/5382393-5618748.html \
baike.so.com/doc/5385244-5621690.html \
baike.so.com/doc/5416096-5654241.html \
baike.so.com/doc/5469311-5707223.html \
baike.so.com/doc/5470573-5708485.html \
baike.so.com/doc/5474694-5712606.html \
baike.so.com/doc/5475995-5713907.html \
baike.so.com/doc/5476183-5714095.html \
baike.so.com/doc/5497680-5735594.html \
baike.so.com/doc/5497807-5735721.html \
baike.so.com/doc/574984-608736.html \
baike.so.com/doc/5957655-6170599.html \
baike.so.com/doc/6601129-6814914.html \
baike.so.com/doc/6707957-6921972.html \
baike.so.com/doc/6786808-7003415.html \
baike.so.com/doc/6816526-7033542.html \
baike.so.com/doc/6896918-7114567.html \
baike.so.com/doc/6900892-10434866.html \
baike.so.com/doc/6900892-7121579.html \
baike.so.com/doc/6911754-7133611.html \
baike.so.com/doc/7089883-7312796.html \
baike.so.com/doc/7598295-7872390.html \
baike.so.com/doc/811373-858159.html \
baike.so.com/doc/8496731-8817019.html \
baike.so.com/doc/8751871-9075265.html \
baike.so.com/doc/9251204-9584628.html \
baike.so.com/doc/927168-980024.html \
baike.so.com/doc/9275617-9609591.html
"
paths="\
result/rel_extraction/baike_static_info.tsv \
result/rel_extraction/baike_names.tsv \
result/rel_extraction/baike_filtered_summary.json \
result/rel_extraction/baike_filtered_summary_with_infobox.json \
result/rel_extraction/baike_ename_title.tsv \
result/360/360_entity_info_processed.json \
"
sample_dir="result/samples"
for path in $paths
do
    filename=$(basename $path)
    echo $filename
    # rm ${path}.sample

    for url in $urls
    do
        grep -m 1 ${url} ${path} >> ${sample_dir}/${filename}
    done
done