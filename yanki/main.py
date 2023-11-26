"""Converts a YAML into Anki decks."""

import os
import random
import sys
import typing
from dataclasses import dataclass

import genanki
import yaml


@dataclass
class Entry:
    name: str
    language: str
    entry_type: str | None
    meaning: str

    def get_parent_deck(self: "Entry") -> str:
        return self.entry_type if self.entry_type else self.language


@dataclass
class Deck:
    name: str
    entries: typing.List[Entry]


def read_data(filename: str) -> dict:
    with open(filename) as file:
        content = file.read()
        return yaml.safe_load(content)


def get_notes(data: dict) -> typing.Generator[Entry, None, None]:
    for key, value in data.items():
        yield Entry(
            key,
            value["language"],
            value.get("type", None),
            value["meaning"],
        )


def generate_decks(entries: typing.List[Entry]) -> typing.List[Deck]:
    decks: dict[str, Deck] = {}
    for entry in entries:
        parent_deck_name = entry.get_parent_deck()

        parent_deck = decks.get(parent_deck_name, Deck(parent_deck_name, []))
        parent_deck.entries.append(entry)

        decks[parent_deck_name] = parent_deck

    return list(decks.values())


def generate_id() -> int:
    return random.randrange(1 << 30, 1 << 31)


def define_model() -> genanki.Model:
    return genanki.Model(
        generate_id(),
        "Generic model",
        fields=[
            {"name": "Question"},
            {"name": "Answer"},
        ],
        templates=[
            {
                "name": "Card I",
                "qfmt": "{{Question}}",
                "afmt": "{{Answer}}",
            },
            {
                "name": "Card II",
                "qfmt": "{{Answer}}",
                "afmt": "{{Question}}",
            },
        ],
    )


def dump_decks(
    model: genanki.Model,
    decks: typing.List[Deck],
    output_folder: str,
) -> None:
    for deck in decks:
        dump_deck(model, deck, output_folder)


def dump_deck(model: genanki.Model, deck: Deck, output_folder: str) -> None:
    out_deck = genanki.Deck(generate_id(), deck.name)

    for entry in deck.entries:
        note = genanki.Note(model=model, fields=[entry.name, entry.meaning])
        out_deck.add_note(note)

    # Save the deck to an Anki package (*.apkg) file
    genanki.Package(out_deck).write_to_file(
        f"{output_folder}/{deck.name}.apkg",
    )


def main() -> None:
    """Run the main functionality."""
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} YAML_FILENAME OUTPUT_FOLDER")
        sys.exit(1)
    filename = sys.argv[1]
    output_folder = sys.argv[2]

    if not os.path.isfile(filename):
        print("The filename should point to an existent YAML file.")
        sys.exit(1)

    if not os.path.isdir(output_folder):
        print("The output folder should exist.")
        sys.exit(1)

    model = define_model()

    data = read_data(filename)
    notes = list(get_notes(data))
    decks = generate_decks(notes)
    dump_decks(model, decks, output_folder)


if __name__ == "__main__":
    main()
