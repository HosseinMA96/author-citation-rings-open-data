#!/usr/bin/env bash
# Round-4 post hoc run (POSTHOC.md round 4), started on the VM with nohup; log in ~/f/data/work/<run>.log, then copied
# into the run folder as stdout.log. usage (on the VM): bash ~/f/vm/run_round4.sh RUN_ID
PY=~/mamba/envs/d/bin/python
RUN="$1"
cd ~/f/experiments/f14_class3 && /usr/bin/time -v $PY f14_class3.py "$RUN" f05_scores_20261126_01 1000 > ~/f/data/work/"$RUN".log 2>&1
rc=$?
[ -d runs/"$RUN" ] && cp ~/f/data/work/"$RUN".log runs/"$RUN"/stdout.log
echo "$RUN exit $rc" >> ~/f/data/work/round4.done
