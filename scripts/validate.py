#!/usr/bin/env python3
"""Validate that this repository's skills follow its distribution conventions."""

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Callable, Dict, List, NamedTuple, Optional, Set, Tuple

MANIFEST_PATH = ".claude-plugin/marketplace.json"
SKILLS_DIRECTORY = "skills"
REPOSITORY_SUBJECT = "(repository)"
NAME_PREFIX = "ba0918-"
REQUIRED_FIELDS = ("name", "description")
DESCRIPTION_LIMIT = 1024
LINE_LIMIT = 500
ESCAPING_REFERENCE = "../"
AMBIGUOUS_COLON = ": "
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BLOCK_SCALAR_PATTERN = re.compile(r"^[|>](?:[0-9][+-]?|[+-][0-9]?)?$")
ROUTING_FIELD = "ba0918-routing"
ROUTING_ALWAYS = "always"
ROUTING_REQUIRED_PATTERN = re.compile(r"^required:[a-z0-9]+(?:-[a-z0-9]+)*$")


class Violation(NamedTuple):
    skill: str
    rule: str
    message: str


class Skill(NamedTuple):
    """One skill directory, read into memory and parsed."""

    name: str
    files: Dict[str, str]
    fields: Optional[Dict[str, object]]

    @property
    def skill_md(self) -> str:
        return self.files.get("SKILL.md", "")

    @property
    def routing(self) -> Optional[str]:
        metadata = (self.fields or {}).get("metadata")
        if not isinstance(metadata, dict):
            return None
        value = metadata.get(ROUTING_FIELD)
        return value if isinstance(value, str) else None


# --- Rules: each takes a parsed skill and returns the violations it finds ---


def check_line_limit(skill: Skill) -> List[Violation]:
    line_count = len(skill.skill_md.splitlines())
    if line_count <= LINE_LIMIT:
        return []
    return [
        Violation(
            skill.name,
            "line-limit",
            f"SKILL.md is {line_count} lines, over the {LINE_LIMIT} line limit",
        )
    ]


def check_self_containment(skill: Skill) -> List[Violation]:
    return [
        Violation(
            skill.name,
            "external-reference",
            f"{relative_path} refers outside the skill directory "
            f"with {ESCAPING_REFERENCE!r}",
        )
        for relative_path, text in sorted(skill.files.items())
        if ESCAPING_REFERENCE in text
    ]


def check_skill_document_present(skill: Skill) -> List[Violation]:
    if "SKILL.md" in skill.files:
        return []
    return [
        Violation(
            skill.name,
            "skill-md-missing",
            "the skill directory contains no SKILL.md",
        )
    ]


def check_frontmatter_presence(skill: Skill) -> List[Violation]:
    if skill.fields is not None or "SKILL.md" not in skill.files:
        return []
    return [
        Violation(
            skill.name,
            "frontmatter-missing",
            "SKILL.md has no closed YAML frontmatter block",
        )
    ]


def check_required_fields(skill: Skill) -> List[Violation]:
    if skill.fields is None:
        return []
    return [
        Violation(
            skill.name,
            "field-missing",
            f"frontmatter is missing the required field {field!r}",
        )
        for field in REQUIRED_FIELDS
        if not skill.fields.get(field)
    ]


def check_name_agreement(skill: Skill) -> List[Violation]:
    declared = (skill.fields or {}).get("name")
    if not declared or declared == skill.name:
        return []
    return [
        Violation(
            skill.name,
            "name-mismatch",
            f"frontmatter name {declared!r} does not match "
            f"directory name {skill.name!r}",
        )
    ]


def check_name_grammar(skill: Skill) -> List[Violation]:
    if skill.fields is None:
        return []
    violations = []
    if not NAME_PATTERN.match(skill.name):
        violations.append(
            Violation(
                skill.name,
                "name-charset",
                "skill name must be lowercase alphanumerics joined by single hyphens",
            )
        )
    if not skill.name.startswith(NAME_PREFIX):
        violations.append(
            Violation(
                skill.name,
                "name-prefix",
                f"skill name must start with {NAME_PREFIX!r}",
            )
        )
    return violations


def check_description_length(skill: Skill) -> List[Violation]:
    description = (skill.fields or {}).get("description")
    if not isinstance(description, str) or len(description) <= DESCRIPTION_LIMIT:
        return []
    return [
        Violation(
            skill.name,
            "description-length",
            f"description is {len(description)} characters, over the "
            f"{DESCRIPTION_LIMIT} character limit",
        )
    ]


def check_routing_value(skill: Skill) -> List[Violation]:
    routing = skill.routing
    if routing is None or is_valid_routing(routing):
        return []
    return [
        Violation(
            skill.name,
            "routing-invalid",
            f"{ROUTING_FIELD} is {routing!r}; only 'always' and "
            "'required:<trigger>' are defined",
        )
    ]


def check_scalar_quoting(skill: Skill) -> List[Violation]:
    """Reject frontmatter values a YAML parser would read as a nested mapping.

    A plain scalar containing ': ' is not valid YAML, and the Japanese trigger
    keywords every description carries are introduced by exactly that sequence.
    Without this rule the lenient in-house parser accepts a file the published
    Agent Skills validator rejects.
    """
    violations = []
    for line in frontmatter_lines(skill.skill_md):
        key, separator, value = line.strip().partition(":")
        if not separator:
            continue
        value = value.strip()
        if not value or is_quoted(value) or AMBIGUOUS_COLON not in value:
            continue
        violations.append(
            Violation(
                skill.name,
                "frontmatter-unquoted-colon",
                f"frontmatter value of {key.strip()!r} contains {AMBIGUOUS_COLON!r} "
                "and must be quoted",
            )
        )
    return violations


def check_block_scalar(skill: Skill) -> List[Violation]:
    """Reject a frontmatter value written as a YAML block scalar.

    The in-house parser reads a value as the text after the first colon on the
    same line, so `description: >` parses as the literal ">" and every check
    against the description — its presence and its length — then inspects a one
    character string. Rejecting the form keeps the parser's supported surface
    declared instead of silently mis-parsed.
    """
    violations = []
    for line in frontmatter_lines(skill.skill_md):
        key, separator, value = line.strip().partition(":")
        if not separator or not BLOCK_SCALAR_PATTERN.match(value.strip()):
            continue
        violations.append(
            Violation(
                skill.name,
                "frontmatter-blockscalar",
                f"frontmatter value of {key.strip()!r} is a YAML block scalar; "
                "this validator reads inline values only",
            )
        )
    return violations


def is_valid_routing(value: str) -> bool:
    return value == ROUTING_ALWAYS or bool(ROUTING_REQUIRED_PATTERN.match(value))


SKILL_RULES: "tuple[Callable[[Skill], List[Violation]], ...]" = (
    check_line_limit,
    check_self_containment,
    check_skill_document_present,
    check_frontmatter_presence,
    check_required_fields,
    check_name_agreement,
    check_description_length,
    check_name_grammar,
    check_routing_value,
    check_scalar_quoting,
    check_block_scalar,
)


def check_skill(skill: Skill) -> List[Violation]:
    return [violation for rule in SKILL_RULES for violation in rule(skill)]


def is_present_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_manifest_metadata(manifest: Dict[str, object]) -> List[Violation]:
    """Check the identity fields the plugin install command is built from."""
    violations = []
    if not is_present_string(manifest.get("name")):
        violations.append(
            Violation(
                REPOSITORY_SUBJECT,
                "marketplace-metadata",
                f"{MANIFEST_PATH} has no top-level 'name'",
            )
        )
    plugins = manifest.get("plugins")
    for index, plugin in enumerate(plugins if isinstance(plugins, list) else []):
        for field in ("name", "source"):
            if not is_present_string(plugin.get(field)):
                violations.append(
                    Violation(
                        REPOSITORY_SUBJECT,
                        "marketplace-metadata",
                        f"plugin at index {index} has no {field!r}",
                    )
                )
    return violations


def check_manifest(
    manifest: Optional[Dict[str, object]], present: Set[str]
) -> List[Violation]:
    """Compare the manifest against the skills on disk.

    Entries are checked as paths, not as basenames: a manifest naming
    './skil/ba0918-x' advertises a directory that does not exist, and comparing
    only the last segment would call that agreement. A trailing slash is
    accepted, since it denotes the same directory.

    A malformed entry is reported once. Its basename still counts as listed, so
    the skill it was meant to name is not additionally reported as absent, but
    it is kept out of the orphan comparison so a typo is not reported twice.
    """
    entries = manifest_entries(manifest) if manifest is not None else None
    if entries is None:
        return [
            Violation(
                REPOSITORY_SUBJECT,
                "marketplace-unreadable",
                f"{MANIFEST_PATH} is missing, is not valid JSON, "
                "or is not shaped as a marketplace manifest",
            )
        ]

    violations = check_manifest_metadata(manifest or {})
    listed: List[str] = []
    resolvable: List[str] = []
    for entry in entries:
        parts = [
            part
            for part in PurePosixPath(entry.replace("\\", "/")).parts
            if part != "."
        ]
        name = parts[-1] if parts else entry
        listed.append(name)
        if "\\" in entry or len(parts) != 2 or parts[0] != SKILLS_DIRECTORY:
            violations.append(
                Violation(
                    name,
                    "marketplace-path",
                    f"manifest entry {entry!r} must be './{SKILLS_DIRECTORY}/<name>'",
                )
            )
        else:
            resolvable.append(name)

    violations.extend(
        Violation(
            name,
            "marketplace-duplicate",
            f"{MANIFEST_PATH} lists this skill {listed.count(name)} times",
        )
        for name in sorted({n for n in listed if listed.count(n) > 1})
    )
    violations.extend(
        Violation(name, "marketplace-missing", f"skill is absent from {MANIFEST_PATH}")
        for name in sorted(present - set(listed))
    )
    violations.extend(
        Violation(
            name,
            "marketplace-orphan",
            f"{MANIFEST_PATH} lists a skill that does not exist",
        )
        for name in sorted(set(resolvable) - present)
    )
    return violations


# --- Parsing ---


def is_quoted(value: str) -> bool:
    return len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'"


def unquote(value: str) -> str:
    return value[1:-1] if is_quoted(value) else value


def frontmatter_lines(text: str) -> List[str]:
    """The raw lines between the opening and closing frontmatter delimiters."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    body = []
    for line in lines[1:]:
        if line.strip() == "---":
            return body
        body.append(line)
    return []


def parse_frontmatter(text: str) -> Optional[Dict[str, object]]:
    """Parse the leading YAML frontmatter block, one level of nesting deep.

    Only the subset SKILL.md frontmatter uses is understood: scalar entries and
    single-level mappings. Splitting on the first colon keeps the rest of the
    value intact, so both a Japanese keyword list inside a description and a
    `required:<trigger>` routing value survive.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields: Dict[str, object] = {}
    parent: Optional[str] = None
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, separator, value = line.strip().partition(":")
        if not separator:
            continue
        key, value = key.strip(), unquote(value.strip())
        if line[:1].isspace() and parent is not None:
            nested = fields.setdefault(parent, {})
            if isinstance(nested, dict):
                nested[key] = value
        elif value == "":
            parent = key
            fields.setdefault(key, {})
        else:
            parent = None
            fields[key] = value
    return None


# --- Reading the repository ---


def is_inside(path: Path, root: Path) -> bool:
    """Whether path stays within root once symlinks are resolved.

    Guards the walk against a symlink inside the repository pointing outward:
    the validator must never read a file outside the repository it was given.
    """
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def read_text_files(directory: Path, root: Path) -> Dict[str, str]:
    files: Dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if not path.is_file() or not is_inside(path, root):
            continue
        try:
            files[path.relative_to(directory).as_posix()] = path.read_text(
                encoding="utf-8"
            )
        except (UnicodeDecodeError, OSError):
            continue
    return files


def collect_skills(root: Path) -> List[Skill]:
    skills_dir = root / SKILLS_DIRECTORY
    if not skills_dir.is_dir():
        return []
    skills = []
    for directory in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        files = read_text_files(directory, root)
        skills.append(
            Skill(
                name=directory.name,
                files=files,
                fields=parse_frontmatter(files.get("SKILL.md", "")),
            )
        )
    return skills


def read_manifest(root: Path) -> Optional[Dict[str, object]]:
    """The parsed marketplace manifest, or None if it cannot be read as one."""
    path = root / MANIFEST_PATH
    if not path.is_file() or not is_inside(path, root):
        return None
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError, UnicodeDecodeError):
        return None
    return manifest if isinstance(manifest, dict) else None


def manifest_entries(manifest: Dict[str, object]) -> Optional[List[str]]:
    """The advertised skill entries, or None if the manifest is misshapen.

    Returning None rather than raising keeps a hand-edited typo in the
    distribution metadata reportable as a named rule instead of a traceback.
    """
    plugins = manifest.get("plugins", [])
    if not isinstance(plugins, list):
        return None
    entries: List[str] = []
    for plugin in plugins:
        if not isinstance(plugin, dict):
            return None
        skills = plugin.get("skills", [])
        if not isinstance(skills, list):
            return None
        if not all(isinstance(entry, str) for entry in skills):
            return None
        entries.extend(skills)
    return entries


def scan_repository(root: Path) -> Tuple[List[Skill], List[Violation]]:
    """Read the repository once and return what was found alongside the verdict."""
    root = Path(root)
    skills = collect_skills(root)
    violations = [v for skill in skills for v in check_skill(skill)]
    violations.extend(
        check_manifest(read_manifest(root), {s.name for s in skills})
    )
    return skills, violations


def validate_repository(root: Path) -> List[Violation]:
    return scan_repository(root)[1]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root",
        nargs="?",
        default=str(Path(__file__).resolve().parent.parent),
        help="repository root to validate (defaults to this repository)",
    )
    root = Path(parser.parse_args(argv).root).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}")
        return 2

    skills, violations = scan_repository(root)
    for violation in violations:
        print(f"{violation.skill}: {violation.rule}: {violation.message}")
    print(f"{len(skills)} skills checked, {len(violations)} violations")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
