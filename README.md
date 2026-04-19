# dk1-policy

Canonical governance policy repository for DK1 platform synchronization.

This repository is the source of truth for:
- Human policy narrative (`standards/`)
- Machine-enforced policy (`policy/policy.yaml` + schema)
- Generated AI agent instruction templates (`templates/`)
- Compliance control mappings (`controls/control_map.csv`)

All product repos pin this repo via `policy.lock`.
