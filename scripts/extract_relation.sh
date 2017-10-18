python -m src.baike_process.process_page $1 result/cache/sentences.txt result/cache/documents.json

cd java
java -mx3g -cp "*:lib/*:." ChNlp_v2 ../result/cache/sentences.txt ../result/cache/stanford_results.txt
cd ..
