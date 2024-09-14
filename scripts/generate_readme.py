from rocrate.rocrate import ROCrate
import json
from pathlib import Path
import re

def get_create_action(crate, datafile):
    actions = crate.get_by_type("CreateAction")
    for action in actions:
        props = action.properties()
        for result in props["result"]:
            if result["@id"] == datafile:
                return action

crate = ROCrate("./")
root = crate.get("./").properties()
gw_section = crate.get(root["mainEntityOfPage"]["@id"])

md = f"# {root['name']}\n\n"

if version := root.get("version"):
    md += f"CURRENT VERSION: {version}\n\n"

md += f"{root['description']}\n\n"
md += f"For more information and documentation see the [{gw_section['name']}]({gw_section['url']}) section of the [GLAM Workbench](https://glam-workbench.net)."
md += "\n\n## Notebooks\n"
details = "\n\n## Dataset details"

for nb in crate.get_by_type(["File", "SoftwareSourceCode"]):
    md += f'- [{nb["name"]}]({nb["url"]})\n'

datasets = []
for action in crate.get_by_type("CreateAction"):
    print(action)
    for result in action["result"]:
        dataset = crate.get(result["@id"])
        try:
            source = crate.get(dataset["isPartOf"]["@id"])
            datasets.append(source)
        except KeyError:
            datasets.append(dataset)
        

if datasets:
    md += "\n\n## Associated datasets\n"
    for ds in list(set(datasets)):
        md += f'- [{ds["name"]}]({ds["url"]})\n'

md += "\n\n<!-- START RUN INFO -->\n\n<!-- END RUN INFO -->"

md += "\n\n----\nCreated by [Tim Sherratt](https://timsherratt.au) for the [GLAM Workbench](https://glam-workbench.net)"


md = re.sub(r'<style type="text/css">\s*</style>', '', md)
Path("README.md").write_text(md)
