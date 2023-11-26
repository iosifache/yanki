# Yanki

## Description

Yanki is a vocabulary manager that converts words and expressions stored in a YAML file into multiple Anki decks.

## Usage

1. Install the package.
2. Create a YAML file named `<yaml_filename>` with entries respecting the structure:

    ```yaml
    "<word_or_expression>":
    language: <language>
    meaning: <meaning>
    date: <date_when_the_entry_was_added>
    ```

3. Convert the YAML file: `poetry run yanki <yaml_filename> <output_folder_for_decks>`
