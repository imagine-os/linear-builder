# Round 4 cross-cutting generator

Generates `plan/round4/gaps/cross-cutting.json` and `plan/round4/digest/cross-cutting.md` from structured issue data.

`python3 build.py` (paths to the Linear inventory snapshot are set at the top of `build.py`). `gen_common.py` renders the canonical PAP spec format and the module trio; `proj_*.py` hold the five proposed projects; `cross.py` the cross-project suggestions; `capmap.py` the capability map.
