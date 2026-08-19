#!/usr/bin/env python3
"""Validate that this repository's skills follow its distribution conventions."""

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Callable, Dict, List, NamedTuple, Optional, Set, Tuple

MANIFEST_PATH = ".claude-plugin/marketplace.json"
PLUGIN_MANIFEST_PATH = ".claude-plugin/plugin.json"
PACKAGE_MANIFEST_PATH = "package.json"
CHANGELOG_PATH = "CHANGELOG.md"
RELEASE_HEADING_PATTERN = re.compile(r"^##\s+\[([^\]]+)\]")
UNRELEASED_HEADING = "unreleased"
SKILLS_DIRECTORY = "skills"
REPOSITORY_SUBJECT = "(repository)"
NAME_PREFIX = "ba0918-"
REQUIRED_FIELDS = ("name", "description")
DESCRIPTION_LIMIT = 1024
NAME_LIMIT = 64
LINE_LIMIT = 500
RELATIVE_ESCAPES = ("../", "..\\")
OUTSIDE_TARGET_PREFIXES = ("/", "~")
WINDOWS_DRIVE_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")
INLINE_LINK_PATTERN = re.compile(r"\]\(\s*<?([^)\s>]+)")
REFERENCE_DEFINITION_PATTERN = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?([^\s>]+)")
AMBIGUOUS_COLON = ": "
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BLOCK_SCALAR_PATTERN = re.compile(r"^[|>](?:[0-9][+-]?|[+-][0-9]?)?$")
ROUTING_FIELD = "ba0918-routing"
ROUTING_ALWAYS = "always"
ROUTING_REQUIRED_PATTERN = re.compile(r"^required:[a-z0-9]+(?:-[a-z0-9]+)*$")


class Violation(NamedTuple):
    """One rule breach, located in the repository where a rule can locate it.

    A rule that scans lines fills path and line so an editor or a CI annotation
    can jump to the site; a rule about a whole skill or the manifest leaves them
    unset and is reported against its subject alone.
    """

    skill: str
    rule: str
    message: str
    path: Optional[str] = None
    line: Optional[int] = None


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


class JsonFile(NamedTuple):
    """A JSON file as the repository offers it: absent, unreadable, or parsed.

    Absence and unreadability are kept apart because they say different things
    about a distribution channel: a manifest the repository does not ship is a
    channel it does not offer, while one it ships but nobody can parse is a
    channel that is broken.
    """

    present: bool
    document: Optional[Dict[str, object]]

    @property
    def unreadable(self) -> bool:
        return self.present and self.document is None


class Repository(NamedTuple):
    """The repository-level material, read into memory and parsed.

    A repository rule receives this and returns violations, exactly as a skill
    rule receives a Skill: reading happens once, in one place, and a rule stays
    a pure function of what was found.
    """

    manifest: JsonFile
    plugin_manifest: JsonFile
    package_manifest: JsonFile
    changelog: Optional[str]
    skill_names: Set[str]


def repository_path(skill_name: str, relative_path: str) -> str:
    """Where a file inside a skill directory sits relative to the repository root."""
    return f"{SKILLS_DIRECTORY}/{skill_name}/{relative_path}"


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
    """Reject references pointing outside the skill directory.

    A relative escape (`../`, `..\\`) is matched anywhere in the line, because a
    path written in prose breaks a single-directory install just as a link does.
    An absolute or home-anchored path is judged only where it is the target of a
    markdown link or reference definition: a skill may legitimately name an
    installation directory such as `~/.claude/skills/` in prose, and matching
    those as raw text would report the sentence describing the install.
    """
    violations = []
    for relative_path, text in sorted(skill.files.items()):
        for number, line in enumerate(text.splitlines(), start=1):
            reference = escaping_reference(line)
            if reference is None:
                continue
            violations.append(
                Violation(
                    skill.name,
                    "external-reference",
                    f"{reference!r} refers outside the skill directory",
                    repository_path(skill.name, relative_path),
                    number,
                )
            )
    return violations


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
    if len(skill.name) > NAME_LIMIT:
        violations.append(
            Violation(
                skill.name,
                "name-length",
                f"skill name is {len(skill.name)} characters, over the "
                f"{NAME_LIMIT} character limit",
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
    for number, line in frontmatter_lines(skill.skill_md):
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
                repository_path(skill.name, "SKILL.md"),
                number,
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
    for number, line in frontmatter_lines(skill.skill_md):
        key, separator, value = line.strip().partition(":")
        if not separator or not BLOCK_SCALAR_PATTERN.match(value.strip()):
            continue
        violations.append(
            Violation(
                skill.name,
                "frontmatter-blockscalar",
                f"frontmatter value of {key.strip()!r} is a YAML block scalar; "
                "this validator reads inline values only",
                repository_path(skill.name, "SKILL.md"),
                number,
            )
        )
    return violations


def escaping_reference(line: str) -> Optional[str]:
    """The first reference on this line that leaves the skill directory."""
    for marker in RELATIVE_ESCAPES:
        if marker in line:
            return marker
    for target in link_targets(line):
        if points_outside(target):
            return target
    return None


def link_targets(line: str) -> List[str]:
    """Every markdown link and reference-definition target written on the line."""
    targets = INLINE_LINK_PATTERN.findall(line)
    definition = REFERENCE_DEFINITION_PATTERN.match(line)
    return targets + ([definition.group(1)] if definition else [])


def points_outside(target: str) -> bool:
    return target.startswith(OUTSIDE_TARGET_PREFIXES) or bool(
        WINDOWS_DRIVE_PATTERN.match(target)
    )


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


def marketplace_readable(repository: Repository) -> bool:
    """Whether the manifest can be read as a marketplace manifest at all.

    Absent, unparseable or misshapen is the single condition under which the
    repository has no distribution metadata to be judged against.
    """
    document = repository.manifest.document
    return document is not None and manifest_is_shaped(document)


def check_manifest(repository: Repository) -> List[Violation]:
    """Check the distribution metadata the plugin install command is built from.

    The manifest deliberately does not list the skills. A plugin's skills load
    from the skills/ directory under its source by default, so a list here would
    only repeat the scan the runtime already performs, while charging every new
    skill an edit to a file that decides nothing.
    """
    if not marketplace_readable(repository):
        return [
            Violation(
                REPOSITORY_SUBJECT,
                "marketplace-unreadable",
                f"{MANIFEST_PATH} is missing, is not valid JSON, "
                "or is not shaped as a marketplace manifest",
            )
        ]
    return check_manifest_metadata(repository.manifest.document or {})


def declared_version(document: Optional[Dict[str, object]]) -> Optional[str]:
    """The version this document declares, or None if it declares none."""
    version = (document or {}).get("version")
    return version.strip() if is_present_string(version) else None


def canonical_version(repository: Repository) -> Optional[str]:
    """The one version the repository is released under.

    It is read from the first plugin entry of the marketplace manifest, which is
    the copy the plugin install command shows, and every other version in the
    repository is checked against it.
    """
    plugins = (repository.manifest.document or {}).get("plugins")
    first = plugins[0] if isinstance(plugins, list) and plugins else None
    return declared_version(first if isinstance(first, dict) else None)


def version_disagreement(
    rule: str,
    path: str,
    declared: Optional[str],
    canonical: Optional[str],
    line: Optional[int] = None,
) -> List[Violation]:
    """Report a version that disagrees with the canonical one.

    An absent version is judged by the caller, not here, because the two callers
    read it differently: a changelog holding no release describes a repository
    that has not released, while a shipped JSON manifest naming no version is a
    channel shipping under a version nobody declared.

    A repository that declares no canonical version has nothing to be checked
    against either way.
    """
    if canonical is None or declared is None or declared == canonical:
        return []
    return [
        Violation(
            REPOSITORY_SUBJECT,
            rule,
            f"{path} declares version {declared!r}, but {MANIFEST_PATH} "
            f"declares {canonical!r}",
            path,
            line,
        )
    ]


def version_declaring_paths(repository: Repository) -> List[str]:
    """Every path that names a version, in the order a report should list them."""
    release = latest_release(repository.changelog)
    declared = (
        (PLUGIN_MANIFEST_PATH, declared_version(repository.plugin_manifest.document)),
        (PACKAGE_MANIFEST_PATH, declared_version(repository.package_manifest.document)),
        (CHANGELOG_PATH, release[1] if release is not None else None),
    )
    return [path for path, version in declared if version is not None]


def check_canonical_version(repository: Repository) -> List[Violation]:
    """Report versions left with no canonical version to be checked against.

    A repository that names no version anywhere has not released and is left
    unchecked, but one whose channels name versions while the marketplace
    manifest names none is already in the state the other three rules exist to
    catch: with the canonical version gone they all fall silent, so its absence
    is itself the disagreement.

    A manifest that cannot be read at all is passed over rather than reported
    twice: marketplace-unreadable already names that file, and a second
    violation would only restate that the same file could not be read.
    """
    if (
        not marketplace_readable(repository)
        or canonical_version(repository) is not None
    ):
        return []
    paths = version_declaring_paths(repository)
    if not paths:
        return []
    return [
        Violation(
            REPOSITORY_SUBJECT,
            "version-sync-canonical",
            f"{MANIFEST_PATH} declares no version for its first plugin, "
            f"but {', '.join(paths)} declare one",
            MANIFEST_PATH,
        )
    ]


def check_json_channel(
    manifest: JsonFile,
    path: str,
    unreadable_rule: str,
    sync_rule: str,
    canonical: Optional[str],
) -> List[Violation]:
    """Check one JSON distribution manifest: readable at all, then in agreement.

    A manifest the repository does not ship is a channel it does not offer and
    is passed over. One it does ship is required to name the released version:
    were a version absent, empty or not a string passed over as nothing to
    compare, deleting the key would silence a disagreement rather than resolve
    it, and the channel would ship under a version nobody declared.

    Every violation names the file but no line: json.loads reports no position
    for the value it parsed, and tracking one would mean hand-rolling a JSON
    parser for the sake of a jumpable column. The changelog rule carries a line
    only because it already reads the file line by line.
    """
    if manifest.unreadable:
        return [
            Violation(
                REPOSITORY_SUBJECT,
                unreadable_rule,
                f"{path} is present but cannot be read as a JSON object",
                path,
            )
        ]
    if not manifest.present or canonical is None:
        return []
    declared = declared_version(manifest.document)
    if declared is None:
        return [
            Violation(
                REPOSITORY_SUBJECT,
                sync_rule,
                f"{path} declares no version, but {MANIFEST_PATH} "
                f"declares {canonical!r}",
                path,
            )
        ]
    return version_disagreement(sync_rule, path, declared, canonical)


def check_plugin_manifest(repository: Repository) -> List[Violation]:
    return check_json_channel(
        repository.plugin_manifest,
        PLUGIN_MANIFEST_PATH,
        "plugin-manifest-unreadable",
        "version-sync-plugin",
        canonical_version(repository),
    )


def check_package_manifest(repository: Repository) -> List[Violation]:
    return check_json_channel(
        repository.package_manifest,
        PACKAGE_MANIFEST_PATH,
        "package-manifest-unreadable",
        "version-sync-package",
        canonical_version(repository),
    )


def latest_release(changelog: Optional[str]) -> Optional[Tuple[int, str]]:
    """The newest release heading in the changelog, as its line and its version.

    The 'Unreleased' section Keep a Changelog puts above the releases names no
    version, so it is passed over instead of compared. A changelog holding only
    that section describes a repository that has not released yet, and returning
    None leaves it with nothing to check.
    """
    for number, line in enumerate((changelog or "").splitlines(), start=1):
        match = RELEASE_HEADING_PATTERN.match(line)
        if match and match.group(1).strip().lower() != UNRELEASED_HEADING:
            return number, match.group(1).strip()
    return None


def check_changelog_version(repository: Repository) -> List[Violation]:
    release = latest_release(repository.changelog)
    if release is None:
        return []
    line, version = release
    return version_disagreement(
        "version-sync-changelog",
        CHANGELOG_PATH,
        version,
        canonical_version(repository),
        line,
    )


REPO_RULES: "tuple[Callable[[Repository], List[Violation]], ...]" = (
    check_manifest,
    check_canonical_version,
    check_plugin_manifest,
    check_package_manifest,
    check_changelog_version,
)


def check_repository(repository: Repository) -> List[Violation]:
    return [violation for rule in REPO_RULES for violation in rule(repository)]


# --- Parsing ---


def is_quoted(value: str) -> bool:
    """Whether the value is one quoted scalar rather than merely edged by quotes.

    The interior must be free of the delimiter: `"a" b: "c"` opens and closes on
    the same character without being a single scalar, and reading it as quoted
    would hide the unquoted ': ' between the two quoted runs.
    """
    return (
        len(value) >= 2
        and value[0] == value[-1]
        and value[0] in "\"'"
        and value[0] not in value[1:-1]
    )


def unquote(value: str) -> str:
    return value[1:-1] if is_quoted(value) else value


def frontmatter_lines(text: str) -> List[Tuple[int, str]]:
    """The raw lines between the frontmatter delimiters, with their line numbers.

    Numbering is 1-based and counted from the start of the file, so a reported
    violation names the line an editor would open.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    body = []
    for number, line in enumerate(lines[1:], start=2):
        if line.strip() == "---":
            return body
        body.append((number, line))
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


def read_file(root: Path, relative_path: str) -> Optional[str]:
    """The text of this file, or None if the repository does not offer it."""
    path = root / relative_path
    if not path.is_file() or not is_inside(path, root):
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def read_json_file(root: Path, relative_path: str) -> JsonFile:
    """How this JSON file stands: not shipped, shipped but unreadable, or parsed.

    Presence is decided on disk rather than on the read succeeding, so a file
    that exists yet cannot be decoded or parsed stays distinguishable from one
    the repository never shipped.
    """
    path = root / relative_path
    if not path.is_file() or not is_inside(path, root):
        return JsonFile(present=False, document=None)
    text = read_file(root, relative_path)
    try:
        document = json.loads(text) if text is not None else None
    except json.JSONDecodeError:
        document = None
    return JsonFile(
        present=True, document=document if isinstance(document, dict) else None
    )


def manifest_is_shaped(manifest: Dict[str, object]) -> bool:
    """Whether the document is shaped as a marketplace manifest.

    Only the plugins array is inspected, because it is what every remaining rule
    reads from: a document whose plugins are not a list of mappings has nothing
    those rules could judge, and saying so once beats letting each fail apart.
    """
    plugins = manifest.get("plugins", [])
    if not isinstance(plugins, list):
        return False
    return all(isinstance(plugin, dict) for plugin in plugins)


def scan_repository(root: Path) -> Tuple[List[Skill], List[Violation]]:
    """Read the repository once and return what was found alongside the verdict."""
    root = Path(root)
    skills = collect_skills(root)
    repository = Repository(
        manifest=read_json_file(root, MANIFEST_PATH),
        plugin_manifest=read_json_file(root, PLUGIN_MANIFEST_PATH),
        package_manifest=read_json_file(root, PACKAGE_MANIFEST_PATH),
        changelog=read_file(root, CHANGELOG_PATH),
        skill_names={s.name for s in skills},
    )
    violations = [v for skill in skills for v in check_skill(skill)]
    violations.extend(check_repository(repository))
    return skills, violations


def validate_repository(root: Path) -> List[Violation]:
    return scan_repository(root)[1]


def describe_location(violation: Violation) -> str:
    """Where the violation is, as a jumpable `path:line` if the rule knows one."""
    if violation.path is None:
        return violation.skill
    if violation.line is None:
        return violation.path
    return f"{violation.path}:{violation.line}"


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
        print(f"{describe_location(violation)}: {violation.rule}: {violation.message}")
    print(f"{len(skills)} skills checked, {len(violations)} violations")
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
