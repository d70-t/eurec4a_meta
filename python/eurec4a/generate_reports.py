import os

from .meta import load_metadata_from_folder

from jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader('eurec4a', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

def render_instruments(metadata, output_folder):
    instruments = [e for e in metadata.values() if e["type"] == "instrument"]
    print(instruments)
    tpl = env.get_template("instruments.html")
    with open(os.path.join(output_folder, "instruments.html"), "w") as outfile:
        outfile.write(tpl.render(objects=metadata,
                                 instruments=instruments))

def _main():
    import argparse

    default_metadata_folder = os.path.join(os.path.dirname(__file__), "..", "..", "metadata")

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_folder", type=str, default=".")
    parser.add_argument("-m", "--metadata_folder", type=str, default=default_metadata_folder)
    args = parser.parse_args()

    metadata = load_metadata_from_folder(args.metadata_folder)

    render_instruments(metadata, args.output_folder)
    

if __name__ == "__main__":
    _main()
