import os
import argparse
import datetime
import requests
from giturlparse import parse as ghparse
from git import Repo
from pathlib import Path
import mimetypes
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from rocrate.rocrate import ROCrate
from rocrate.model.person import Person
from rocrate.model.data_entity import DataEntity
from rocrate.model.contextentity import ContextEntity
from extract_metadata import extract_notebook_metadata

load_dotenv()

NOTEBOOK_EXTENSION = ".ipynb"

DEFAULT_LICENCE = {
    "@id": "https://spdx.org/licenses/MIT",
    "name": "MIT License",
    "@type": "CreativeWork",
    "url": "https://spdx.org/licenses/MIT.html",
}

METADATA_LICENCE = {
    "@id": "https://creativecommons.org/publicdomain/zero/1.0/",
    "name": "CC0 Public Domain Dedication",
    "@type": "CreativeWork",
    "url": "https://creativecommons.org/publicdomain/zero/1.0/",
}

NKC_LICENCE = {
    "@id": "http://rightsstatements.org/vocab/NKC/1.0/",
    "@type": "CreativeWork",
    "description": "The organization that has made the Item available reasonably believes that the Item is not restricted by copyright or related rights, but a conclusive determination could not be made.",
    "name": "No Known Copyright",
    "url": "http://rightsstatements.org/vocab/NKC/1.0/"
}
CNE_LICENCE = {
    "@id": "http://rightsstatements.org/vocab/CNE/1.0/",
    "@type": "CreativeWork",
    "description": "The copyright and related rights status of this Item has not been evaluated.",
    "name": "Copyright Not Evaluated",
    "url": "http://rightsstatements.org/vocab/CNE/1.0/"
}

PYTHON = {
    "@id": "https://www.python.org/downloads/release/python-31012/",
    "version": "3.10.12",
    "name": "Python 3.10.12",
    "url": "https://www.python.org/downloads/release/python-31012/",
    "@type": ["ComputerLanguage", "SoftwareApplication"],
}

DEFAULT_AUTHORS = [
    {
        "name": "Sherratt, Tim",
        "orcid": "https://orcid.org/0000-0001-7956-4498",
        "mainEntityOfPage": "https://timsherratt.au",
    }
]

GLAM_WORKBENCH = {
    "@id": "https://glam-workbench.net/",
    "@type": "CreativeWork",
    "name": "GLAM Workbench",
    "url": "https://glam-workbench.net/",
    "description": "A collection of tools, tutorials, examples, and hacks to help researchers work with data from galleries, libraries, archives, and museums (the GLAM sector).",
    "author": [{"@id": "https://orcid.org/0000-0001-7956-4498"}],
}


def main(version, data_repo):
    # Make working directory the parent of the scripts directory
    os.chdir(Path(__file__).resolve().parent.parent)
    # Get a list of paths to notebooks in the cwd
    notebooks = get_notebooks()
    # Update the crate
    update_crate(version, data_repo, notebooks)


def get_notebooks():
    """Returns a list of paths to jupyter notebooks in the given directory

    Parameters:
        dir: The path to the directory in which to search.

    Returns:
        Paths of the notebooks found in the directory
    """
    # files = [Path(file) for file in os.listdir()]
    files = Path(".").glob("*.ipynb")
    is_notebook = lambda file: not file.name.lower().startswith(("draft", "untitled", "index.", "App-"))
    return list(filter(is_notebook, files))


def id_ify(elements):
    """Wraps elements in a list with @id keys
    eg, convert ['a', 'b'] to [{'@id': 'a'}, {'@id': 'b'}]
    """
    # If the input is a string, make it a list
    # elements = [elements] if isinstance(elements, str) else elements
    # Nope - single elements shouldn't be lists, see: https://www.researchobject.org/ro-crate/1.1/appendix/jsonld.html
    if isinstance(elements, str):
        return {"@id": elements}
    else:
        return [{"@id": element} for element in elements]


def add_people(crate, authors):
    """Converts a list of authors to a list of Persons to be embedded within an ROCrate

    Parameters:
        crate: The rocrate in which the authors will be created.
        authors:
            A list of author information.
            Expects a dict with at least a 'name' value ('Surname, Givenname')
            If there's an 'orcid' this will be used as the id (and converted to a uri if necessary)
    Returns:
        A list of Persons.
    """
    persons = []

    # Loop through list of authors
    for author in authors:
        # If there's no orcid, create an id from the name
        if "orcid" not in author or not author["orcid"]:
            author_id = f"#{author['name'].replace(', ', '_')}"

        # If there's an orcid but it's not a url, turn it into one
        elif not author["orcid"].startswith("http"):
            author_id = f"https://orcid.org/{author['orcid']}"

        # Otherwise we'll just use the orcid as the id
        else:
            author_id = author["orcid"]

        # Check to see if there's already an entry for this person in the crate
        author_current = crate.get(author_id)

        # If there's already an entry we'll update the existing properties
        if author_current:
            properties = author_current.properties()

            # Update the name in case it has changed
            # properties.update({"name": author["name"]})
            for key, value in author.items():
                properties.update({key: value})

        # Otherwise set default properties
        else:
            properties = {"name": author["name"]}

        # Add/update the person record and add to the list of persons to return
        persons.append(crate.add(Person(crate, author_id, properties=properties)))

    return persons

def find_local_file(file_name, local_path):
    # Look for local copy of data file in likely locations
    file_path = Path(local_path, file_name)
    if file_path.exists():
        return file_path


def get_file_stats(datafile, local_path):
    """
    Try to get the file size and last modified date of the datafile.
    """
    file_name = datafile.rstrip("/").split("/")[-1]
    local_file = find_local_file(file_name, local_path)
    # If there's a local copy use that to derive stats
    # This means we can get an accurate date modified value (GitHub only gives date committed).
    if local_file and local_file.is_dir():
        size = None
        rows = len(list(local_file.glob("*")))
        # print(rows)
        stats = local_file.stat()
        date = datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d")
    elif local_file:
        # Get file stats from local filesystem
        stats = local_file.stat()
        size = stats.st_size
        date = datetime.datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d")
        if local_file.name.endswith((".zip", ".db")):
            rows = ""
        else:
            rows = 0
            with local_file.open("r") as df:
                for line in df:
                    rows += 1
    elif datafile.startswith("http"):
        # I don't think I want to download the whole file, so set to None
        rows = None
        # Process GitHub links
        if "github.com" in datafile:
            # the ghparser doesn't seem to like 'raw' urls
            datafile = datafile.replace("/raw/", "/blob/")
            gh_parts = ghparse(datafile)

            # API url to get the latest commit for this file
            gh_commit_url = f"https://api.github.com/repos/{gh_parts.owner}/{gh_parts.repo}/commits?path={gh_parts.path_raw.split('/')[-1]}"
            try:
                response = requests.get(gh_commit_url)

                # Get the date of the last commit
                date = response.json()[0]["commit"]["committer"]["date"][:10]

            except (IndexError, KeyError):
                date = None

            # Different API endpoint for file data
            gh_file_url = f"https://api.github.com/repos/{gh_parts.owner}/{gh_parts.repo}/contents/{gh_parts.path_raw.split('/')[-1]}"
            try:
                response = requests.get(gh_file_url)
                contents_data = response.json()
                # Get the file size
                try:
                    size = contents_data["size"]
                except TypeError:
                    size = None

            except KeyError:
                size = None

        else:
            # If the file is online, get size from content headers
            size = requests.head(datafile).headers.get("Content-length")
            date = None

    return date, size, rows


def get_default_gh_branch(url):
    # Process GitHub links
    if "github.com" in url:
        # the ghparser doesn't seem to like 'raw' urls
        url = url.replace("/raw/", "/blob/")
        gh_parts = ghparse(url)
        headers = {'Authorization': f'token {os.getenv("GITHUB_TOKEN")}'}
        gh_repo_url = f"https://api.github.com/repos/{gh_parts.owner}/{gh_parts.repo}"
        response = requests.get(gh_repo_url, headers=headers)
        return response.json().get("default_branch")

def add_files(crate, action, data_type, gw_url, data_repo, local_path):
    """
    Add data files to the crate.
    Tries to extract some basic info about files (size, date) before adding them.
    """
    file_entities = []

    # Loop through list of datafiles
    for df_data in action.get(data_type, []):
        datafile = df_data["url"]
        print(datafile)
        # print(df_data)
        # local_path = action.get("local_path", ".")

        # Check if file exists (or is a url)
        if (
            Path(datafile).exists()
            or (datafile.startswith("http"))
            or (data_repo and data_repo in datafile)
        ):
            # If this is a data repo crate use the file name (not full url) as the id
            if data_repo and data_repo in datafile:
                file_id = datafile.rstrip("/").split("/")[-1]
            else:
                file_id = datafile
            # To construct a full GitHub url to a file we need to find the repo url and default branch
            if not datafile.startswith("http"):
                repo = Repo(".")
                repo_url = repo.git.config("--get", "remote.origin.url").replace(
                    ".git", "/"
                )
                gh_branch = get_default_gh_branch(repo_url)
                file_url = f"{repo_url}blob/{gh_branch}/{datafile}"
            else:
                file_url = datafile

            # Get date and size info
            date, size, rows = get_file_stats(datafile, local_path)

            # Check to see if there's already an entry for this file in the crate
            file_entity = crate.get(file_id)

            # If there's already an entry for this file, we'll keep it's properties
            # but modify the date, size etc later
            if file_entity:
                properties = file_entity.properties()
                # print(properties)

            # Otherwise we'll define default properties for a new file entity
            else:
                if df_data.get("name"):
                    name = df_data.get("name")
                else:
                    name = datafile.rstrip("/").split("/")[-1]
                properties = {
                    "name": name,
                    "url": file_url,
                }

            # Add contextual entities for data repo associated with file
            # If this is a data repo crate, this is not necessary as the crate root will have this
            if data_type == "result" and not data_repo:
                # print(data_type)
                examples = action.get("workExample", [])
                # print(examples)
                add_example_entities(crate, examples)
                if gw_page := action.get("mainEntityOfPage"):
                    add_gw_page_link(crate, gw_page)
                data_repo_url = action.get("isPartOf")
                if data_repo_url:
                    properties["isPartOf"] = id_ify(data_repo_url)
                elif gw_page:
                    properties["mainEntityOfPage"] = id_ify(gw_page)
                    properties["workExample"] = id_ify([e["url"] for e in examples])
                if not crate.get(data_repo_url):
                    
                    data_rocrate = {
                        "@id": data_repo_url,
                        "@type": "Dataset",
                        "url": data_repo_url,
                        "name": data_repo_url.rstrip("/").split("/")[-1]
                    }
                    if data_roc_description := action.get("description"):
                        print(data_roc_description)
                        data_rocrate["description"] = data_roc_description
                    if gw_page:
                        # print(gw_page)
                        data_rocrate["mainEntityOfPage"] = id_ify(gw_page)
                    if current_data_rocrate := crate.get(data_repo_url):
                        current_examples = [e["@id"] for e in current_data_rocrate.properties().get("workExample")]
                    else:
                        current_examples = []
                    data_rocrate["workExample"] = id_ify(list(set([e["url"] for e in examples] + current_examples)))

                    add_context_entity(crate, data_rocrate)
                
                    
            # Guess the encoding type from extension
            encoding = mimetypes.guess_type(datafile)[0]
            if encoding:
                properties["encodingFormat"] = encoding

            if description := df_data.get("description"):
                properties["description"] = description
            if license := df_data.get("license"):
                properties["license"] = id_ify(license)

            # Add/update modified date
            if date:
                properties["dateModified"] = date

            # Add/update file size
            if size:
                properties["contentSize"] = size

            # If it's a CSV add number of rows
            if rows and properties.get("encodingFormat") == "text/csv":
                properties["size"] = rows - 1
            elif rows:
                properties["size"] = rows

            # If it's a web link add today's date to indicate when it was last accessed
            if datafile.startswith("http"):
                properties["sdDatePublished"] = datetime.datetime.now().strftime(
                    "%Y-%m-%d"
                )

            # Add/update the file entity and add to the list of file entities
            local_file = find_local_file(datafile.rstrip("/").split("/")[-1], action.get("local_path", "."))
            # print(datafile, local_file, file_id)
            if data_repo and data_repo in datafile:
                crate_id = local_file
            else:
                crate_id = file_id
            if local_file and local_file.is_dir():
                properties["@type"] = "Dataset"
                file_entities.append(crate.add_dataset(crate_id, properties=properties))
            elif local_file:
                properties["@type"] = ["File", "Dataset"]
                file_entities.append(crate.add_file(crate_id, properties=properties))
            else:
                file_entities.append(crate.add_file(crate_id, properties=properties))
    return file_entities


def add_action(crate, notebook, input_files, output_files, query, index, local_path):
    """
    Links a notebook and associated datafiles through a CreateAction.
    """
    # Create an action id from the notebook name
    action_id = f"{notebook.id.split('/')[-1].replace('.ipynb', '')}_run_{index}"

    # Get a list of dates from the output files
    dates = [f.properties()["dateModified"] for f in output_files if "dateModified" in f.properties()]
    # Find the latest date to use as the endDate for the action
    try:
        last_date = sorted(dates)[-1]

    # There's no dates (or no output files)
    except IndexError:
        # Use the date the notebook was last modified
        last_date, _, _ = get_file_stats(notebook.id, local_path)

    # Check to see if this action is already in the crate
    action_current = crate.get(action_id)
    if action_current:
        # Remove current files from existing action entity
        properties = {"object": [], "result": []}
    else:
        # Default properties for new action
        properties = {
            "@type": "CreateAction",
            "instrument": id_ify(notebook.id),
            "actionStatus": {"@id": "http://schema.org/CompletedActionStatus"},
            "name": f"Run of notebook: {notebook.id.split('/')[-1]}",
        }

        if query:
            properties["query"] = query

    # Set endDate to latest file modification date
    properties["endDate"] = last_date

    # Add or update action
    action_new = crate.add(ContextEntity(crate, action_id, properties=properties))

    # Add input files to action
    for input in input_files:
        action_new.append_to("object", input)

    # Add output files to action
    for output in output_files:
        action_new.append_to("result", output)

def add_example_entities(crate, examples):
    for example in examples:
        example_props = {
            "@id": example["url"],
            "@type": "CreativeWork",
            "name": example["name"],
            "url": example["url"]
        }
        add_context_entity(crate, example_props)


def creates_data(data_repo, notebook_metadata):
    """
    Check to see if a notebook creates a data file.
    """
    if data_repo:
        for action in notebook_metadata["action"]:
            for result in action["result"]:
                if data_repo in result["url"]:
                    return True
    return False


def add_notebook(crate, notebook, data_repo, gw_url):
    """Adds notebook information to an ROCRate.

    Parameters:
        crate: The rocrate to update.
        notebook: The notebook to add to the rocrate
    """
    # Get the crate root
    root = crate.get("./").properties()

    # Extract embedded metadata from the notebook
    notebook_metadata = extract_notebook_metadata(
        notebook,
        {
            "name": notebook.name,
            "author": [],
            "description": "",
            "action": [],
            "mainEntityOfPage": "",
            "workExample": [],
            "category": "",
            "position": 0
        },
    )
    if not notebook_metadata:
        return
    # print(notebook.name)
    has_data = creates_data(data_repo, notebook_metadata)

    # If this is a data repo crate change nb ids to full urls
    if has_data:
        repo = Repo(".")
        repo_url = repo.git.config("--get", "remote.origin.url").replace(".git", "/")
        gh_branch = get_default_gh_branch(repo_url)
        nb_id = f"{repo_url}blob/{gh_branch}/{notebook.name}"
        nb_url = nb_id
    else:
        repo_url = root["url"]
        gh_branch = get_default_gh_branch(repo_url)
        nb_id = notebook
        nb_url = f"{repo_url}blob/{gh_branch}/{notebook.name}"

    # If this is a data repo crate only add notebooks that generate data
    if not data_repo or has_data:
        # Check if this notebook is already in the crate
        nb_current = crate.get(notebook.name)

        # If there's an entry for this notebook, we'll update it
        if nb_current:
            # Get current properties of the notebook
            properties = nb_current.properties()

            # If details have changed in notebook metadata they should be updated in the crate
            properties.update(
                {
                    "name": notebook_metadata["name"],
                    "description": notebook_metadata["description"],
                }
            )
        else:
            # Default properties for a new notebook
            properties = {
                "@type": ["File", "SoftwareSourceCode"],
                "name": notebook_metadata["name"],
                "description": notebook_metadata["description"],
                "programmingLanguage": id_ify(PYTHON["@id"]),
                "encodingFormat": "application/x-ipynb+json",
                "conformsTo": id_ify(
                    "https://purl.archive.org/textcommons/profile#Notebook"
                ),
                "codeRepository": repo_url,
                "url": nb_url,
                "category": notebook_metadata["category"],
                "position": notebook_metadata["position"]
            }

            if doc_url := notebook_metadata.get("mainEntityOfPage"):
                add_gw_page_link(crate, doc_url)
                properties["mainEntityOfPage"] = id_ify(doc_url)

        nb_examples = notebook_metadata.get("workExample", [])
        add_example_entities(crate, nb_examples)
        properties["workExample"] = id_ify([e["url"] for e in nb_examples])


        # Add input files from 'object' property of actions
        #nb_inputs = [a["object"] for a in notebook_metadata.get("action", [])]
        #input_files = add_files(crate, nb_inputs, data_repo)

        # Add output files from 'result' property
        #nb_outputs = [a["result"] for a in notebook_metadata.get("action", [])]
        #output_files = add_files(crate, nb_outputs, data_repo)

        # Add or update the notebook entity
        # (if there's an existing entry it will be overwritten)
        nb_new = crate.add_file(nb_id, properties=properties)

        # Add a CreateAction that links the notebook run with the input and output files
        for index, action in enumerate(notebook_metadata.get("action", [])):
            local_path = action.get("local_path", ".")
            if not data_repo or data_repo in action.get("result", [])[0]["url"]:
                # print(action)
                input_files = add_files(crate, action, "object", gw_url, data_repo, local_path)
                output_files = add_files(crate, action, "result", gw_url, data_repo, local_path)
                add_action(crate, nb_new, input_files, output_files, action.get("query", ""), index, local_path)
                if data_repo:
                    if dataset_gw_page := action.get("mainEntityOfPage"):
                        crate.update_jsonld({"@id": "./", "mainEntityOfPage": id_ify(dataset_gw_page)})
                        add_gw_page_link(crate, dataset_gw_page)
                    if dataset_description := action.get("description"):
                        crate.update_jsonld({"@id": "./", "description": dataset_description})
                    dataset_examples = action.get("workExample", [])
                    current_examples = root.get("workExample", [])
                    crate.update_jsonld({"@id": "./", "workExample": id_ify([e["url"] for e in dataset_examples]) + current_examples})
                    add_example_entities(crate, dataset_examples)
                
        # If the notebook has author info, add people to crate
        if notebook_metadata["author"]:
            # Add people referenced in notebook metadata
            persons = add_people(crate, notebook_metadata["author"])

        # Otherwise add crate root authors to notebook
        else:
            persons = root["author"]

        # If people are not already attached to notebook, append them to the author property
        for person in persons:
            if (
                nb_current and person not in nb_current.get("author", [])
            ) or not nb_current:
                nb_new.append_to("author", person)


def remove_deleted_files(crate, data_paths):
    """
    Loops through File entities checking to see if they exist in local filesystem.
    If they don't then they're removed from the crate.
    """
    file_ids = []
    for action in crate.get_by_type("CreateAction"):
        for file_type in ["object", "result"]:
            try:
                file_ids += [o["@id"] for o in action.properties()[file_type]]
            except KeyError:
                pass

    # Loop through File entities
    for f in crate.get_by_type("File"):
        found = False
        for dpath in data_paths:
            if  Path(dpath, f.id).exists():
                found = True
        # If they don't exist and they're not urls, then delete
        if not found and not f.id.startswith("http"):
            crate.delete(f)
        # If they're not referenced in CreateActions then delete
        if f.id not in file_ids and not f.id.endswith(".ipynb"):
            crate.delete(f)


def remove_unreferenced_authors(crate):
    """
    Compares the current Person entities with those referenced by the "author" property.
    Removes Person entities that are not authors.
    """
    # Get authors from root
    authors = crate.get("./")["author"]

    # Loop through all File entities, extracting authors
    for file_ in crate.get_by_type("File"):
        try:
            authors += file_["author"]
        except KeyError:
            pass
    # Loop though Person entities checking against authors
    for person in crate.get_by_type("Person"):
        # If Person is not an author, delete them
        if not person in authors:
            crate.delete(person)


def add_update_action(crate, version):
    """
    Adds an UpdateAction to the crate when the repo version is updated.
    """
    # Create an id for the action using the version number
    action_id = f"create_version_{version.replace('.', '_')}"

    # Set basic properties for action
    properties = {
        "@type": "UpdateAction",
        "endDate": datetime.datetime.now().strftime("%Y-%m-%d"),
        "name": f"Create version {version}",
        "actionStatus": {"@id": "http://schema.org/CompletedActionStatus"},
    }

    # Create entity
    crate.add(ContextEntity(crate, action_id, properties=properties))


def add_context_entity(crate, entity):
    """
    Adds a ContextEntity to the crate.

    Parameters:
        crate: the current ROCrate
        entity: A JSONLD ready dict containing "@id" and "@type" values
    """
    crate.add(ContextEntity(crate, entity["@id"], properties=entity))

def add_gw_page_link(crate, doc_url):
    gw_title = get_page_title(doc_url)
    nd_docs = {
        "@id": doc_url,
        "@type": "CreativeWork",
        "name": gw_title,
        "isPartOf": id_ify("https://glam-workbench.net"),
        "url": doc_url
    }
    add_context_entity(crate, nd_docs)

def get_page_title(url):
    response = requests.get(url)
    if response.ok:
        soup = BeautifulSoup(response.text, features="lxml")
        return soup.title.string.split(" - ")[0].strip()

def get_gw_docs(repo_name):
    """ """
    gw_url = f"https://glam-workbench.net/{repo_name}"
    gw_title = get_page_title(gw_url)
    if gw_title:
        return {"url": gw_url, "title": gw_title}


def update_crate(version, data_repo, notebooks):
    """Creates a parent crate in the supplied directory.

    Parameters:
        version: The version of the repository
        notebooks: The notebooks to include in the crate
    """
    repo = Repo(".")
    code_repo_url = repo.git.config("--get", "remote.origin.url").replace(".git", "/")

    # Set some defaults based on whether this is a code or data repo
    if data_repo:
        crate_source = "./data-rocrate"
        repo_url = data_repo
        description = "A GLAM Workbench dataset"
    else:
        crate_source = "./"
        repo_url = code_repo_url
        description = "A GLAM Workbench repository"

    repo_name = repo_url.strip("/").split("/")[-1]
    code_repo_name = code_repo_url.strip("/").split("/")[-1]
    # Get links to the GLAM Workbench
    gw_link = get_gw_docs(repo_name)
    if gw_link:
        gw_url = gw_link.get("url")
    else:
        gw_url = None
    # Load existing crate
    try:
        crate = ROCrate(source=crate_source)

    # If there's not an existing crate, create a new one
    except (ValueError, FileNotFoundError):
        crate = ROCrate()

        crate.update_jsonld(
            {
                "@id": "./",
                "@type": "Dataset",
                "name": repo_name,
                "description": description,
                "url": repo_url,
                "author": id_ify([a["orcid"] for a in DEFAULT_AUTHORS]),
            }
        )

        if gw_link:
            gw_url = gw_link.get("url")
            crate.update_jsonld(
                {"@id": "./", "mainEntityOfPage": id_ify(gw_url)}
            )
            gw_docs = {
                "@id": gw_url,
                "@type": "CreativeWork",
                "name": gw_link["title"],
                "isPartOf": id_ify("https://glam-workbench.net/"),
                "url": gw_url,
            }
            add_context_entity(crate, gw_docs)
            add_context_entity(crate, GLAM_WORKBENCH)

        add_people(crate, DEFAULT_AUTHORS)

    # If this is a data repo crate, create a link back to code repo
    if data_repo:
        crate.update_jsonld(
            {
                "@id": "./",
                "isBasedOn": id_ify(code_repo_url),
                "distribution": id_ify(f"{repo_url.rstrip('/')}/archive/refs/heads/main.zip")
            }
        )
        source_repo = {
            "@id": code_repo_url,
            "@type": "Dataset",
            "name": code_repo_name,
            "url": code_repo_url,
        }
        add_context_entity(crate, source_repo)

        download = {
            "@id": f"{ repo_url.rstrip('/')}/archive/refs/heads/main.zip",
            "@type": "DataDownload",
            "name": "Download repository as zip",
            "url": f"{ repo_url.rstrip('/')}/archive/refs/heads/main.zip",
        }
        add_context_entity(crate, download)

    # If this is a new version, change version number and add UpdateAction
    if version:
        crate.update_jsonld(
            {
                "@id": "./",
                "version": version,
                "datePublished": datetime.datetime.now().strftime("%Y-%m-%d"),
            }
        )
        add_update_action(crate, version)

    # Add licence to root
    crate.license = id_ify(DEFAULT_LICENCE["@id"])
    add_context_entity(crate, DEFAULT_LICENCE)

    # Add licence to metadata
    crate.update_jsonld(
        {
            "@id": "ro-crate-metadata.json",
            "license": id_ify(METADATA_LICENCE["@id"]),
        }
    )
    add_context_entity(crate, METADATA_LICENCE)
    add_context_entity(crate, NKC_LICENCE)
    add_context_entity(crate, CNE_LICENCE)

    # Add Python for programming language
    add_context_entity(crate, PYTHON)

    # Process notebooks
    for notebook in notebooks:
        add_notebook(crate, notebook, data_repo, gw_url)

    # Remove files from crate if they're no longer in the repo
    # remove_deleted_files(crate, data_paths)

    # Remove authors from crate if they're not referenced by any entities
    remove_unreferenced_authors(crate)

    # Save the crate
    crate.write(crate_source)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--version", type=str, help="New version number", required=False
    )
    parser.add_argument("--data-repo", type=str, default="", required=False)
    args = parser.parse_args()
    main(args.version, args.data_repo)
