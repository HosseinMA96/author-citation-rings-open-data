#!/usr/bin/env bash
# Round-7 run (POSTHOC.md round 7, P20), started on the VM with nohup; log in ~/f/data/work/<run>.log, then copied into
# the run folder as stdout.log.
# usage (on the VM): bash ~/f/vm/run_round7.sh RUN_ID
PY=~/mamba/envs/d/bin/python
RUN="$1"
cd ~/f/experiments/f19_informative && /usr/bin/time -v $PY f19_informative.py "$RUN" f05_scores_20261126_01 f06_eval_20261126_02 f14_class3_20261126_01 1000 > ~/f/data/work/"$RUN".log 2>&1
rc=$?
[ -d runs/"$RUN" ] && cp ~/f/data/work/"$RUN".log runs/"$RUN"/stdout.log
echo "$RUN exit $rc" >> ~/f/data/work/round7.done
