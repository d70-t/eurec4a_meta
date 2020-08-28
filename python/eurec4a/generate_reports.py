import os
from collections import defaultdict

from .meta import load_metadata_from_folder

from jinja2 import Environment, PackageLoader, select_autoescape
html_env = Environment(
    loader=PackageLoader('eurec4a', os.path.join('templates', 'html')),
    autoescape=select_autoescape(['html', 'xml'])
)

tex_env = Environment(
    block_start_string='\BLOCK{',
    block_end_string='}',
    variable_start_string='\VAR{',
    variable_end_string='}',
    comment_start_string='\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=PackageLoader('eurec4a', os.path.join('templates', 'tex')),
)

def render_instruments(metadata, output_folder):
    instruments = [e for e in metadata.values() if e["type"] == "instrument"]
    print(instruments)
    tpl = html_env.get_template("instruments.html")
    with open(os.path.join(output_folder, "instruments.html"), "w") as outfile:
        outfile.write(tpl.render(objects=metadata,
                                 instruments=instruments))

def tabulate(metadata, output_folder):
    keys_per_type = defaultdict(set)
    for o in metadata.values():
        keys_per_type[o["type"]] |= set(o)

    display_keys = {t: ["id"] + list(sorted(k - {"id", "type"}))
                    for t, k in keys_per_type.items()}

    tabulated = {}
    for t, ks in display_keys.items():
        rows = [
            [o.get(k, None) for k in ks]
            for o in metadata.values()
            if o["type"] == t
        ]
        tabulated[t] = {"column_names": ks, "rows": rows}

    tpl = html_env.get_template("object_table.html")
    with open(os.path.join(output_folder, "object_table.html"), "w") as outfile:
        outfile.write(tpl.render(objects=metadata,
                                 tabulated=tabulated))

def render_tex_instruments(metadata, output_folder):
    instruments = [e for e in metadata.values() if e["type"] == "instrument"]
    print(instruments)
    tpl = tex_env.get_template("instruments.tex")
    with open(os.path.join(output_folder, "instruments.tex"), "w") as outfile:
        outfile.write(tpl.render(objects=metadata,
                                 instruments=instruments))

def render_tex_platform_configuration(metadata, output_folder, platform_configuration_id):
    platform_configuration = metadata[platform_configuration_id]
    platform_id = platform_configuration["configuration of"]
    instrument_configurations = [e for e in metadata.values()
            if e["type"] == "instrument_configuration"
            and e["part of"] == platform_configuration_id]

    platform = metadata[platform_id]

    configured_instruments = [
        {**metadata[ic["configuration of"]],
         "variables": {k: e for k, e in metadata.items()
                       if e["type"] == "variable"
                       and e["measured by"] == ic["id"]}}
        for ic in instrument_configurations
    ]

    tpl = tex_env.get_template("platform_configuration.tex")
    with open(os.path.join(output_folder, "platform_configuration_{}.tex".format(platform_configuration_id)), "w") as outfile:
        outfile.write(tpl.render(objects=metadata,
                                 platform_configuration=platform_configuration,
                                 platform=platform,
                                 configured_instruments=configured_instruments))

def _main():
    import argparse

    default_metadata_folder = os.path.join(os.path.dirname(__file__), "..", "..", "metadata")

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_folder", type=str, default=".")
    parser.add_argument("-m", "--metadata_folder", type=str, default=default_metadata_folder)
    args = parser.parse_args()

    metadata = load_metadata_from_folder(args.metadata_folder)

    tabulate(metadata, args.output_folder)
    render_instruments(metadata, args.output_folder)
    render_tex_instruments(metadata, args.output_folder)
    render_tex_platform_configuration(metadata, args.output_folder, "HALO_EUREC4A")
    

if __name__ == "__main__":
    _main()
