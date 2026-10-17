from pathlib import Path

import pytest

from check_frontend_pins import main

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]

STACK = """# Stack

## 3. Frontend (`frontend/`)

| Concern | Choice | Version | Notes |
| ------- | ------ | ------- | ----- |
| Build-time runtime | Node.js LTS "Krypton" | 24.22.0 | |
| Package manager | pnpm | 12.14.0 | |
| Framework | Vue | 3.5.44 | |
| **Office renderer** | **pixi.js** | 8.22.0 | |
| Unit/component tests | Vitest + @vitest/coverage-v8 | 5.0.5 | |
| Component test utils | @vue/test-utils | 2.5.1 | |

## 4. Graphics

| Concern | Choice | Version | Notes |
| ------- | ------ | ------- | ----- |
| Ignored | lodash | 4.17.21 | |
"""

PACKAGE = """{
  "packageManager": "pnpm@12.14.0",
  "engines": {"node": "24.22.0", "pnpm": "12.14.0"},
  "dependencies": {"vue": "3.5.44", "pixi.js": "8.22.0"},
  "devDependencies": {
    "vitest": "5.0.5",
    "@vitest/coverage-v8": "5.0.5",
    "@vue/test-utils": "2.5.1"
  }
}
"""


def write_repository(root: Path, package: str = PACKAGE) -> Path:
    (root / ".docs").mkdir()
    (root / ".docs" / "STACK.md").write_text(STACK, encoding="utf-8")
    (root / "frontend").mkdir()
    (root / "frontend" / "package.json").write_text(package, encoding="utf-8")
    return root


def test_the_repository_pins_match_the_stack() -> None:
    assert main(["--root", str(REPOSITORY_ROOT)]) == 0


def test_passes_when_every_pin_matches_the_stack(tmp_path: Path) -> None:
    assert main(["--root", str(write_repository(tmp_path))]) == 0


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ('"vue": "3.5.44"', '"vue": "^3.5.44"', "vue@^3.5.44: is not an exact version"),
        ('"vue": "3.5.44"', '"vue": "~3.5.44"', "vue@~3.5.44: is not an exact version"),
        (
            '"vue": "3.5.44"',
            '"vue": "3.5.43"',
            "vue@3.5.43: pins 3.5.43, STACK.md §3 says 3.5.44",
        ),
        (
            '"@vue/test-utils": "2.5.1"',
            '"@vue/test-utils": "2.5.1", "lodash": "4.17.21"',
            "lodash@4.17.21: is not listed in STACK.md §3",
        ),
        (
            '"pnpm@12.14.0"',
            '"pnpm@12.13.0"',
            "packageManager = 'pnpm@12.13.0': expected 'pnpm@12.14.0' (STACK.md §3 pnpm)",
        ),
        (
            '"node": "24.22.0"',
            '"node": ">=24"',
            "engines.node = '>=24': expected '24.22.0' (STACK.md §3 Node.js)",
        ),
        (
            '"pnpm": "12.14.0"}',
            '"pnpm": "12"}',
            "engines.pnpm = '12': expected '12.14.0' (STACK.md §3 pnpm)",
        ),
    ],
)
def test_fails_with_file_and_dependency(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], old: str, new: str, message: str
) -> None:
    assert old in PACKAGE
    root = write_repository(tmp_path, PACKAGE.replace(old, new))

    assert main(["--root", str(root)]) == 1
    assert f"frontend/package.json: {message}" in capsys.readouterr().out
