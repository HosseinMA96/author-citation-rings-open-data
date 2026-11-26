#!/usr/bin/env bash
# Run ON THE F VM: deallocates this VM through its managed identity (role granted by vmctl.sh restore).
# Unlike `sudo shutdown`, deallocation stops compute billing. Acts only on the VM it runs on (instance metadata).
set -euo pipefail
md() { curl -s -H Metadata:true "http://169.254.169.254/metadata/$1"; }
TOKEN=$(md "identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/" \
        | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
read -r SUB RG NAME < <(md "instance/compute?api-version=2021-02-01" \
        | python3 -c "import json,sys; c=json.load(sys.stdin); print(c['subscriptionId'], c['resourceGroupName'], c['name'])")
[ "$NAME" = "vm-project-f" ] || { echo "refusing: this script deallocates vm-project-f only (found $NAME)"; exit 1; }
echo "$(date -u +%FT%TZ) self-deallocating $NAME" | tee -a ~/f/vm/self_deallocate.log
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Length: 0" \
  "https://management.azure.com/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Compute/virtualMachines/$NAME/deallocate?api-version=2024-07-01"
