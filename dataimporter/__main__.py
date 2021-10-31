import argparse
import logging
import json
from pathlib import Path

from .achievements import AchievementFixer
from .mounts import MountFixer
from .pets import PetFixer
from .realms import RealmFixer
from .toys import ToyFixer
from .factions import FactionFixer

FIXERS = {
    'achievements': (AchievementFixer, ['achievements.json']),
    'mounts': (MountFixer, ['mounts.json']),
    'pets': (PetFixer, ['pets.json', 'battlepets.json']),
    'realms': (RealmFixer, ['servers.eu.json', 'servers.us.json']),
    'reputations': (FactionFixer, ['factions.json']),
    'toys': (ToyFixer, ['toys.json']),
}


def parse_args():
    def fixer_arg(value: str):
        fixers = value.split(',')
        for fixer in fixers:
            if fixer not in FIXERS:
                raise argparse.ArgumentTypeError(
                    f"Fixer {fixer} does not exit")
        return fixers

    def datadir_arg(value: str):
        p = Path(value)
        if not p.exists():
            raise argparse.ArgumentTypeError(
                f"Path {value} does not exist. Specify it with --datadir?"
            )
        return p

    parser = argparse.ArgumentParser(
        description="Import WoW data to SimpleArmory's JSON database"
    )
    parser.add_argument(
        '--fixers',
        default=','.join(FIXERS.keys()),
        type=fixer_arg,
        help=(
            "Comma-separated list of data importers to run, among: [{}]"
            .format(', '.join(FIXERS.keys()))
        )
    )
    parser.add_argument(
        '--datadir',
        default='./static/data',
        type=datadir_arg,
        help=("Path to the SimpleArmory JSON database directory."
              " Defaults to ./static/data")
    )
    parser.add_argument(
        '--build',
        help=("WoW build prefix (e.g., '9.1' or '9.1.5.40078')."
              " By default the most recent build is used."),
    )
    args = parser.parse_args()
    return args


def main():
    logging.basicConfig(level=logging.INFO)
    args = parse_args()
    for fixer_name in args.fixers:
        logging.info(f"Running fixer '{fixer_name}'.")
        fixer_cls, paths = FIXERS[fixer_name]
        json_paths = [args.datadir / p for p in paths]
        jsons = [json.loads(p.read_text()) for p in json_paths]
        fixer = fixer_cls(*jsons, build=args.build)
        fixed_list = fixer.run()
        for fixed_content, path in zip(fixed_list, json_paths):
            with path.open('w') as json_file:
                json.dump(
                    fixed_content,
                    json_file,
                    indent=2,
                    sort_keys=True,
                    ensure_ascii=False
                )
                json_file.write('\n')


if __name__ == '__main__':
    main()