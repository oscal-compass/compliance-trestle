# Experiments
## Summary
This directory is designed to capture various experiments used for development purposes in the trestle project.

# Setup configuration for experiments
## Profiling setup
In order to setup profiling you also need visualisation tooling to be effective. Following https://medium.com/@narenandu/profiling-and-visualization-tools-in-python-89a46f578989

run `scripts/experiments/profiling_tools_setup_OSX.sh` to setup on a mac. Note it presumes that `brew` is installed.

# List of experiments
# tanium_ben.py
Performance benchmarking of the tanium conversion script. Run from trestle root directory as 
`./scripts/experiments/profile_tanium_ben.sh`

Call stack can be visualised with either:
`gprof2dot -f pstats tanium_ben.pstats | dot -Tpng -o callgraph.png`
or 
`snakeviz tanium_ben.profile` which opens a webserver to explore the results.
