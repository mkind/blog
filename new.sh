#!/bin/bash

now=$(date +"%Y%m%d-%H%M%S")
fn="raw/${now}.txt"

jsondate=$(date +'%Y-%m-%d %H:%M:%S')
echo -e "{\n \"author\": \"mkind\",\n \"date\": \"${jsondate}\",\n \"title\":\"\",\n\"entry\": \"\n\n\"}" > ${fn}
echo "new file ${fn}"
chmod 600 ${fn}
vim -f +5 "+set tw=0 encoding=utf-8" ${fn}
