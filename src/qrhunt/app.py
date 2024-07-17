import csv
import os
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

import art  # type: ignore
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.timer import Timer
from textual.widgets import Button, Footer, Label, ListItem, ListView, RichLog, Static, TextArea

from .animals import ANIMAL_RE, ANIMALS_BY_NAME, Animal


@dataclass(frozen=True)
class LogEntry:
    time: float
    points: int
    animals: list[str]

    def row(self) -> list[str]:
        return [f"{self.time:.02f}", str(self.points), " ".join(self.animals)]


class TimeDisplay(Static):
    """A widget to display elapsed time."""

    start_time = reactive(time.monotonic)
    total = reactive(0.0)

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_timer = self.set_interval(1 / 60, self.update_time, pause=True)

    def update_time(self) -> None:
        """Method to update time to current."""
        self.total = time.monotonic() - self.start_time

    def watch_total(self, time: float) -> None:
        """Called when the time attribute changes."""
        self.update(art.text2art(f"{time:5.2f}", font="tarty1"))

    def start(self) -> None:
        """Method to start (or resume) time updating."""
        self.start_time = time.monotonic()
        self.update_timer.resume()

    def stop(self) -> None:
        """Method to stop the time display updating."""
        self.update_timer.pause()
        self.total = time.monotonic() - self.start_time

    def reset(self) -> None:
        """Method to reset the time display to zero."""
        self.total = 0


class ContestantResult(Static):
    def __init__(self, time: timedelta, hits: list[Animal]) -> None:
        super().__init__()

        self.time = time
        self.hits = hits

    def compose(self) -> ComposeResult:
        total_points = sum(animal.points for animal in self.hits)
        yield Label(
            art.text2art(f"{self.time.total_seconds():.02f}s    {total_points:+}", font="tarty3"),
            classes="resulttime",
        )

        grouped_hits: dict[str, int] = defaultdict(int)

        for animal in self.hits:
            grouped_hits[animal.name] += 1

        for animal_name, count in sorted(grouped_hits.items(), key=lambda x: x[0]):
            animal = ANIMALS_BY_NAME[animal_name]
            sign = "+" if animal.points >= 0 else ""
            points = f"{sign}{animal.points*count}"
            yield Label(
                f"{count:>3}x - {animal.name:8} {points:>5}",
                classes="positive" if animal.points >= 0 else "negative",
            )


class HuntApp(App[None]):
    CSS_PATH = "app.tcss"

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+k", "clear_results", "Clear"),
    ]

    TEXT_DEBOUNCE = 0.3

    LOGS_DIR = "logs"

    def __init__(self) -> None:
        super().__init__()

        self.text_timer: Timer | None = None
        self.text_first_time = 0.0

        os.makedirs(self.LOGS_DIR, exist_ok=True, mode=0o755)

    def compose(self) -> ComposeResult:
        yield Horizontal(
            ListView(
                id="hits_list",
            ),
            Vertical(
                TimeDisplay(id="time"),
                Button("Start", variant="success", id="start_btn"),
                Button("Stop", variant="error", id="stop_btn", disabled=True),
                TextArea(id="input"),
                RichLog(),
            ),
        )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        time_display = self.query_one(TimeDisplay)
        if button_id == "start_btn":
            time_display.start()
            event.button.disabled = True
            self.query_one("#stop_btn", Button).disabled = False
        elif button_id == "stop_btn":
            time_display.stop()
            event.button.disabled = True
            self.query_one("#start_btn", Button).disabled = False

    def action_clear_results(self) -> None:
        time_display = self.query_one(TimeDisplay)
        time_display.stop()
        time_display.reset()

        self.query_one("#start_btn", Button).disabled = False
        self.query_one("#stop_btn", Button).disabled = True
        self.query_one("#hits_list", ListView).clear()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        if event.text_area.text == "":
            return

        if self.text_timer is not None:
            self.text_timer.reset()
        else:
            self.text_first_time = time.monotonic()
            self.text_timer = self.set_interval(self.TEXT_DEBOUNCE, self._process_input, repeat=1)

    def _write_log(self, entry: LogEntry) -> None:
        path = os.path.join(self.LOGS_DIR, date.today().isoformat() + ".csv")

        with open(path, "a") as f:
            writer = csv.writer(f)
            writer.writerow(entry.row())

    def _process_input(self) -> None:
        self.text_timer = None

        input = self.query_one("#input", TextArea)

        lines = input.text.splitlines()
        if len(lines) == 0:
            return

        time_display = self.query_one(TimeDisplay)
        total_time = timedelta(seconds=self.text_first_time - time_display.start_time)

        dedup: set[str] = set()
        hits: list[Animal] = []
        for line in lines:
            m = ANIMAL_RE.match(line)
            if not m:
                self.query_one(RichLog).write(f"failed to match '{line}'")
                continue

            if m.group(0) in dedup:
                continue
            dedup.add(m.group(0))

            animal = ANIMALS_BY_NAME.get(m.group(1))
            if not animal:
                self.query_one(RichLog).write(f"unknown animal '{line}'")
                continue
            hits.append(animal)

        self._write_log(
            LogEntry(
                total_time.total_seconds(), sum(a.points for a in hits), [a.name for a in hits]
            )
        )

        self.query_one("#hits_list", ListView).insert(
            0, (ListItem(ContestantResult(total_time, hits)),)
        )
        input.clear()
