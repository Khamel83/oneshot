# oneshot — daily digest
_Generated 2026-05-01 00:03 UTC_

- Added daily credit refresh for Manus: new cron (`d9f1097`) and vault vars (`a30c579`, `a03773a`) updated in `scripts/manus‑daily‑refresh.sh` and `secrets/oneshot.env.encrypted`.  
- Fixed Manus v2 API usage: switched to `agent_profile` (`57c9f50`) and set default to `manus-1.6-lite` (`be93c31`).  
- Integrated cross‑project credit tracking into dispatch (`5f9902f`) and added worker routing support (`db748c1`).  
- Updated dispatch runner logic in `core/dispatch/run.py` (three edits) and worker config in `config/workers.yaml` (one edit).  
- **Next action:** Verify the new daily credit refresh cron runs successfully and that credit usage is correctly logged across projects.
