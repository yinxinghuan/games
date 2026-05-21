#!/usr/bin/env python3
"""Add a permanent random uuid (uuid4) to every game in games.json.

Rules (per colleague's spec):
- Use a real UUID generator (uuid.uuid4()).
- UUID is permanent — never regenerated if a game is updated or redeployed.
- No slot reuse — even if a game is deleted, no future game inherits its UUID.

This script enforces those rules by being idempotent: if an entry already has
a `uuid` field, it is left untouched. New games appended later that lack a
uuid will get a fresh one on the next run.

`uuid` is inserted immediately after `id` for readability.
"""

import json
import sys
import uuid
from pathlib import Path
from collections import OrderedDict

PATH = Path('/Users/yin/code/games/games/games.json')


def main():
    raw = PATH.read_text()
    # Preserve original object key order using object_pairs_hook=OrderedDict
    games = json.loads(raw, object_pairs_hook=OrderedDict)
    if not isinstance(games, list):
        print(f"error: expected a JSON array at top level, got {type(games).__name__}", file=sys.stderr)
        sys.exit(1)

    added = 0
    kept = 0
    for g in games:
        if not isinstance(g, OrderedDict):
            continue
        if 'uuid' in g and g['uuid']:
            kept += 1
            continue
        new_uuid = str(uuid.uuid4())
        # Place uuid right after id; if no id key, place at the front.
        items = list(g.items())
        rebuilt = OrderedDict()
        inserted = False
        for k, v in items:
            rebuilt[k] = v
            if k == 'id' and not inserted:
                rebuilt['uuid'] = new_uuid
                inserted = True
        if not inserted:
            rebuilt['uuid'] = new_uuid
            rebuilt.move_to_end('uuid', last=False)
        # Replace in place
        g.clear()
        g.update(rebuilt)
        added += 1

    # Match existing formatting: 2-space indent, no extra spaces.
    out = json.dumps(games, ensure_ascii=False, indent=2)
    # Preserve trailing newline if original had one.
    if raw.endswith('\n'):
        out += '\n'
    PATH.write_text(out)
    print(f"added {added}, kept {kept}, total {len(games)}")


if __name__ == '__main__':
    main()
