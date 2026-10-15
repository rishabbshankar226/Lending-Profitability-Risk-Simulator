"""Format-specific generation from immutable applied snapshots."""

from collections.abc import Callable
from functools import partial
from typing import Literal, overload

import streamlit as st

from lending_simulator import MODEL_VERSION
from lending_simulator.data import Dataset
from lending_simulator.decisions import select_strategy
from lending_simulator.exports import scenario_workbook
from lending_simulator.presentation import csv_package, decision_brief
from lending_simulator.types import ModelResult


@st.cache_data(max_entries=12, show_spinner=False)
def cached_export(
    kind: str, run_id: str, model_version: str, dataset_hash: str,
    _selected: ModelResult, _results: tuple[ModelResult, ...], _dataset: Dataset,
) -> str | bytes:
    if run_id != _selected.run_id or model_version != MODEL_VERSION or dataset_hash != _dataset.dataset_hash:
        raise ValueError('Export identity does not match its captured inputs.')
    if kind == 'brief':
        return decision_brief(_selected, _results)
    if kind == 'csv':
        return csv_package(_selected, _dataset)
    if kind == 'workbook':
        return scenario_workbook(_selected, _results, _dataset)
    raise ValueError('Unknown export format.')


@overload
def download_factory(kind: Literal['brief'], selected: ModelResult, results: tuple[ModelResult, ...], dataset: Dataset) -> Callable[[], str]: ...


@overload
def download_factory(kind: Literal['csv', 'workbook'], selected: ModelResult, results: tuple[ModelResult, ...], dataset: Dataset) -> Callable[[], bytes]: ...


@overload
def download_factory(kind: str, selected: ModelResult, results: tuple[ModelResult, ...], dataset: Dataset) -> Callable[[], str | bytes]: ...


def download_factory(
    kind: str, selected: ModelResult, results: tuple[ModelResult, ...], dataset: Dataset,
) -> Callable[[], str | bytes]:
    if selected not in results or selected.dataset_hash != dataset.dataset_hash:
        raise ValueError('Export must use one complete applied result bundle and its dataset.')
    select_strategy(results)
    if kind not in ('brief', 'csv', 'workbook'):
        raise ValueError('Unknown export format.')
    return partial(cached_export, kind, selected.run_id, MODEL_VERSION, dataset.dataset_hash,
                   selected, results, dataset)
