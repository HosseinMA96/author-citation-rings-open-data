#!/usr/bin/env bash
# Round-6 run (POSTHOC.md round 6, P18-P19), started on the VM with nohup; log in ~/f/data/work/<run>.log, then copied into
# the run folder as stdout.log. CROSSREF_MAILTO (optional) selects Crossref's polite pool and is not written anywhere.
# usage (on the VM): CROSSREF_MAILTO=<address> bash ~/f/vm/run_round6.sh RUN_ID
PY=~/mamba/envs/d/bin/python
RUN="$1"
cd ~/f/experiments/f17_attribution && /usr/bin/time -v $PY f17_attribution.py "$RUN" f05_scores_20261126_01 1000 > ~/f/data/work/"$RUN".log 2>&1
rc=$?
[ -d runs/"$RUN" ] && cp ~/f/data/work/"$RUN".log runs/"$RUN"/stdout.log
echo "$RUN exit $rc" >> ~/f/data/work/round6.done
