import os
import yaml
import hashlib

def dois_from_any(a):
    if isinstance(a, dict):
        for v in a.values():
            yield from dois_from_any(v)
    elif isinstance(a, list):
        for v in a:
            yield from dois_from_any(v)
    elif isinstance(a, str):
        if a.startswith("doi:"):
            yield a

def dois_from_file(filename):
    with open(filename) as f:
        metadata = yaml.load(f, Loader=yaml.SafeLoader)
    yield from dois_from_any(metadata)

def dois_from_folder(folder):
    for root, dirs, files in os.walk(folder):
        for filename in files:
            if filename.endswith(".yaml"):
                path = os.path.join(root, filename)
                yield from dois_from_file(path)

def _main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("folder")
    parser.add_argument("-H", "--hash", default=False, action="store_true", help="output hash of all dois (i.e. to be used as cache key)")
    args = parser.parse_args()

    dois = list(sorted(dois_from_folder(args.folder)))

    if args.hash:
        print(hashlib.sha256(";".join(dois).encode("utf-8")).hexdigest())
    else:
        for d in dois:
            print(d)

if __name__ == "__main__":
    _main()
