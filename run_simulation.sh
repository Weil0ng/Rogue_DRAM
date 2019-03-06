#!/bin/bash

# $1: dramsim2_root, $2: config_dir $3: trace_path
echo "run DRAMSim2 for configs in $2"
for config in $(find $2 -type f);
do
    echo "running $config"
    # -c -1: runs to end of trace
    # -q: only print last stats
    $1/DRAMSim -t $3 -s $1/system.ini.example -d $config -c -1 -q > $config\_out
done
