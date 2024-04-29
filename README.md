# Substack to note

A simple Python script that converts a Substack export to a WXR (WordPress eXtended RSS) file to be imported by [note](note.com).  
It will also download any images inside the posts and save them in the output directory.

## Preqrequisites

- Python 3

## Installation

1. Install Python.
1. Clone the repository.
    ```sh
    git clone git@github.com:diskshima/substack-to-note.git
    ```
1. Install the required packages.
    ```sh
    cd substack-to-note
    pip install -r requirements.txt
    ```

## Usage

1. Follow the [instructions here](https://support.substack.com/hc/en-us/articles/360037466012-How-do-I-export-my-posts) and download your Substack data.
2. Extract the downloaded zip file.
3. Run the script with the path to the extracted folder as an argument.
    ```bash
    python main.py -i path/to/extracted/directory -o path/to/output/directory
    ```

Your WXR file will be saved in the output directory together with the images.

## Development

A few things to keep in mind if you want to contribute to this project:

- Please use [Poetry](https://python-poetry.org/) to manage dependencies.
- Please run [ruff](https://docs.astral.sh/ruff/) before committing to ensure code quality.
    ```sh
    poetry run ruff format
    ```
- Please export the requirements after adding a new package.
    ```sh
    poetry export -f requirements.txt --output requirements.txt
    ```
- Please run the tests before committing.
    ```sh
    poetry run python test.py
    ```
