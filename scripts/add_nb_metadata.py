import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import nbformat
import re

DEFAULT_AUTHORS = [{
    "name": "Sherratt, Tim",
    "orcid": "https://orcid.org/0000-0001-7956-4498",
    "mainEntityOfPage": "https://timsherratt.au"
}]

def main():
    notebooks = get_notebooks()
    for notebook in notebooks:
        nb = nbformat.read(notebook, nbformat.NO_CONVERT)
        title = extract_notebook_title(nb)
        metadata = {"name": title, "author": DEFAULT_AUTHORS}
        nb.metadata.rocrate = metadata
        # print(nb.metadata)
        nbformat.write(nb, notebook, nbformat.NO_CONVERT)

def extract_notebook_title(nb):
    md_cells = [c for c in nb.cells if c["cell_type"] == "markdown"]
    for cell in md_cells:
        if title := re.search(r"^# (.+)(\n|$)", cell["source"]):
            return title.group(1)
        
def get_notebooks():
    """
    Returns a list of paths to jupyter notebooks in the current directory
    Returns:
        Paths of the notebooks found in the directory
    """
    files = Path(".").glob("*.ipynb")
    is_notebook = lambda file: not file.name.lower().startswith(("draft", "untitled"))
    return list(filter(is_notebook, files))

if __name__ == "__main__":
    main()