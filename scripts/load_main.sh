patterns="chunk00*ttl chunk01*ttl chunk02*ttl chunk03*ttl chunk04*ttl chunk05*ttl chunk06*ttl chunk07*ttl chunk08*ttl chunk09*ttl chunk10*ttl chunk11*ttl chunk12*ttl chunk13*ttl"
for pattern in $patterns
do
    isql 13093 dba dba exec="ld_dir('/home/lhr/KnowledgeGraph/data/freebase', '${pattern}', 'freebase');"
    isql 13093 dba dba exec="rdf_loader_run();" &
    isql 13093 dba dba exec="rdf_loader_run();" &
    isql 13093 dba dba exec="rdf_loader_run();" &
    wait
    isql 13093 dba dba exec="checkpoint;"


done