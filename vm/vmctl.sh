#!/usr/bin/env bash
# Laptop-side control of the Project F VM (adapted from E's vmctl.sh). Billing events are logged to vm/sessions.log.
#   vm/vmctl.sh restore   create RG, disk from the D archive snapshot, VM (SSH from your IP only, auto-shutdown)
#   vm/vmctl.sh start | stop (DEALLOCATE) | status | ssh | ip
#   vm/vmctl.sh push      copy F code (no data) to ~/f on the VM
#   vm/vmctl.sh fetch RUN copy ~/f/experiments/*/runs/RUN back and verify SHA256SUMS
#   vm/vmctl.sh hours     logged VM hours and compute cost
#   vm/vmctl.sh delete    delete the resource group (asks you to type its name; the snapshot is elsewhere and stays)
# Safety: Project E runs in its own resource group (rg-project-e). This script refuses to act on any RG but rg-project-f.
# Size: at most 8 vCPU, so that E's VM (8 vCPU) can always start inside the 20-vCPU regional quota.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"; F_ROOT="$(dirname "$HERE")"
source "$HERE/vm.env"
[ "$RG" = "rg-project-f" ] && [ "$VM" = "vm-project-f" ] || { echo "refusing: vm.env must name rg-project-f / vm-project-f"; exit 1; }
LOG="$HERE/sessions.log"; PRICE_PER_H=0.529
ip() { az vm show -d -g "$RG" -n "$VM" --query publicIps -o tsv; }
note() { echo "$(date -u +%Y-%m-%dT%H:%M:%SZ) $1 $SIZE ${2:-}" >> "$LOG"; }
case "${1:-}" in
  restore)
    MYIP=$(curl -s https://api.ipify.org)
    az group create -n "$RG" -l "$LOCATION" --tags project=F -o none
    az disk create -g "$RG" -n "${VM}-osdisk" --source "$SNAPSHOT_ID" --sku "$DISK_SKU" --size-gb "$DISK_GB" \
      --os-type Linux --hyper-v-generation V2 --tags project=F -o none
    az vm create -g "$RG" -n "$VM" --attach-os-disk "${VM}-osdisk" --os-type linux --size "$SIZE" \
      --disk-controller-type "$DISK_CONTROLLER" --public-ip-sku Standard --nsg-rule NONE \
      --assign-identity '[system]' --tags project=F -o none
    note start
    az network nsg rule create -g "$RG" --nsg-name "${VM}NSG" -n ssh-from-my-ip --priority 1000 \
      --source-address-prefixes "$MYIP/32" --destination-port-ranges 22 --protocol Tcp --access Allow -o none
    VMID=$(az vm show -g "$RG" -n "$VM" --query id -o tsv)
    PRINCIPAL=$(az vm show -g "$RG" -n "$VM" --query identity.principalId -o tsv)
    az role assignment create --assignee-object-id "$PRINCIPAL" --assignee-principal-type ServicePrincipal \
      --role "Virtual Machine Contributor" --scope "$VMID" -o none   # lets the VM deallocate itself (self_deallocate.sh)
    az vm auto-shutdown -g "$RG" -n "$VM" --time "$AUTO_SHUTDOWN_UTC" -o none
    echo "VM up at $(ip)" ;;
  start)  az vm start -g "$RG" -n "$VM" -o none; note start; echo "running at $(ip)" ;;
  stop)   az vm deallocate -g "$RG" -n "$VM" -o none; note stop; echo deallocated ;;
  status) az vm get-instance-view -g "$RG" -n "$VM" --query "instanceView.statuses[1].displayStatus" -o tsv; ip ;;
  ip)     ip ;;
  myip)   # the laptop's public IP changes: refresh the SSH rule
    MYIP=$(curl -s https://api.ipify.org)
    az network nsg rule update -g "$RG" --nsg-name "${VM}NSG" -n ssh-from-my-ip --source-address-prefixes "$MYIP/32" -o none
    echo "SSH allowed from $MYIP" ;;
  ssh)    shift; ssh -o ServerAliveInterval=60 -o StrictHostKeyChecking=accept-new "$ADMIN@$(ip)" "$@" ;;
  push)   rsync -az --exclude 'data/' --exclude 'runs/' --exclude 'paper/' --exclude 'lit/' --exclude 'vm/sessions.log' \
            --exclude 'vm/vm.env' "$F_ROOT/" "$ADMIN@$(ip):f/" ;;
  fetch)
    RUN="${2:?usage: vmctl.sh fetch RUN_ID}"
    SRC=$(ssh "$ADMIN@$(ip)" "ls -d f/experiments/*/runs/$RUN" ) ; DEST="$F_ROOT/${SRC#f/}"
    [ -e "$DEST" ] && { echo "$DEST exists; never overwrite a run"; exit 1; }
    mkdir -p "$DEST"; rsync -az "$ADMIN@$(ip):$SRC/" "$DEST/"; (cd "$DEST" && sha256sum -c --quiet SHA256SUMS && echo "checksums OK") ;;
  hours)
    python3 - "$LOG" "$PRICE_PER_H" <<'PY'
import sys, datetime as dt
total, start = 0.0, None
for line in open(sys.argv[1]):
    ts, ev = line.split()[:2]; t = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    if ev == "start" and start is None: start = t
    elif ev in ("stop", "delete") and start is not None: total += (t - start).total_seconds()/3600; start = None
print(f"logged VM hours {total:.2f}; compute ~${total*float(sys.argv[2]):.2f}" + (" (still running)" if start else ""))
PY
    ;;
  delete)
    read -r -p "Type $RG to delete it: " a; [ "$a" = "$RG" ] || exit 1
    az group delete -n "$RG" --yes --no-wait; note delete ;;
  *) sed -n '2,10p' "$0"; exit 1 ;;
esac
