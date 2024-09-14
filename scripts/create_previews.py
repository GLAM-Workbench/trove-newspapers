import nbformat
from nbconvert import HTMLExporter
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path
import argparse

def main(path):
    if path:
        output = Path(path, "previews")
    else:
        output = Path("previews")
    output.mkdir(exist_ok=True)

    nbs = [n for n in Path(".").glob("*.ipynb") if not n.name.startswith(("index.", "draft", "Untitled", "snippets"))]
    for nb_path in nbs:
        print(nb_path.name)
        with nb_path.open() as f:
            nb = nbformat.read(f, as_version=4)
            #ep = ExecutePreprocessor(skip_cells_with_tag="nbval-skip")
            #ep.preprocess(nb, {'metadata': {'path': '.'}})
            html_exporter = HTMLExporter()

            # 3. Process the notebook we loaded earlier
            (body, resources) = html_exporter.from_notebook_node(nb)

            Path(output, f"{nb_path.stem}.html").write_text(body)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path", type=str, help="Path to save", required=False
    )
    args = parser.parse_args()
    main(args.path)
