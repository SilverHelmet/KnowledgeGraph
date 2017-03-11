files=(`ls data/freebase`)
length=${#files[@]}
step=3
echo "----------"
for (( st=0; st<length; st+=$step )) 
do
    for i in `seq $st $[$st+$step-1]`
    do
        if [ $i -lt $length ] 
        then
            
            echo ${files[$i]}
            python -u src/extract/extract_ttl_from_fb.py "data/freebase/${files[$i]}" "result/freebase" >& "log/extract_fb_${files[$i]}.log" &
        fi
    done
    wait
    echo "----------"
done