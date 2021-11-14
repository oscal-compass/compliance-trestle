#!/usr/bin/env bash
# run from the root of compliance trestle

echo 'Running json_serialize_ben with profiling'

python -m cProfile -o json_serialize.pstats scripts/experiments/json_serialize_ben.py

gprof2dot -f pstats json_serialize.pstats | dot -Tpng -o callgraph.png

open callgraph.png
