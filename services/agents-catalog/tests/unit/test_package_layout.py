import importlib
from pathlib import Path

import pytest

PACKAGES = (
    "agents_catalog",
    "agents_catalog.domain",
    "agents_catalog.application",
    "agents_catalog.infrastructure",
    "agents_catalog.api",
)
MODULES = ("agents_catalog.settings", "agents_catalog.main")
CATALOG_FOLDERS = ("roles", "prompts", "characters", "evals")
CATALOG_ROOT = Path(__file__).resolve().parents[2] / "catalog"


@pytest.mark.parametrize("name", PACKAGES)
def test_layered_package_exists(name: str) -> None:
    module = importlib.import_module(name)

    assert module.__file__ is not None
    assert module.__file__.endswith("__init__.py")


@pytest.mark.parametrize("name", MODULES)
def test_entry_module_exists(name: str) -> None:
    assert importlib.import_module(name).__file__ is not None


@pytest.mark.parametrize("folder", CATALOG_FOLDERS)
def test_catalog_source_folder_is_tracked(folder: str) -> None:
    assert (CATALOG_ROOT / folder / ".gitkeep").is_file()
