import sys
import yaml
import json
from .meta import load_metadata_from_folder, create_backward_links, check_metadata_consistency

import logging

def _main():
    logging.basicConfig()
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    parser.add_argument("-j", "--json", default=False, action="store_true")
    parser.add_argument("-v", "--validate", default=False, action="store_true")
    args = parser.parse_args()
    meta = create_backward_links(load_metadata_from_folder(args.folder))
    if args.validate:
        res = list(check_metadata_consistency(meta))
        if len(res) > 0:
            for status, message in res:
                print(f"{status}: {message}", file=sys.stderr)
            return -1

    if args.json:
        json.dump(meta, sys.stdout)
    else:
        yaml.dump(meta, sys.stdout, allow_unicode=True)
    return 0

if __name__ == "__main__":
    exit(_main())
