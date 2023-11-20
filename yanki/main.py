"""Dummy source file."""

import random
import typing
from dataclasses import dataclass

import genanki
import yaml

DATA_FILE = "data.yaml"


@dataclass
class Entry:
    name: str
    entry_type: str
    meaning: str


@dataclass
class Deck:
    name: str
    entries: typing.List[Entry]


def read_data() -> dict:
    with open(DATA_FILE) as file:
        content = file.read()
        return yaml.safe_load(content)


def get_notes(data: dict) -> typing.Generator[Entry, None, None]:
    for key, value in data.items():
        yield Entry(key, value["type"], value["meaning"])


def generate_decks(entries: typing.List[Entry]) -> typing.List[Deck]:
    decks: dict[str, Deck] = {}
    for entry in entries:
        parent_deck = decks.get(entry.entry_type, Deck(entry.entry_type, []))
        parent_deck.entries.append(entry)

        decks[entry.entry_type] = parent_deck

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


def dump_decks(model: genanki.Model, decks: typing.List[Deck]) -> None:
    for deck in decks:
        dump_deck(model, deck)


def dump_deck(model: genanki.Model, deck: Deck) -> None:
    out_deck = genanki.Deck(generate_id(), deck.name)

    print(deck.name, deck.entries)

    for entry in deck.entries:
        note = genanki.Note(model=model, fields=[entry.name, entry.meaning])
        out_deck.add_note(note)

    # Save the deck to an Anki package (*.apkg) file
    genanki.Package(out_deck).write_to_file(f"{deck.name}.apkg")


def main() -> None:
    """Run the main functionality."""
    model = define_model()

    data = read_data()
    notes = list(get_notes(data))
    decks = generate_decks(notes)
    dump_decks(model, decks)


if __name__ == "__main__":
    main()
