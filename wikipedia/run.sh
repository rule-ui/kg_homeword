wikiroot=./wikipedia
dataroot=./data

declare -i i=1
while ((i<=10))
do
    python extractor.py \
        --input_file=$wikiroot/wiki_$i$i \
        --output_file=$dataroot/data$i.json
    let i++
done
