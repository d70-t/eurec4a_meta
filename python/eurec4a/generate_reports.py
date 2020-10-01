import os
import shutil
from collections import defaultdict

from .meta import load_metadata_from_folder, create_backward_links

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

def configure_platform(metadata, platform_configuration_id):
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
                       and e["measured by"] == ic["id"]},
         "configuration": ic}
        for ic in instrument_configurations
    ]
    return {"platform_configuration": platform_configuration,
            "platform": platform,
            "configured_instruments": configured_instruments}

def render_instruments(metadata, output_folder):
    instruments = [e.copy() for e in metadata.values() if e["type"] == "instrument"]
    for instrument in instruments:
        instrument["_related"] = {
            "platforms": sorted(list({metadata[metadata[ic]["part of"]]["configuration of"]
                                      for ic in instrument["configurations"]}))
            }
    print(instruments)
    tpl = html_env.get_template("instruments.html")
    with open(os.path.join(output_folder, "instruments.html"), "w") as outfile:
        outfile.write(tpl.render(objects=metadata,
                                 instruments=instruments))

def render_instruments_on_platform_and_campaign(metadata, output_folder, platform_configuration_id):
    config = configure_platform(metadata, platform_configuration_id)
    tpl = html_env.get_template("instruments_on_platform_and_campaign.html")
    with open(os.path.join(output_folder, "instruments_{}.html".format(platform_configuration_id)), "w") as outfile:
        outfile.write(tpl.render(objects=metadata, **config))

def render_platforms(metadata, output_folder):
    platforms = [e.copy() for e in metadata.values() if e["type"] == "platform"]
    for platform in platforms:
        platform["_related"] = {
            "instruments": sorted(list({metadata[ic]["configuration of"]
                                        for pc in platform["configurations"]
                                        for ic in metadata[pc]["contains"]}))
            }
    print(platforms)
    tpl = html_env.get_template("platforms.html")
    with open(os.path.join(output_folder, "platforms.html"), "w") as outfile:
        outfile.write(tpl.render(objects=metadata,
                                 platforms=platforms))

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
    config = configure_platform(metadata, platform_configuration_id)
    tpl = tex_env.get_template("platform_configuration.tex")
    with open(os.path.join(output_folder, "platform_configuration_{}.tex".format(platform_configuration_id)), "w") as outfile:
        outfile.write(tpl.render(objects=metadata, **config))

def _main():
    import argparse

    default_metadata_folder = os.path.join(os.path.dirname(__file__), "..", "..", "metadata")
    static_html_folder = os.path.join(os.path.dirname(__file__), "static", "html")

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output_folder", type=str, default=".")
    parser.add_argument("-m", "--metadata_folder", type=str, default=default_metadata_folder)
    args = parser.parse_args()

    metadata = create_backward_links(load_metadata_from_folder(args.metadata_folder))

    shutil.copytree(static_html_folder,
                    os.path.join(args.output_folder, "static"),
                    dirs_exist_ok=True)

    tabulate(metadata, args.output_folder)
    render_instruments(metadata, args.output_folder)
    render_instruments_on_platform_and_campaign(metadata, args.output_folder, "HALO_EUREC4A")
    render_platforms(metadata, args.output_folder)
    render_tex_instruments(metadata, args.output_folder)
    render_tex_platform_configuration(metadata, args.output_folder, "HALO_EUREC4A")
    

if __name__ == "__main__":
    _main()
