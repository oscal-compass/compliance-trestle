#!/usr/bin/env bash
# run from the root of compliance trestle

echo 'Running tanium_ben with profiling'
echo 'This runs the benchmark twice for different outputs'
echo 'There may be more optimal calling methods'

python -m cProfile -o tanium_ben.pstats scripts/experiments/tanium_ben.py
python -m cProfile -o tanium_ben.profile scripts/experiments/tanium_ben.py