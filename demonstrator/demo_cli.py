from __future__ import annotations

import json
from pathlib import Path

import server

ROOT = Path(__file__).resolve().parent
UX = json.loads((ROOT / 'ux_config_v1_1.json').read_text(encoding='utf-8'))
CASES = {row['id']: row for row in server.CONFIG['cases']}


def main() -> None:
    print('CFC Demonstrator — 60-second CLI review')
    print('Does the available evidence actually justify closing the AI decision?')
    print()

    total = len(UX['path'])
    for i, case_id in enumerate(UX['path'], start=1):
        row = CASES[case_id]
        live = server.run_case(case_id)
        presentation = live['presentation']

        print(f'[{i}/{total}] {row["title"]}')
        print(f'Model: {row["model_conclusion"]}')
        print(f'CFC state: {presentation.get("claim_state") or row.get("claim_state")}')
        print(f'Decision: {presentation["decision"]}')
        print(f'Why: {UX["human_explanations"][case_id]}')
        print('Replay matches frozen reference:', 'YES' if live['replay_matches_reference'] else 'NO')
        print('-' * 72)

    print('Review complete.')
    print('CFC is not a block-everything rule: the final case demonstrates valid ALLOW closure.')


if __name__ == '__main__':
    main()
