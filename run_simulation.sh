#!/bin/bash

# $1: dramsim2_root, $2: config_dir $3: trace_path
echo "run DRAMSim2 for configs in $2"
result_dir=$2/results/
mkdir -p $result_dir
for config in $(find $2 -maxdepth 1 -type f);
do
    base_name=$(basename $config)
    echo "running "
    # -c -1: runs to end of trace
    # -q: only print last stats
    $1/DRAMSim -t $3 -s $1/system.ini.example -d $config -c -1 -q > $result_dir/$base_name
done
