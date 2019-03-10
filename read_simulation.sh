#!/bin/bash
# ../read_simulation.sh ./DDR3_micron_64M_8B_x4_sg15.ini/results ./out.txt
# $0: dramsim2_root, $1: result_file $2: output_file

IFS=$'\n'

echo -n '' > "$2"
#echo "Index Bandwith Ave_Power" >> "$2"

#for file_name in $(find  "$1" -type f -name "DDR3_micron_64M_8B_x4_sg15.ini_*"); 

for n in {0..10000} 
do 
file_name="$1/DDR3_micron_64M_8B_x4_sg15.ini_$n"
if [ -f "$file_name" ]
then
	echo -n "$n " >> "$2"
	cat "$file_name" | grep bandwidth | grep -o '[0-9.]\+'GB | sed 's/GB//g' | tr '\n' ' ' >> "$2"
	cat "$file_name" | grep Average | grep Power | grep -o '[0-9.]\+' >> "$2"

fi
done
