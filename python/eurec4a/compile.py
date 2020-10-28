import sys
import yaml
import json
from .meta import load_metadata_from_folder, create_backward_links

def _main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    parser.add_argument("-j", "--json", default=False, action="store_true")
    args = parser.parse_args()
    meta = create_backward_links(load_metadata_from_folder(args.folder))
    if args.json:
        json.dump(meta, sys.stdout)
    else:
        yaml.dump(meta, sys.stdout, allow_unicode=True)

if __name__ == "__main__":
    _main()
