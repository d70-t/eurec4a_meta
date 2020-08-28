import sys
import yaml
from .meta import load_metadata_from_folder

def _main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    args = parser.parse_args()

    yaml.dump(load_metadata_from_folder(args.folder), sys.stdout, allow_unicode=True)

if __name__ == "__main__":
    _main()
