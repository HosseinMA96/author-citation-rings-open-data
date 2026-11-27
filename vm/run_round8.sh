#!/usr/bin/env bash
# Round-8 run (POSTHOC.md round 8, P21), started on the VM with nohup; log in ~/f/data/work/<run>.log, then copied into
# the run folder as stdout.log.
# usage (on the VM): bash ~/f/vm/run_round8.sh RUN_ID
PY=~/mamba/envs/d/bin/python
RUN="$1"
cd ~/f/experiments/f20_posctrl && /usr/bin/time -v $PY f20_posctrl.py "$RUN" f05_scores_20261126_01 f09_posthoc2_20261126_02 1000 > ~/f/data/work/"$RUN".log 2>&1
rc=$?
[ -d runs/"$RUN" ] && cp ~/f/data/work/"$RUN".log runs/"$RUN"/stdout.log
echo "$RUN exit $rc" >> ~/f/data/work/round8.done
