document_path="result/cache/documents.json"
python -m src.baike_process.process_page $1 "$document_path"
python -m src.extractor.main "${document_path}" $2