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


def test_skill_name_longer_than_the_name_limit_is_reported(conforming_repo):
    rename_skill(conforming_repo, "ba0918-alpha", "ba0918-" + "a" * 58)

    assert rules_of(validate.validate_repository(conforming_repo)) == ["name-length"]


def test_skill_name_at_exactly_the_name_limit_is_accepted(conforming_repo):
    at_limit = "ba0918-" + "a" * 57
    rename_skill(conforming_repo, "ba0918-alpha", at_limit)

    assert len(at_limit) == 64
    assert validate.validate_repository(conforming_repo) == []


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
    "escaping_link",
    [
        "[shared](..\\ba0918-alpha\\SKILL.md)",
        "[shared](/home/someone/dotfiles/ai/shared/design-principles.md)",
        "[shared](~/.claude/skills/ba0918-alpha/SKILL.md)",
        "[shared](C:\\skills\\ba0918-alpha\\SKILL.md)",
    ],
)
def test_link_target_outside_the_skill_directory_is_reported(
    conforming_repo, escaping_link
):
    target = conforming_repo / "skills" / "ba0918-beta" / "SKILL.md"
    target.write_text(target.read_text() + f"\nSee {escaping_link}.\n")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "external-reference"
    ]


def test_reference_definition_pointing_outside_the_skill_directory_is_reported(
    conforming_repo,
):
    target = conforming_repo / "skills" / "ba0918-beta" / "SKILL.md"
    target.write_text(
        target.read_text()
        + "\n[shared]: /home/someone/dotfiles/ai/shared/design-principles.md\n"
    )

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "external-reference"
    ]


def test_prose_naming_an_installation_path_is_not_reported_as_a_reference(
    conforming_repo,
):
    target = conforming_repo / "skills" / "ba0918-beta" / "SKILL.md"
    target.write_text(
        target.read_text()
        + "\nSkills are installed into `~/.claude/skills/` or /usr/share/skills.\n"
    )

    assert validate.validate_repository(conforming_repo) == []


def test_link_to_an_external_url_is_accepted(conforming_repo):
    target = conforming_repo / "skills" / "ba0918-beta" / "SKILL.md"
    target.write_text(
        target.read_text() + "\nSee the [specification](https://agentskills.io).\n"
    )

    assert validate.validate_repository(conforming_repo) == []


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


def test_frontmatter_value_quoted_only_at_its_edges_is_reported(conforming_repo):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    kept = [
        'description: "Baseline skill" 日本語キーワード: "正常系"'
        if line.startswith("description:")
        else line
        for line in skill_md.read_text().splitlines()
    ]
    skill_md.write_text("\n".join(kept))

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "frontmatter-unquoted-colon"
    ]


@pytest.mark.parametrize("block_indicator", ["|", ">", "|-", ">-", "|+", ">2"])
def test_description_written_as_a_block_scalar_is_reported(
    conforming_repo, block_indicator
):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    overlong = "d" * 2000
    kept = [
        f"description: {block_indicator}\n  {overlong}"
        if line.startswith("description:")
        else line
        for line in skill_md.read_text().splitlines()
    ]
    skill_md.write_text("\n".join(kept))

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "frontmatter-blockscalar"
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


def add_escaping_reference(repo):
    """Append an escaping link to a fixture file and return its 1-based line number."""
    target = repo / "skills" / "ba0918-beta" / "references" / "notes.md"
    text = target.read_text()
    target.write_text(text + "\nSee [shared](../ba0918-alpha/SKILL.md).\n")
    return len(text.splitlines()) + 2


def test_reference_violation_carries_the_file_and_line_it_was_found_on(conforming_repo):
    line_number = add_escaping_reference(conforming_repo)

    [violation] = validate.validate_repository(conforming_repo)

    assert (violation.path, violation.line) == (
        "skills/ba0918-beta/references/notes.md",
        line_number,
    )


def test_frontmatter_violation_carries_the_file_and_line_it_was_found_on(
    conforming_repo,
):
    skill_md = conforming_repo / "skills" / "ba0918-alpha" / "SKILL.md"
    kept = [
        "description: Baseline skill. 日本語キーワード: 正常系"
        if line.startswith("description:")
        else line
        for line in skill_md.read_text().splitlines()
    ]
    skill_md.write_text("\n".join(kept))

    [violation] = validate.validate_repository(conforming_repo)

    assert (violation.path, violation.line) == ("skills/ba0918-alpha/SKILL.md", 3)


def test_command_line_run_prints_a_located_violation_as_path_and_line(
    conforming_repo, capsys
):
    line_number = add_escaping_reference(conforming_repo)

    validate.main([str(conforming_repo)])

    assert (
        f"skills/ba0918-beta/references/notes.md:{line_number}: external-reference: "
        in capsys.readouterr().out
    )


def subjects_of(violations):
    return sorted((v.skill, v.rule) for v in violations)


@pytest.mark.parametrize(
    "manifest_json",
    [
        '[]',
        '{"plugins": 5}',
        '{"plugins": "./skills/ba0918-alpha"}',
        '{"plugins": {"not": "a list"}}',
        '{"plugins": ["not a mapping"]}',
        '{"plugins": [{"skills": 5}]}',
        '{"plugins": [{"skills": [7]}]}',
        '{"plugins": [{"skills": [null]}]}',
    ],
)
def test_structurally_invalid_manifest_is_reported_without_crashing(
    conforming_repo, manifest_json
):
    (conforming_repo / ".claude-plugin" / "marketplace.json").write_text(manifest_json)

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "marketplace-unreadable"
    ]


def test_manifest_entry_using_windows_separators_is_reported_once(conforming_repo):
    edit_manifest(conforming_repo, "./skills/ba0918-alpha", ".\\\\skills\\\\ba0918-alpha")

    assert rules_of(validate.validate_repository(conforming_repo)) == ["marketplace-path"]


def test_manifest_entry_with_a_bad_path_is_not_also_reported_as_an_orphan(
    conforming_repo,
):
    edit_manifest(conforming_repo, "./skills/ba0918-alpha", "./skills/deep/ba0918-ghost")

    assert subjects_of(validate.validate_repository(conforming_repo)) == [
        ("ba0918-alpha", "marketplace-missing"),
        ("ba0918-ghost", "marketplace-path"),
    ]


@pytest.mark.parametrize(
    "removed",
    ['"name": "fixture-marketplace",', '"name": "fixture-rules",', '"source": "./",'],
)
def test_manifest_missing_an_identity_field_is_reported(conforming_repo, removed):
    edit_manifest(conforming_repo, removed, "")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "marketplace-metadata"
    ]


def edit_file(repo, relative_path, old, new):
    target = repo / relative_path
    target.write_text(target.read_text().replace(old, new))


def test_plugin_manifest_version_disagreeing_with_the_canonical_one_is_reported(
    conforming_repo,
):
    edit_file(
        conforming_repo, ".claude-plugin/plugin.json", '"version": "0.1.0"', '"version": "0.2.0"'
    )

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "version-sync-plugin"
    ]


def test_package_manifest_version_disagreeing_with_the_canonical_one_is_reported(
    conforming_repo,
):
    edit_file(conforming_repo, "package.json", '"version": "0.1.0"', '"version": "0.2.0"')

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "version-sync-package"
    ]


def test_latest_changelog_release_disagreeing_with_the_canonical_version_is_reported(
    conforming_repo,
):
    edit_file(conforming_repo, "CHANGELOG.md", "## [0.1.0]", "## [0.2.0]")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "version-sync-changelog"
    ]


def test_changelog_version_violation_carries_the_heading_it_was_found_on(
    conforming_repo,
):
    edit_file(conforming_repo, "CHANGELOG.md", "## [0.1.0]", "## [0.2.0]")

    [violation] = validate.validate_repository(conforming_repo)

    assert (violation.path, violation.line) == ("CHANGELOG.md", 5)


def test_changelog_holding_only_an_unreleased_section_is_accepted(conforming_repo):
    (conforming_repo / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- Something not released yet.\n"
    )

    assert validate.validate_repository(conforming_repo) == []


@pytest.mark.parametrize(
    "absent_manifest", [".claude-plugin/plugin.json", "package.json"]
)
def test_repository_not_shipping_a_channel_manifest_is_accepted(
    conforming_repo, absent_manifest
):
    (conforming_repo / absent_manifest).unlink()

    assert validate.validate_repository(conforming_repo) == []


@pytest.mark.parametrize(
    "unreadable_text", ["{ not json", "[]", '"a string, not an object"']
)
@pytest.mark.parametrize(
    "manifest_path, rule",
    [
        (".claude-plugin/plugin.json", "plugin-manifest-unreadable"),
        ("package.json", "package-manifest-unreadable"),
    ],
)
def test_channel_manifest_that_is_shipped_but_unreadable_is_reported(
    conforming_repo, manifest_path, rule, unreadable_text
):
    (conforming_repo / manifest_path).write_text(unreadable_text)

    assert rules_of(validate.validate_repository(conforming_repo)) == [rule]


def test_unreadable_channel_manifest_violation_names_the_file_without_a_line(
    conforming_repo,
):
    (conforming_repo / "package.json").write_text("{ not json")

    [violation] = validate.validate_repository(conforming_repo)

    assert (violation.path, violation.line) == ("package.json", None)


def test_repository_declaring_versions_without_a_canonical_one_is_reported(
    conforming_repo,
):
    """A missing canonical version is drift, because it silences every sync rule.

    The other three rules all compare against the canonical version, so losing
    it while the channels still declare versions would turn the whole guarantee
    off without a word.
    """
    edit_manifest(conforming_repo, '"version": "0.1.0",', "")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "version-sync-canonical"
    ]


def test_repository_declaring_no_version_anywhere_is_accepted(conforming_repo):
    """A repository that has not released names no version to be checked."""
    edit_manifest(conforming_repo, '"version": "0.1.0",', "")
    edit_file(conforming_repo, ".claude-plugin/plugin.json", '"version": "0.1.0",', "")
    edit_file(conforming_repo, "package.json", '"version": "0.1.0",', "")
    (conforming_repo / "CHANGELOG.md").write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Added\n\n- Nothing released yet.\n"
    )

    assert validate.validate_repository(conforming_repo) == []


def test_repository_without_a_skills_directory_reports_the_listed_skills_as_orphans(
    conforming_repo,
):
    shutil.rmtree(conforming_repo / "skills")

    assert rules_of(validate.validate_repository(conforming_repo)) == [
        "marketplace-orphan",
        "marketplace-orphan",
    ]
