#!/usr/bin/env python3
"""Add a `category` field to every game in games.json.

Category values (English lowercase, matching the platform UI rule that
end-user-visible content defaults to English):

    casual      休闲      sensory toys, daily rituals, instant-play ambient
    puzzle      益智      merge/match, memory, spot-diff, word, deduction
    social      社交      cross-user wall-first / friend-targeted games
    action      动作      real-time reflex, dodging, brawler, runner
    shooter     射击      reserved (no games yet)
    racing     竞速     reserved (no games yet)
    strategy    策略      reserved (no games yet)
    simulation  模拟      tycoon, sandbox-build, life-sim
    tool        工具      AlterU Press utilities, AI generators
    other       其他      FMV interactive narrative, anything that doesn't fit

`category` is inserted immediately after `name` for readability.

Idempotent: entries already carrying a `category` are left untouched. New games
appended later that lack a category will get one on the next run *if* they are
in CATEGORIES below; otherwise the script prints a WARN and exits non-zero so
nothing ships uncategorized.
"""

import json
import sys
from pathlib import Path
from collections import OrderedDict

PATH = Path('/Users/yin/code/games/games/games.json')

ALLOWED = {
    'casual', 'puzzle', 'social', 'action', 'shooter',
    'racing', 'strategy', 'simulation', 'tool', 'other',
}

# Canonical mapping. Keys are game ids exactly as they appear in games.json.
CATEGORIES = {
    'sky-leap': 'action',
    # AlterU After Dark — instant-play / daily ritual / sensory
    'trash-or-treasure': 'casual',
    'hold-it-together': 'casual',
    'hour-capsule': 'casual',
    'the-seal-press': 'social',
    'the-daily-arcana': 'casual',
    'bell-tower': 'social',
    'bubble-wrap-eternal': 'casual',
    'static-channel': 'casual',
    'pebble-pocket': 'casual',
    'ink-of-fate': 'social',
    'frost-crystals': 'casual',
    'ferrofluid': 'casual',
    'crack-tap': 'casual',
    'liquid-drop': 'casual',
    'murmuration': 'casual',
    'frosted-window': 'casual',
    'sand-mandala': 'casual',
    'iron-filings': 'casual',
    'atomic': 'casual',
    'lava-lamp': 'casual',
    'aurora': 'casual',
    'bubble-wrap': 'casual',
    'wind-chime': 'casual',
    'marbles': 'casual',
    'snowglobe': 'casual',
    'hourglass': 'casual',
    'one-tap-a-day': 'casual',
    'tap-and-tell': 'casual',

    # Puzzle — merge, memory, spot-diff, word capture, deduction
    'build-a-boyfriend': 'puzzle',
    'botfish': 'puzzle',
    'depthy': 'puzzle',
    'agent-string-v2': 'puzzle',
    'agent-string': 'puzzle',
    'spot-diff-s2': 'puzzle',
    'spot-diff': 'puzzle',
    'memory-card': 'puzzle',

    # Social — cross-user wall-first / friend-targeted / collective ritual
    'the-stand-in': 'social',
    'tap-and-tell-vertical': 'social',
    'kiss-wall': 'social',
    'mugshot-booth': 'social',
    'confession-booth': 'social',
    'confession-booth-v4': 'social',
    'wake-up-service': 'social',
    'crystal-ball-collective': 'social',
    'tag-youre-it': 'social',
    'pet-filter': 'social',

    # Action — real-time reflex, brawler, runner, rhythm
    'river-row': 'action',
    'block-hop': 'action',
    'vital-signs': 'action',
    'corner-office': 'action',
    'endless-slice': 'action',
    'tidal-survive': 'action',
    'sumo-king': 'action',
    'lantern': 'action',
    'penguin-sumo': 'action',
    'beat-drop': 'action',
    'piper-sheepdog': 'action',
    'penguin-rescue': 'action',
    'slap-cam': 'action',
    'magnet-drop': 'action',
    'stack': 'action',
    'layer-pop': 'action',
    'ume-battle': 'action',
    'flappy-bird': 'action',
    'whack-a-mole': 'action',

    # Simulation — tycoon, sandbox-build, life-sim
    'alter-isle-mini': 'simulation',
    'mykonos-island': 'simulation',
    'tiny-farm': 'simulation',
    'ume-boba-shop': 'simulation',
    'ghost-garden': 'simulation',
    'pitch': 'simulation',
    'bsod': 'simulation',
    'convenience-store': 'simulation',
    'shelf-it': 'simulation',

    # Tool — AlterU Press utilities, AI generators, music makers
    'fit-check': 'tool',
    'alteru-press-almanac': 'tool',
    'alteru-press-field-guide': 'tool',
    'meow-machine': 'tool',
    'rhythm-machine': 'tool',
    'ai-drama': 'tool',
    'my-meme': 'tool',
    'album-cover-generator': 'tool',

    # Other — FMV interactive narrative (V1 / v2 / v3)
    'last-pour': 'other',
    'going-down': 'other',
    'last-train': 'other',
    'the-locksmith': 'other',
    'the-midnight-dinner': 'other',
    'the-audition': 'other',
    'house-of-the-moon': 'other',
    'the-couturier': 'other',
    'the-photographer': 'other',
    'late-check-in': 'other',
    'mykonos-five-days': 'other',
    'the-bidding': 'other',
    'dispatch': 'other',
    'rileyontheradio': 'other',
    'setting-the-table': 'other',
    'replicant-wake': 'other',
    'the-confession': 'other',
    'boy-next-door': 'other',
    'last-cigarette': 'other',
    'pulp-hour': 'other',
}


def main():
    raw = PATH.read_text()
    games = json.loads(raw, object_pairs_hook=OrderedDict)
    if not isinstance(games, list):
        print(f"error: expected JSON array at top level, got {type(games).__name__}", file=sys.stderr)
        sys.exit(1)

    added = 0
    kept = 0
    missing = []

    for g in games:
        if not isinstance(g, OrderedDict):
            continue
        if 'category' in g and g['category']:
            if g['category'] not in ALLOWED:
                print(f"WARN: {g.get('id')} has unknown category {g['category']!r}", file=sys.stderr)
            kept += 1
            continue
        gid = g.get('id')
        if gid not in CATEGORIES:
            missing.append(gid)
            continue
        cat = CATEGORIES[gid]
        if cat not in ALLOWED:
            print(f"error: mapping for {gid} uses unknown category {cat!r}", file=sys.stderr)
            sys.exit(1)

        # Insert `category` right after `name`. Fall back to end of object if no `name`.
        items = list(g.items())
        rebuilt = OrderedDict()
        inserted = False
        for k, v in items:
            rebuilt[k] = v
            if k == 'name' and not inserted:
                rebuilt['category'] = cat
                inserted = True
        if not inserted:
            rebuilt['category'] = cat
        g.clear()
        g.update(rebuilt)
        added += 1

    if missing:
        print(f"\nERROR: {len(missing)} game(s) in games.json have no entry in CATEGORIES:", file=sys.stderr)
        for gid in missing:
            print(f"  - {gid}", file=sys.stderr)
        print(f"\nAdd them to CATEGORIES in {PATH.parent}/add-categories.py and rerun.", file=sys.stderr)
        sys.exit(2)

    out = json.dumps(games, ensure_ascii=False, indent=2)
    if raw.endswith('\n'):
        out += '\n'
    PATH.write_text(out)
    print(f"added {added}, kept {kept}, total {len(games)}")


if __name__ == '__main__':
    main()
