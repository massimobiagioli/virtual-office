import importlib

import pytest

PACKAGES = (
    "virtual_office",
    "virtual_office.domain",
    "virtual_office.domain.shared",
    "virtual_office.domain.kanban",
    "virtual_office.domain.staff",
    "virtual_office.domain.intake",
    "virtual_office.domain.decisions",
    "virtual_office.application",
    "virtual_office.agents",
    "virtual_office.infrastructure",
    "virtual_office.api",
)


@pytest.mark.parametrize("name", PACKAGES)
def test_layered_package_exists(name: str) -> None:
    module = importlib.import_module(name)

    assert module.__file__ is not None
    assert module.__file__.endswith("__init__.py")
