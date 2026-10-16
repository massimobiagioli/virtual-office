import json
from pathlib import Path

import pytest

from check_coverage import main


def file_summary(
    statements: int, covered: int, branches: int = 0, covered_branches: int = 0
) -> dict[str, object]:
    return {
        "summary": {
            "num_statements": statements,
            "covered_lines": covered,
            "num_branches": branches,
            "covered_branches": covered_branches,
        }
    }


def write_report(folder: Path, files: dict[str, dict[str, object]]) -> Path:
    report = folder / "coverage.json"
    report.write_text(json.dumps({"files": files}), encoding="utf-8")
    return report


def test_passes_when_every_layer_meets_its_threshold(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(
        tmp_path,
        {
            "src/virtual_office/domain/kanban/card.py": file_summary(100, 95),
            "src/virtual_office/application/commands.py": file_summary(10, 9),
            "src/virtual_office/api/app.py": file_summary(10, 7),
            "src/virtual_office/main.py": file_summary(5, 5),
        },
    )

    assert main([str(report), "--package", "virtual_office"]) == 0
    assert "domain: 95.0 % (required 95 %)" in capsys.readouterr().out


def test_fails_when_the_domain_is_below_95_percent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path, {"src/virtual_office/domain/card.py": file_summary(100, 94)})

    assert main([str(report), "--package", "virtual_office"]) == 1
    assert "FAIL domain: 94.0 % (required 95 %)" in capsys.readouterr().out


def test_fails_when_the_application_is_below_90_percent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path, {"src/catalog/application/roles.py": file_summary(10, 8)})

    assert main([str(report), "--package", "catalog"]) == 1
    assert "FAIL application: 80.0 % (required 90 %)" in capsys.readouterr().out


def test_fails_when_another_layer_is_below_70_percent(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path, {"src/catalog/infrastructure/db.py": file_summary(10, 6)})

    assert main([str(report), "--package", "catalog"]) == 1
    assert "FAIL infrastructure: 60.0 % (required 70 %)" in capsys.readouterr().out


def test_top_level_modules_count_as_other_code(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path, {"src/catalog/settings.py": file_summary(10, 6)})

    assert main([str(report), "--package", "catalog"]) == 1
    assert "FAIL catalog (top-level modules): 60.0 % (required 70 %)" in capsys.readouterr().out


def test_branches_count_together_with_lines(tmp_path: Path) -> None:
    # 19 of 20 lines (95 %) but 0 of 2 branches: (19 + 0) / (20 + 2) = 86.4 % < 95 %.
    report = write_report(
        tmp_path, {"src/virtual_office/domain/card.py": file_summary(20, 19, 2, 0)}
    )

    assert main([str(report), "--package", "virtual_office"]) == 1


def test_files_of_other_packages_are_ignored(tmp_path: Path) -> None:
    report = write_report(
        tmp_path,
        {
            "tests/unit/test_card.py": file_summary(10, 0),
            "src/virtual_office/domain/card.py": file_summary(10, 10),
        },
    )

    assert main([str(report), "--package", "virtual_office"]) == 0


def test_fails_when_no_file_belongs_to_the_package(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    report = write_report(tmp_path, {"src/virtual_office/domain/card.py": file_summary(10, 10)})

    assert main([str(report), "--package", "virtual_ofice"]) == 1
    assert "no measured file belongs to package 'virtual_ofice'" in capsys.readouterr().out


def test_a_threshold_is_not_reached_by_rounding(tmp_path: Path) -> None:
    # 9496 of 10000 lines = 94.96 %, displayed as 95.0 % but below the 95 % domain threshold.
    report = write_report(
        tmp_path, {"src/virtual_office/domain/card.py": file_summary(10000, 9496)}
    )

    assert main([str(report), "--package", "virtual_office"]) == 1
