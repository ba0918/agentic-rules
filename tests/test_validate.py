import shutil

import pytest

import validate


def rules_of(violations):
    return sorted(v.rule for v in violations)


def rename_skill(repo, old_name, new_name):
    """Rename a skill everywhere it is spelled, so only the new name is under test."""
    skills = repo / "skills"
    (skills / old_name).rename(skills / new_name)
    skill_md = skills / new_name / "SKILL.md"
    skill_md.write_text(
        skill_md.read_text().replace(f"name: {old_name}", f"name: {new_name}")
    )
    manifest = repo / ".claude-plugin" / "marketplace.json"
    manifest.write_text(
        manifest.read_text().replace(f"./skills/{old_name}", f"./skills/{new_name}")
    )


def test_repository_following_every_convention_reports_no_violations(conforming_repo):
    assert validate.validate_repository(conforming_repo) == []


def test_name_field_disagreeing_with_its_directory_name_is_reported(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    skill_md.write_text(
        skill_md.read_text().replace("name: ba0918-alpha", "name: ba0918-renamed")
    )

    assert rules_of(validate.validate_repository(conforming_repo)) == ["name-mismatch"]


def test_skill_name_missing_the_owner_prefix_is_reported(conforming_repo):
    rename_skill(conforming_repo, "ba0918-alpha", "alpha")

    assert rules_of(validate.validate_repository(conforming_repo)) == ["name-prefix"]


@pytest.mark.parametrize(
    "malformed_name",
    ["ba0918-Alpha", "ba0918--alpha", "ba0918-alpha-", "ba0918-alpha_one"],
)
def test_skill_name_outside_the_permitted_character_grammar_is_reported(
    conforming_repo, malformed_name
):
    rename_skill(conforming_repo, "ba0918-alpha", malformed_name)

    assert rules_of(validate.validate_repository(conforming_repo)) == ["name-charset"]


def test_skill_without_a_description_is_reported(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    kept = [
        line
        for line in skill_md.read_text().splitlines()
        if not line.startswith("description:")
    ]
    skill_md.write_text("\n".join(kept))

    assert rules_of(validate.validate_repository(conforming_repo)) == ["field-missing"]


def test_description_longer_than_the_frontmatter_limit_is_reported(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    overlong = "d" * 1025
    kept = [
        f"description: {overlong}" if line.startswith("description:") else line
        for line in skill_md.read_text().splitlines()
    ]
    skill_md.write_text("\n".join(kept))

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "description-length"
    ]


def test_skill_document_longer_than_the_line_limit_is_reported(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    padding = "\n".join(f"- filler line {n}" for n in range(501))
    skill_md.write_text(skill_md.read_text() + "\n" + padding + "\n")

    assert rules_of(validate.validate_repository(conforming_repo)) == ["line-limit"]


@pytest.mark.parametrize(
    "relative_path", ["SKILL.md", "references/notes.md"]
)
def test_reference_escaping_the_skill_directory_is_reported(
    conforming_repo, relative_path
):
    target = conforming_repo / "skills" / "ba0918-beta" / relative_path
    target.write_text(target.read_text() + "\nSee [shared](../ba0918-alpha/SKILL.md).\n")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "external-reference"
    ]


@pytest.mark.parametrize(
    "malformed_routing", ["sometimes", "required", "required:", "always:commit"]
)
def test_routing_value_outside_the_two_permitted_forms_is_reported(
    conforming_repo, malformed_routing
):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    skill_md.write_text(
        skill_md.read_text().replace(
            "ba0918-routing: always", f"ba0918-routing: {malformed_routing}"
        )
    )

    assert rules_of(validate.validate_repository(conforming_repo)) == ["routing-invalid"]


def test_skill_declaring_no_routing_is_accepted(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    kept = [
        line
        for line in skill_md.read_text().splitlines()
        if "ba0918-routing" not in line and line.strip() != "metadata:"
    ]
    skill_md.write_text("\n".join(kept))

    assert validate.validate_repository(conforming_repo) == []


def add_skill(repo, name):
    directory = repo / "skills" / name
    directory.mkdir()
    (directory / "SKILL.md").write_text(
        f'---\nname: {name}\ndescription: "An added skill. 日本語キーワード: 追加"\n---\n\n# {name}\n'
    )


def test_skill_absent_from_the_marketplace_manifest_is_reported(conforming_repo):
    add_skill(conforming_repo, "ba0918-unlisted")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "marketplace-missing"
    ]


def test_marketplace_entry_without_a_matching_skill_is_reported(conforming_repo):
    shutil.rmtree(conforming_repo / "skills" / "ba0918-beta")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "marketplace-orphan"
    ]


def test_skill_document_without_a_frontmatter_block_is_reported(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    skill_md.write_text("# Alpha\n\nNo frontmatter at all.\n")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "frontmatter-missing"
    ]


def test_command_line_run_on_a_conforming_repository_exits_zero(conforming_repo):
    assert validate.main([str(conforming_repo)]) == 0


def test_command_line_run_reports_each_violation_and_exits_nonzero(
    conforming_repo, capsys
):
    shutil.rmtree(conforming_repo / "skills" / "ba0918-beta")

    exit_code = validate.main([str(conforming_repo)])

    assert exit_code == 1
    assert "marketplace-orphan" in capsys.readouterr().out


def test_unquoted_frontmatter_value_containing_a_colon_is_reported(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    kept = [
        'description: Baseline skill. 日本語キーワード: 正常系'
        if line.startswith("description:")
        else line
        for line in skill_md.read_text().splitlines()
    ]
    skill_md.write_text("\n".join(kept))

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "frontmatter-unquoted-colon"
    ]


def edit_manifest(repo, old, new):
    manifest = repo / ".claude-plugin" / "marketplace.json"
    manifest.write_text(manifest.read_text().replace(old, new))


@pytest.mark.parametrize(
    "wrong_entry",
    ["./skil/ba0918-alpha", "ba0918-alpha", "/etc/ba0918-alpha", "./skills/nested/ba0918-alpha"],
)
def test_manifest_entry_not_pointing_into_the_skills_directory_is_reported(
    conforming_repo, wrong_entry
):
    edit_manifest(conforming_repo, "./skills/ba0918-alpha", wrong_entry)

    assert rules_of(validate.validate_repository(conforming_repo)) == ["marketplace-path"]


def test_skill_listed_twice_in_the_manifest_is_reported(conforming_repo):
    edit_manifest(
        conforming_repo,
        '"./skills/ba0918-alpha",',
        '"./skills/ba0918-alpha",\n        "./skills/ba0918-alpha",',
    )

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "marketplace-duplicate"
    ]


def test_unparseable_manifest_is_reported_as_unreadable(conforming_repo):
    (conforming_repo / ".claude-plugin" / "marketplace.json").write_text("{ not json")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "marketplace-unreadable"
    ]


def test_absent_manifest_is_reported_as_unreadable(conforming_repo):
    (conforming_repo / ".claude-plugin" / "marketplace.json").unlink()

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "marketplace-unreadable"
    ]


def test_skill_directory_without_a_skill_document_is_reported(conforming_repo):
    (conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md").unlink()

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "skill-md-missing"
    ]


def test_skill_without_a_name_field_is_reported(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    kept = [
        line for line in skill_md.read_text().splitlines() if not line.startswith("name:")
    ]
    skill_md.write_text("\n".join(kept))

    assert rules_of(validate.validate_repository(conforming_repo)) == ["field-missing"]


def test_skill_document_at_exactly_the_line_limit_is_accepted(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    lines = skill_md.read_text().splitlines()
    lines += [f"- filler line {n}" for n in range(500 - len(lines))]
    skill_md.write_text("\n".join(lines) + "\n")

    assert len(skill_md.read_text().splitlines()) == 500
    assert validate.validate_repository(conforming_repo) == []


def test_description_at_exactly_the_character_limit_is_accepted(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    at_limit = "d" * 1024
    kept = [
        f'description: "{at_limit}"' if line.startswith("description:") else line
        for line in skill_md.read_text().splitlines()
    ]
    skill_md.write_text("\n".join(kept))

    assert validate.validate_repository(conforming_repo) == []


def test_file_symlinked_outside_the_repository_is_not_read(conforming_repo, tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("content that would violate self-containment: ../elsewhere\n")
    link = conforming_repo / "skills" / "ba0918-beta" / "references" / "linked.md"
    link.symlink_to(outside)

    assert validate.validate_repository(conforming_repo) == []


def test_command_line_run_on_a_path_that_is_not_a_directory_exits_two(tmp_path):
    assert validate.main([str(tmp_path / "does-not-exist")]) == 2
