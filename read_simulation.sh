#!/bin/bash
# ./read_simulation.sh ./ out.txt
# $1: dramsim2_root, $2: output_file

IFS=$'\n'

echo -n '' > "$2"
echo "Bandwith Power" >> "$2"
for file_name in $(find  "$1" -type f -name "DDR3_micron_64M_8B_x4_sg15.*"); 
do 
cat "$file_name" | grep bandwidth | grep -o '[0-9.]\+'GB | sed 's/GB//g' | tr '\n' ' ' >> "$2"
cat "$file_name" | grep Average | grep Power | grep -o '[0-9.]\+' >> "$2"
#echo "" >>> "$2"
done
