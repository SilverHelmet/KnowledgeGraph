sentence_path="result/cache/sentences.txt"
document_path="result/cache/documents.json"
stf_result_path="result/cache/stanford_results.txt"
python -m src.baike_process.process_page $1 "$sentence_path" "$document_path"

cd java
java -mx3g -cp "*:lib/*:." ChNlp_v2 "../${sentence_path}" "../${stf_result_path}"
cd ..

python -m src.extractor.main "${document_path}" "${sentence_path}" "${stf_result_path}" $2