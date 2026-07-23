#!/usr/bin/env python3
"""groundwork validator — Python stdlib only (zero third-party deps, enforced).

Walks a repo tree and reports ERROR/WARN Findings. ERROR fails the gate.
Schema-specific checks (#5/#6/#7/#8) live in a later build slice; this module
is the generic foundation: frontmatter parsing, secrets, context budget,
referential integrity.
"""
import datetime
import fnmatch
import math
import os
import re
import subprocess
import sys
import unicodedata
from collections import namedtuple

Finding = namedtuple("Finding", ["level", "path", "line", "message"])

SKIP_DIRS = {".git", ".remember", "__pycache__"}
# Non-content trees, relative to the validated root: the validator's own test
# harness (deliberately-poisoned fixtures + documented-example secret patterns)
# and the build-workbench docs (specs/plans that quote that poison verbatim).
# Everything else is checked at full strictness.
SKIP_RELPATHS = {"tests", os.path.join("docs", "superpowers")}


def parse_frontmatter(text, path="<unknown>"):
    """Parse a restricted frontmatter block. Returns (dict, list[Finding]).

    Grammar (flat subset only): a leading '---' line, then lines that are
    'key: value', 'key:' (introducing a list), '- item' list elements, blank,
    or '# comment', terminated by a closing '---'. Every scalar is returned as
    a RAW STRING (no type coercion — field validators own all typing, which
    sidesteps the Norway/date-coercion problems). Any other syntax ERRORs.
    """
    findings = []
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return {}, findings  # no frontmatter block is not itself an error
    data = {}
    current_key = None
    closed = False
    i = 1
    while i < len(lines):
        raw = lines[i]
        line_no = i + 1
        stripped = raw.strip()
        if stripped == "---":
            closed = True
            break
        if stripped == "" or stripped.startswith("#"):
            i += 1
            continue
        if stripped.startswith("- "):
            if current_key is None:
                findings.append(Finding("ERROR", path, line_no, "list item with no preceding key"))
            elif not isinstance(data.get(current_key), list):
                findings.append(Finding("ERROR", path, line_no,
                                        "list item under scalar key '%s'" % current_key))
            else:
                data[current_key].append(stripped[2:].strip())
            i += 1
            continue
        if raw.startswith((" ", "\t")):
            findings.append(Finding("ERROR", path, line_no,
                                    "unsupported indented frontmatter syntax: %r" % raw))
            i += 1
            continue
        if ":" in raw:
            key, _, value = raw.partition(":")
            key, value = key.strip(), value.strip()
            if key == "":
                findings.append(Finding("ERROR", path, line_no, "empty frontmatter key"))
            elif key in data:
                findings.append(Finding(
                    "ERROR", path, line_no,
                    "duplicate frontmatter key '%s'" % key))
                current_key = None
            elif value == "":
                data[key] = []          # a list is expected to follow
                current_key = key
            else:
                data[key] = value       # raw string, no coercion
                current_key = key
            i += 1
            continue
        findings.append(Finding("ERROR", path, line_no,
                                "unsupported frontmatter syntax: %r" % raw))
        i += 1
    if not closed:
        findings.append(Finding("ERROR", path, len(lines),
                                "frontmatter block opened with '---' but never closed"))
    return data, findings


def _read_utf8(abspath, relpath):
    """Read text without letting I/O/encoding failures crash the validator."""
    try:
        with open(abspath, encoding="utf-8") as fh:
            text = fh.read()
    except UnicodeError:
        return None, [Finding(
            "ERROR", relpath, None,
            "structured file is not valid UTF-8")]
    except OSError as exc:
        return None, [Finding(
            "ERROR", relpath, None,
            "could not read structured file: %s" % exc)]
    return text, []


def _load_frontmatter(abspath, relpath):
    """Read and parse one structured Markdown file. None means unreadable."""
    text, findings = _read_utf8(abspath, relpath)
    if text is None:
        return None, findings
    data, parse_findings = parse_frontmatter(text, relpath)
    return data, findings + parse_findings


SECRET_PATTERNS = [
    ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private key header", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PGP |DSA )?PRIVATE KEY-----")),
    ("GitHub token", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("Slack token", re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}")),
    ("OpenAI-style API key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
]
_HIGH_ENTROPY = re.compile(r"[A-Za-z0-9+/=_-]{40,}")


def check_secrets(text, path):
    """High-signal, not exhaustive. Global ERROR — a leaked credential is
    dangerous everywhere (unlike the demo-only synthetic rule, #16)."""
    findings = []
    for lineno, line in enumerate(text.split("\n"), 1):
        for label, pat in SECRET_PATTERNS:
            if pat.search(line):
                findings.append(Finding("ERROR", path, lineno,
                                        "possible %s (high-signal, not exhaustive)" % label))
    return findings


def _shannon_entropy(s):
    if not s:
        return 0.0
    return -sum((s.count(c) / len(s)) * math.log2(s.count(c) / len(s)) for c in set(s))


def check_entropy(text, path):
    findings = []
    for lineno, line in enumerate(text.split("\n"), 1):
        for tok in _HIGH_ENTROPY.findall(line):
            if _shannon_entropy(tok) >= 4.0:
                findings.append(Finding("WARN", path, lineno,
                                        "high-entropy string (possible secret; high-signal, not exhaustive)"))
    return findings


WARN_TOKENS = 20_000
ERROR_TOKENS = 50_000


def est_tokens(num_bytes):
    """Measure bytes, report estimated tokens (stdlib len/4 heuristic, #13)."""
    return num_bytes // 4


def check_context_budget(path, data_bytes):
    toks = est_tokens(len(data_bytes))
    if toks >= ERROR_TOKENS:
        return [Finding("ERROR", path, None,
                        "context budget: ~%d est. tokens (>= %d ERROR)" % (toks, ERROR_TOKENS))]
    if toks >= WARN_TOKENS:
        return [Finding("WARN", path, None,
                        "context budget: ~%d est. tokens (>= %d WARN)" % (toks, WARN_TOKENS))]
    return []


_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def check_links(abspath, text, root):
    """ERROR on broken relative markdown links. External and anchor-only
    links are skipped (referential integrity, brief §10 validator)."""
    findings = []
    base = os.path.dirname(abspath)
    for lineno, line in enumerate(text.split("\n"), 1):
        for target in _LINK.findall(line):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = os.path.normpath(os.path.join(base, path_part))
            if not os.path.exists(resolved):
                findings.append(Finding("ERROR", os.path.relpath(abspath, root), lineno,
                                        "broken relative link: %s" % target))
    return findings


DIRECTIONS = {"up", "down"}
MOTIONS = {"automate", "build", "buy", "hire", "wait"}
AUTOMATION_MOTIONS = {"automate", "build"}
WORK_TYPES = {"routing", "sensemaking", "accountability"}
SHAPES = {"chat", "single-agent", "agent-team", "dont-bother"}
SCORE_FIELDS = ["score_repetition", "score_risk", "score_judgment",
                "score_company_specificity", "score_market_maturity"]
SCORE_VALUES = {"low", "medium", "high"}
GATE_FIELDS = ["gate_inputs", "gate_output", "gate_standard", "gate_source_of_truth",
               "gate_exception_path", "gate_error_cost", "gate_owner", "gate_review_gate"]


def parse_exec_table(text):
    """Parse the first markdown table whose header row contains 'Direction'.
    Returns [(activity, direction_lower, deep_link_or_None, line_no)]."""
    rows = []
    lines = text.split("\n")
    header_idx = None
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("|") and "direction" in line.lower():
            header_idx = idx
            break
    if header_idx is None:
        return rows
    for j in range(header_idx + 1, len(lines)):
        line = lines[j]
        if not line.lstrip().startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or set("".join(cells)) <= set("-: "):
            continue  # the |---|---| separator row
        activity = cells[0] if len(cells) > 0 else ""
        direction = cells[1].lower() if len(cells) > 1 else ""
        link = None
        if len(cells) > 2:
            m = _LINK.search(cells[2])
            if m:
                link = m.group(1)
        rows.append((activity, direction, link, j + 1))
    return rows


def check_deep_record(abspath, root):
    """#5 machinery-follows checks for one acted-on activity's deep record."""
    rel = os.path.relpath(abspath, root)
    data, findings = _load_frontmatter(abspath, rel)
    if data is None:
        return findings
    findings = list(findings)
    if not data:
        findings.append(Finding("WARN", rel, None,
                                "acted-on activity has no structured fields yet (incomplete thinking)"))
        return findings

    motion = data.get("motion")
    if motion is None or motion == []:
        findings.append(Finding("WARN", rel, None, "missing 'motion' (incomplete thinking)"))
    elif not isinstance(motion, str):
        findings.append(Finding("ERROR", rel, None,
                                "invalid motion %r — must be a single value (one of %s)"
                                % (motion, sorted(MOTIONS))))
    elif motion not in MOTIONS:
        findings.append(Finding("ERROR", rel, None,
                                "invalid motion %r (one of %s)" % (motion, sorted(MOTIONS))))
    on_automation = isinstance(motion, str) and motion in AUTOMATION_MOTIONS

    def require(field, valid=None):
        v = data.get(field)
        missing_level = "ERROR" if on_automation else "WARN"
        if v is None or v == [] or (isinstance(v, str) and v.strip() == ""):
            findings.append(Finding(missing_level, rel, None, "missing '%s'" % field))
        elif not isinstance(v, str):
            findings.append(Finding("ERROR", rel, None,
                                    "invalid '%s' %r — must be a single value" % (field, v)))
        elif valid is not None and v not in valid:
            findings.append(Finding("ERROR", rel, None,
                                    "invalid '%s' %r (one of %s)" % (field, v, sorted(valid))))

    require("work_type", WORK_TYPES)
    require("accountable_owner")
    for sf in SCORE_FIELDS:
        require(sf, SCORE_VALUES)

    if on_automation:
        require("substrate")
        require("shape", SHAPES)
        for gf in GATE_FIELDS:
            v = data.get(gf)
            if not isinstance(v, str):
                findings.append(Finding("ERROR", rel, None,
                                        "Describability Gate: '%s' must be a single answered value" % gf))
            elif v.strip() == "":
                findings.append(Finding("ERROR", rel, None,
                                        "Describability Gate: '%s' must be answered ('none' is valid; blank is not)" % gf))
            elif v.strip().lower() in {"n/a", "na", "tbd"}:
                findings.append(Finding("ERROR", rel, None,
                                        "Describability Gate: '%s' is %r — must be answered "
                                        "('none' is valid; 'N/A' is not, no waiver)" % (gf, v)))
    return findings


def check_ontology(root, ignore=()):
    """#5 structural checks over ontologies/<function>/ directories.
    Honors the same .gitignore patterns as the generic walker."""
    findings = []
    base = os.path.join(root, "ontologies")
    if not os.path.isdir(base):
        return findings
    for fn in sorted(os.listdir(base)):
        fdir = os.path.join(base, fn)
        if not os.path.isdir(fdir) or _ignored(fn, ignore):
            continue
        rel_fdir = os.path.relpath(fdir, root)
        exec_path = os.path.join(fdir, "_executive-view.md")
        deep_files = sorted(f for f in os.listdir(fdir)
                            if f.endswith(".md") and f != "_executive-view.md"
                            and not _ignored(f, ignore))
        linked = set()
        if not os.path.isfile(exec_path):
            if deep_files:
                findings.append(Finding("ERROR", os.path.join(rel_fdir, "_executive-view.md"),
                                        None, "function ontology has no executive view (_executive-view.md)"))
        else:
            rel_exec = os.path.relpath(exec_path, root)
            exec_text, exec_findings = _read_utf8(exec_path, rel_exec)
            findings += exec_findings
            rows = parse_exec_table(exec_text) if exec_text is not None else []
            for activity, direction, link, ln in rows:
                if direction not in DIRECTIONS:
                    findings.append(Finding("ERROR", rel_exec, ln,
                                            "Direction must be 'up' or 'down', got %r" % direction))
                if link:
                    linked.add(os.path.basename(link))
        for df in deep_files:
            findings += check_deep_record(os.path.join(fdir, df), root)
            if df not in linked:
                findings.append(Finding("WARN", os.path.join(rel_fdir, df), None,
                                        "deep record not listed in the executive view"))
    return findings


PROVENANCE = {"observed", "inferred", "confirmed", "superseded"}

ACTION_CLASSES = {"read-only", "reversible-write", "external-side-effect", "high-risk"}
RUNGS = {"value", "instruction", "reminder", "hard-block", "human-decision"}
TRACK2_CLASSES = {"external-side-effect", "high-risk"}
CARD_REQUIRED = ["owner", "backup_owner", "job",
                 "allowed_actions", "proposed_only_actions", "forbidden_actions",
                 "pause_condition", "retirement_condition",
                 "source_of_truth", "review_cadence", "known_failure_modes",
                 "last_reviewed", "next_review", "success_standard"]
CARD_TRACK2 = ["evidence_required", "sources_must_not_use", "review_sample"]


def _blank(v):
    """A field is blank if absent, an empty list (a bare 'key:'), or whitespace."""
    return v is None or v == [] or (isinstance(v, str) and v.strip() == "")


def _parse_date(v):
    if not isinstance(v, str) or \
            re.fullmatch(r"\d{4}-\d{2}-\d{2}", v.strip()) is None:
        return None
    try:
        return datetime.date.fromisoformat(v.strip())
    except ValueError:
        return None


def check_owner_cards(root, ignore=()):
    """#6 checks over skills/<name>/ work packages: required spine, track-2
    trio, freshness, and the card<->skill<->ontology drift checks. Strictness
    follows the skill's `provisioned` flag. Honors the same .gitignore
    patterns as the generic walker."""
    findings = []
    base = os.path.join(root, "skills")
    if os.path.islink(base):
        return [Finding(
            "ERROR", "skills", None,
            "skills directory must not be a symlink")]
    if not os.path.isdir(base):
        return findings
    if _ignored("skills", ignore):
        return findings
    today = datetime.date.today()
    ontologies_root = os.path.realpath(os.path.join(root, "ontologies"))
    memory_record_realpaths = None
    for name in sorted(os.listdir(base)):
        sdir = os.path.join(base, name)
        rel_sdir = os.path.relpath(sdir, root)
        if _ignored(name, ignore):
            continue
        if os.path.islink(sdir):
            findings.append(Finding(
                "ERROR", rel_sdir, None,
                "skill package directory must not be a symlink"))
            continue
        if not os.path.isdir(sdir):
            continue

        skill_path = os.path.join(sdir, "SKILL.md")
        rel_skill = os.path.relpath(skill_path, root)
        if _ignored("SKILL.md", ignore) or not os.path.isfile(skill_path):
            findings.append(Finding(
                "ERROR", rel_sdir, None,
                "skill package has no usable SKILL.md"))
            continue
        if os.path.islink(skill_path):
            findings.append(Finding(
                "ERROR", rel_skill, None,
                "SKILL.md must not be a symlink"))
            continue

        skill_fm, sfm_findings = _load_frontmatter(skill_path, rel_skill)
        findings += sfm_findings
        if skill_fm is None:
            continue

        skill_name = skill_fm.get("name")
        if not isinstance(skill_name, str) or not skill_name.strip():
            findings.append(Finding(
                "ERROR", rel_skill, None,
                "skill name must be a single non-blank value"))
        elif skill_name.strip() != name:
            findings.append(Finding(
                "ERROR", rel_skill, None,
                "skill name %r must match package directory %r"
                % (skill_name, name)))

        description = skill_fm.get("description")
        if not isinstance(description, str) or not description.strip():
            findings.append(Finding(
                "ERROR", rel_skill, None,
                "skill description must be a single non-blank value"))

        provisioned_value = skill_fm.get("provisioned")
        if not isinstance(provisioned_value, str) or \
                provisioned_value.strip().lower() not in {"yes", "no"}:
            findings.append(Finding(
                "ERROR", rel_skill, None,
                "skill provisioned must be a single 'yes' or 'no' value"))
        provisioned = isinstance(provisioned_value, str) and \
            provisioned_value.strip().lower() == "yes"

        if provisioned:
            baseline = skill_fm.get("baseline")
            if _blank(baseline):
                findings.append(Finding("ERROR", rel_skill, None,
                                        "provisioned skill must cite a captured 'baseline' (#5 provisioning gate)"))
            elif not isinstance(baseline, str):
                findings.append(Finding("ERROR", rel_skill, None,
                                        "skill baseline must be a single value"))
            else:
                if memory_record_realpaths is None:
                    memory_record_realpaths = _live_record_realpaths(
                        _memory_record_files(root))
                baseline_real = _record_ref_realpath(root, baseline)
                if baseline_real is None or \
                        baseline_real not in memory_record_realpaths:
                    findings.append(Finding(
                        "ERROR", rel_skill, None,
                        "baseline record not found (must be a repo-relative "
                        "path resolving to a memory record): %s"
                        % baseline.strip()))

        action_class = skill_fm.get("action_class")
        if not isinstance(action_class, str):
            findings.append(Finding(
                "ERROR", rel_skill, None,
                "skill action_class must be a single value (one of %s)"
                % sorted(ACTION_CLASSES)))
        elif action_class not in ACTION_CLASSES:
            findings.append(Finding(
                "ERROR", rel_skill, None,
                "invalid skill action_class %r (one of %s)"
                % (action_class, sorted(ACTION_CLASSES))))

        ontology = None
        ontology_ref = skill_fm.get("ontology")
        if not isinstance(ontology_ref, str) or not ontology_ref.strip():
            findings.append(Finding(
                "ERROR", rel_skill, None,
                "skill ontology must be a single non-blank reference"))
        else:
            ontology_ref = ontology_ref.strip()
            if "\x00" in ontology_ref:
                findings.append(Finding(
                    "ERROR", rel_skill, None,
                    "ontology reference contains a NUL byte"))
                ontology_path = None
            else:
                try:
                    ontology_path = os.path.realpath(
                        os.path.join(root, ontology_ref))
                except (OSError, ValueError):
                    ontology_path = None
                    findings.append(Finding(
                        "ERROR", rel_skill, None,
                        "ontology reference is not a valid filesystem path"))
            if ontology_path is None:
                under_ontologies = False
            else:
                try:
                    under_ontologies = os.path.commonpath(
                        (ontologies_root, ontology_path)) == ontologies_root
                except ValueError:
                    under_ontologies = False
            if ontology_path is None:
                pass
            elif not under_ontologies:
                findings.append(Finding(
                    "ERROR", rel_skill, None,
                    "ontology reference must stay under ontologies/: %s"
                    % ontology_ref))
            elif _ignored(os.path.basename(ontology_path), ignore):
                findings.append(Finding(
                    "ERROR", rel_skill, None,
                    "ontology reference not found or ignored: %s"
                    % ontology_ref))
            elif not os.path.isfile(ontology_path):
                findings.append(Finding(
                    "ERROR", rel_skill, None,
                    "ontology reference not found: %s" % ontology_ref))
            else:
                ontology, ontology_findings = _load_frontmatter(
                    ontology_path, os.path.relpath(ontology_path, root))
                findings += ontology_findings

        card_path = os.path.join(sdir, "owner-card.md")
        if _ignored("owner-card.md", ignore) or not os.path.isfile(card_path):
            level = "ERROR" if provisioned else "WARN"
            findings.append(Finding(
                level,
                os.path.join(rel_sdir, "owner-card.md"),
                None,
                ("%s skill has no Owner's Card"
                 % ("provisioned" if provisioned else "draft"))))
            continue
        rel_card = os.path.relpath(card_path, root)
        if os.path.islink(card_path):
            findings.append(Finding(
                "ERROR", rel_card, None,
                "owner-card.md must not be a symlink"))
            continue
        card, cfm_findings = _load_frontmatter(card_path, rel_card)
        findings += cfm_findings
        if card is None:
            continue
        miss = "ERROR" if provisioned else "WARN"

        for field in CARD_REQUIRED:
            value = card.get(field)
            if _blank(value):
                findings.append(Finding(
                    miss, rel_card, None,
                    "missing required card field '%s'" % field))
            elif not isinstance(value, str):
                findings.append(Finding(
                    "ERROR", rel_card, None,
                    "card field '%s' must be a single value" % field))

        is_track2 = isinstance(action_class, str) and action_class in TRACK2_CLASSES
        for field in CARD_TRACK2:
            value = card.get(field)
            if _blank(value):
                level = "ERROR" if (is_track2 and provisioned) else "WARN"
                findings.append(Finding(
                    level, rel_card, None,
                    "track-2 field '%s' blank "
                    "(required at external-side-effect/high-risk)" % field))
            elif not isinstance(value, str):
                findings.append(Finding(
                    "ERROR", rel_card, None,
                    "track-2 card field '%s' must be a single value" % field))

        next_review = _parse_date(card.get("next_review"))
        if isinstance(card.get("next_review"), str) and next_review is None:
            findings.append(Finding(
                miss, rel_card, None,
                "next_review must be an ISO date (YYYY-MM-DD)"))
        elif next_review is not None and next_review < today:
            findings.append(Finding(
                "WARN", rel_card, None,
                "next_review date has passed (freshness)"))

        last_reviewed = _parse_date(card.get("last_reviewed"))
        if isinstance(card.get("last_reviewed"), str) and last_reviewed is None:
            findings.append(Finding(
                miss, rel_card, None,
                "last_reviewed must be an ISO date (YYYY-MM-DD)"))
        elif last_reviewed is not None and last_reviewed > today:
            findings.append(Finding(
                miss, rel_card, None,
                "last_reviewed cannot be in the future"))
        elif last_reviewed is not None and (today - last_reviewed).days > 90:
            findings.append(Finding(
                "WARN", rel_card, None,
                "last_reviewed is over 90 days old (freshness)"))

        # --- drift: card action_class vs skill action_class ---
        card_action_class = card.get("action_class")
        if not isinstance(card_action_class, str):
            findings.append(Finding(
                "ERROR", rel_card, None,
                "card action_class must be a single value (one of %s)"
                % sorted(ACTION_CLASSES)))
        elif card_action_class not in ACTION_CLASSES:
            findings.append(Finding(
                "ERROR", rel_card, None,
                "invalid card action_class %r (one of %s)"
                % (card_action_class, sorted(ACTION_CLASSES))))
        elif isinstance(action_class, str) and \
                action_class in ACTION_CLASSES and \
                card_action_class != action_class:
            findings.append(Finding(
                "ERROR", rel_card, None,
                "card action_class %r drifts from skill action_class %r"
                % (card_action_class, action_class)))

        # --- drift: card owner / source_of_truth vs the referenced ontology ---
        if ontology is not None:
            accountable_owner = ontology.get("accountable_owner")
            if not isinstance(accountable_owner, str) or \
                    not accountable_owner.strip():
                findings.append(Finding(
                    "ERROR", rel_skill, None,
                    "referenced ontology accountable_owner must be "
                    "a single non-blank value"))
            else:
                card_owner = card.get("owner")
                if isinstance(card_owner, str) and \
                        card_owner.strip() != accountable_owner.strip():
                    findings.append(Finding(
                        "ERROR", rel_card, None,
                        "card owner %r drifts from ontology accountable_owner %r"
                        % (card_owner, accountable_owner)))

            gate_source_of_truth = ontology.get("gate_source_of_truth")
            if not isinstance(gate_source_of_truth, str) or \
                    not gate_source_of_truth.strip():
                findings.append(Finding(
                    "ERROR", rel_skill, None,
                    "referenced ontology gate_source_of_truth must be "
                    "a single non-blank value"))
            else:
                card_source_of_truth = card.get("source_of_truth")
                if isinstance(card_source_of_truth, str) and \
                        card_source_of_truth.strip() != \
                        gate_source_of_truth.strip():
                    findings.append(Finding(
                        "ERROR", rel_card, None,
                        "card source_of_truth drifts from ontology "
                        "gate_source_of_truth"))
    return findings


def _memory_record_files(root):
    out = []
    for abspath in iter_files(root, load_gitignore(root)):
        rel = os.path.relpath(abspath, root).replace("\\", "/")
        parts = rel.split("/")
        if "memory" in parts and abspath.endswith(".md") \
                and os.path.basename(abspath) not in {"_index.md", "README.md"}:
            out.append(abspath)
    return out


def _record_ref_realpath(root, ref):
    """Resolve a memory-record reference. None if the literal path is absolute
    or escapes the repo root (the schema says repo-relative), or unresolvable.
    Drive-letter ('C:...') and UNC ('\\\\server') literals are rejected on every
    platform — a repo-relative record path never looks like either."""
    ref = ref.strip()
    if os.path.isabs(ref) or ref.startswith(("\\\\", "//")) \
            or re.match(r"[A-Za-z]:", ref):
        return None
    norm = os.path.normpath(ref).replace("\\", "/")
    if norm == ".." or norm.startswith("../"):
        return None
    try:
        return os.path.realpath(os.path.join(root, ref))
    except (OSError, ValueError):
        return None


def _live_record_realpaths(records):
    """The reference allowlist: real paths of non-symlink records only, so a
    symlinked record cannot smuggle an out-of-tree target into the set."""
    return {os.path.realpath(p) for p in records if not os.path.islink(p)}


def check_memory(root):
    """#7 record-level shape checks. Nothing is silent at record level."""
    findings = []
    records = _memory_record_files(root)
    record_realpaths = _live_record_realpaths(records)
    symlinked = {p for p in records if os.path.islink(p)}
    for abspath in records:
        rel = os.path.relpath(abspath, root)
        if abspath in symlinked:
            findings.append(Finding("ERROR", rel, None,
                                    "memory record must not be a symlink"))
            continue
        data, fm = _load_frontmatter(abspath, rel)
        findings += fm
        if data is None:
            continue

        prov = data.get("provenance")
        if _blank(prov):
            findings.append(Finding("ERROR", rel, None, "missing 'provenance'"))
        elif not (isinstance(prov, str) and prov in PROVENANCE):
            findings.append(Finding("ERROR", rel, None,
                                    "invalid 'provenance' %r (one of %s)" % (prov, sorted(PROVENANCE))))

        owner = data.get("owner")
        if _blank(owner):
            findings.append(Finding("ERROR", rel, None, "missing 'owner' (an unowned memory is ungoverned drift)"))
        elif not isinstance(owner, str):
            findings.append(Finding("ERROR", rel, None, "'owner' must be a single value"))

        if _blank(data.get("valid_at")) or _parse_date(data.get("valid_at")) is None:
            findings.append(Finding("ERROR", rel, None, "missing or unparseable 'valid_at' (ISO date)"))

        source_blank = _blank(data.get("source"))
        if source_blank and prov == "confirmed":
            findings.append(Finding("ERROR", rel, None, "'confirmed' record has no 'source' (confirmation must cite evidence)"))
        elif source_blank:
            findings.append(Finding("WARN", rel, None, "missing 'source' (push toward evidence)"))

        if _blank(data.get("review_by")):
            findings.append(Finding("WARN", rel, None, "missing 'review_by' (staleness)"))
        else:
            rb = _parse_date(data.get("review_by"))
            if rb is None:
                findings.append(Finding("WARN", rel, None,
                                        "'review_by' is not an ISO date (YYYY-MM-DD)"))
            elif rb < datetime.date.today():
                findings.append(Finding("WARN", rel, None, "'review_by' has passed (staleness)"))

        # supersession invariants
        is_sup = prov == "superseded"
        has_sb = not _blank(data.get("superseded_by"))
        has_ia = not _blank(data.get("invalid_at"))
        if is_sup and not (has_sb and has_ia):
            findings.append(Finding("ERROR", rel, None,
                                    "superseded record must carry both 'superseded_by' and 'invalid_at'"))
        if not is_sup and (has_sb or has_ia):
            findings.append(Finding("ERROR", rel, None,
                                    "supersession fields (invalid_at/superseded_by) are forbidden on a live record"))
        if has_ia and _parse_date(data.get("invalid_at")) is None:
            findings.append(Finding("ERROR", rel, None, "unparseable 'invalid_at' (ISO date)"))
        if has_sb:
            target = data.get("superseded_by")
            if not isinstance(target, str):
                findings.append(Finding("ERROR", rel, None, "'superseded_by' must be a single value"))
            else:
                target_real = _record_ref_realpath(root, target)
                if target_real is None or target_real not in record_realpaths:
                    findings.append(Finding(
                        "ERROR", rel, None,
                        "dangling 'superseded_by' pointer (must be a repo-relative "
                        "path resolving to a memory record): %s" % target))

    # index cross-check: live records must appear in their memory/_index.md
    for abspath in iter_files(root, load_gitignore(root)):
        if os.path.basename(abspath) != "_index.md":
            continue
        rel = os.path.relpath(abspath, root).replace("\\", "/")
        if "memory" not in rel.split("/"):
            continue
        mem_dir = os.path.dirname(abspath)
        index_text, idx_findings = _read_utf8(abspath, rel)
        findings += idx_findings
        if index_text is None:
            continue
        linked = {os.path.normpath(os.path.join(mem_dir, t.split("#", 1)[0]))
                  for t in _LINK.findall(index_text)
                  if not t.startswith(("http://", "https://", "mailto:", "#"))}
        for rec in records:
            if rec in symlinked:
                continue  # already an ERROR in the record pass
            if os.path.dirname(rec) != mem_dir and not rec.startswith(mem_dir + os.sep):
                continue
            data, _discard = _load_frontmatter(rec, os.path.relpath(rec, root))
            if data is None:
                continue  # unreadable — already reported in the record pass
            if data.get("provenance") == "superseded":
                continue  # history, silent
            if os.path.normpath(rec) not in linked:
                findings.append(Finding("WARN", os.path.relpath(rec, root), None,
                                        "live record not in the index (dark, not lying)"))
    return findings


# Explicit unanswered values must not satisfy a safety invariant: a generated
# worksheet that writes `human_appeal: none` has NOT provided an appeal path.
_PLACEHOLDERS = {"none", "n/a", "na", "tbd", "todo", "unknown", "pending", "-", "?"}


def _answered(v):
    """A present, single-valued, non-placeholder answer. A list defeats
    one-owner accountability; quoting or formatting a placeholder (\"TBD\",
    **TBD**, # TODO, `none`) does not answer it."""
    if not isinstance(v, str):
        return False
    s = v.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1]
    s = s.strip().strip("*_`#> \t").strip()
    return s != "" and s.lower() not in _PLACEHOLDERS


# Multiline HTML comments (template leftovers) render nothing: neither a
# commented-out heading nor the comment delimiters count as rule content.
_HTML_COMMENT = re.compile(r"<!--.*?(?:-->|\Z)", re.S)


_SEPARATOR_LINE = re.compile(r"[-*_=]{3,}")


def _substantive_line(ln):
    """A body line that carries actual rule content: not blank, not a heading,
    not a horizontal rule, not an HTML comment, not a bare placeholder."""
    s = ln.strip()
    if not s or s.startswith("#") or _SEPARATOR_LINE.fullmatch(s):
        return False
    if s.startswith("<!--") and s.endswith("-->"):
        return False
    return s.strip("*_ \t").lower() not in _PLACEHOLDERS


# The four owned governance objects of §5.1 minus the rule statement itself
# (the H1 + body, checked separately) and the top-level `owner` (checked with
# its own message). Required in full once a rule is active (rung-placed).
_RULE_OBJECT_FIELDS = ["value", "value_owner", "runtime_check", "runtime_check_owner",
                       "human_appeal", "human_appeal_owner"]
_H1 = re.compile(r"^# \S", re.MULTILINE)


def check_constitution(root, ignore=()):
    """#8 typed-rule checks. Strict where a rule backs a safety invariant; WARN on
    incomplete thinking. The runnable hook set is a separate artifact (Slice 1.5b).
    Honors the same .gitignore patterns as the generic walker."""
    findings = []
    base = os.path.join(root, "governance", "constitution")
    if not os.path.isdir(base):
        return findings
    if _ignored("governance", ignore) or _ignored("constitution", ignore):
        return findings
    today = datetime.date.today()
    for name in sorted(os.listdir(base)):
        if not name.endswith(".md") or name in {"README.md", "_index.md"} \
                or _ignored(name, ignore):
            continue
        abspath = os.path.join(base, name)
        rel = os.path.relpath(abspath, root)
        text, rd_findings = _read_utf8(abspath, rel)
        findings += rd_findings
        if text is None:
            continue
        data, body, fm = _frontmatter_and_body(text, rel)
        findings += fm

        # Only the provisioning requirements (owner + the full four-object
        # schema) wait for a rung (#6/#8: incomplete is fine while drafting).
        # The safety-spine checks below run on drafts too — a high-risk draft
        # with no appeal path must not leave the gate green.
        rung = data.get("rung")
        active = not _blank(rung)
        if not active:
            findings.append(Finding("WARN", rel, None, "rule not yet placed on a rung (draft)"))
        else:
            if not (isinstance(rung, str) and rung in RUNGS):
                findings.append(Finding("ERROR", rel, None,
                                        "invalid rung %r (one of %s)" % (rung, sorted(RUNGS))))
            owner = data.get("owner")
            if _blank(owner):
                findings.append(Finding("ERROR", rel, None, "active rule has no owner"))
            elif not isinstance(owner, str):
                findings.append(Finding("ERROR", rel, None, "'owner' must be a single value"))
            elif not _answered(owner):
                findings.append(Finding("ERROR", rel, None,
                                        "active rule owner is a placeholder, not an answer"))
            for field in _RULE_OBJECT_FIELDS:
                v = data.get(field)
                if _blank(v):
                    findings.append(Finding("ERROR", rel, None,
                                            "active rule missing '%s' (four objects / four owners)" % field))
                elif not isinstance(v, str):
                    findings.append(Finding("ERROR", rel, None,
                                            "'%s' must be a single value" % field))
                elif not _answered(v):
                    findings.append(Finding("ERROR", rel, None,
                                            "'%s' is a placeholder, not an answer" % field))
            # the rule statement is the H1 plus a substantive body, not a bare
            # title over placeholders, separators, or comments
            rendered = _HTML_COMMENT.sub("", body)
            if _H1.search(rendered) is None or not any(
                    _substantive_line(ln) for ln in rendered.split("\n")):
                findings.append(Finding("ERROR", rel, None,
                                        "active rule has no rule statement (H1 title + body)"))

        # action_class drives the no-rung-six invariant, so it cannot be
        # optional: a rule that omits it would bypass the safety spine.
        ac = data.get("action_class")
        if _blank(ac):
            findings.append(Finding(
                "ERROR" if active else "WARN", rel, None,
                "missing 'action_class' (one of %s)" % sorted(ACTION_CLASSES)))
        elif not (isinstance(ac, str) and ac in ACTION_CLASSES):
            findings.append(Finding("ERROR", rel, None,
                                    "invalid action_class %r (one of %s)" % (ac, sorted(ACTION_CLASSES))))
        if isinstance(ac, str) and ac == "high-risk" \
                and not (_answered(data.get("human_appeal")) and _answered(data.get("human_appeal_owner"))):
            findings.append(Finding("ERROR", rel, None,
                                    "high-risk rule must carry a human-appeal path with an owner "
                                    "(there is no rung six)"))
        sunset = data.get("sunset")
        if _blank(sunset):
            findings.append(Finding("WARN", rel, None, "missing sunset date"))
        else:
            sd = _parse_date(sunset)
            if sd is None:
                findings.append(Finding("WARN", rel, None,
                                        "'sunset' is not an ISO date (YYYY-MM-DD)"))
            elif sd < today:
                findings.append(Finding("WARN", rel, None, "sunset date has passed"))

        # `repeals: none` is an explicit no-repeal answer, not a repeal; a
        # non-empty list of repealed rituals declares one.
        repeals = data.get("repeals")
        repeal_declared = bool(repeals) if isinstance(repeals, list) else _answered(repeals)
        if repeal_declared:
            if not _answered(data.get("surviving_job")) or not _answered(data.get("reassigned_to")):
                findings.append(Finding("ERROR", rel, None,
                                        "orphan-prohibition: a repealed ritual's surviving job must be "
                                        "reassigned ('surviving_job' + 'reassigned_to') before the repeal ships"))
    return findings


_PROV_FORWARD = {
    "observed": {"observed", "confirmed", "superseded"},
    "inferred": {"inferred", "confirmed", "superseded"},
    "confirmed": {"confirmed", "superseded"},
    "superseded": {"superseded"},
}


def _frontmatter_and_body(text, path="<unknown>"):
    data, findings = parse_frontmatter(text, path)
    lines = text.split("\n")
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return data, "\n".join(lines[i + 1:]), findings
    return data, text, findings


def _as_list(v):
    if v is None or v == []:
        return []
    return v if isinstance(v, list) else [v]


def _source_append_only(old_src, new_src):
    """Append-only: every existing entry is preserved in order; only the FINAL
    existing entry may be extended in place (a scalar source grows by suffix);
    new entries may follow. Removal or alteration of earlier entries fails."""
    if not old_src:
        return True
    return (len(new_src) >= len(old_src)
            and new_src[:len(old_src) - 1] == old_src[:-1]
            and new_src[len(old_src) - 1].startswith(old_src[-1]))


def check_memory_diff(old_text, new_text, path):
    """#7 immutability rules between a record's base version and its new version.
    Pure (no git). All findings are ERROR — an immutable field changed.
    Line endings are normalized first (a git blob keeps CRLF as committed while
    text-mode reads translate it), and edge whitespace around the body is
    tolerated — whitespace-only differences are not treated as edits."""
    findings = []
    old_text = old_text.replace("\r\n", "\n").replace("\r", "\n")
    new_text = new_text.replace("\r\n", "\n").replace("\r", "\n")
    old_fm, old_body, _old_parse = _frontmatter_and_body(old_text, path)
    new_fm, new_body, new_parse = _frontmatter_and_body(new_text, path)
    # Malformed NEW frontmatter (e.g. a duplicate provenance key) fails closed
    # here — the diff layer may be the only gate that sees this record. The old
    # side is committed history; its shape was the stateless gate's job.
    findings += [f for f in new_parse if f.level == "ERROR"]

    if old_body.strip() != new_body.strip():
        findings.append(Finding("ERROR", path, None, "immutable: body changed (frozen at commit)"))
    if old_fm.get("valid_at") != new_fm.get("valid_at"):
        findings.append(Finding("ERROR", path, None, "immutable: valid_at changed (frozen at commit)"))

    op, np = old_fm.get("provenance"), new_fm.get("provenance")
    if isinstance(op, str) and op in _PROV_FORWARD and (
            not isinstance(np, str) or np not in _PROV_FORWARD[op]):
        # a removed/blank/non-scalar new label is as illegal as a downgrade
        findings.append(Finding("ERROR", path, None,
                                "provenance downgrade / illegal transition: %s -> %r (forward only)" % (op, np)))

    old_src, new_src = _as_list(old_fm.get("source")), _as_list(new_fm.get("source"))
    if not _source_append_only(old_src, new_src):
        findings.append(Finding("ERROR", path, None,
                                "source is append-only (existing entries cannot be altered or removed)"))

    for field in ("invalid_at", "superseded_by"):
        ov = old_fm.get(field)
        if not _blank(ov) and new_fm.get(field) != ov:
            findings.append(Finding("ERROR", path, None,
                                    "supersession field '%s' is set once and cannot change" % field))
    return findings


def load_gitignore(root):
    """Minimal .gitignore reader: exact names and simple globs (e.g. '*.log').
    Enough to skip .env-style files so the gate scans (roughly) what's tracked.
    NOT full git ignore semantics (no negation, nesting, or path anchoring) —
    documented in docs/known-limitations.md."""
    patterns = set()
    gi = os.path.join(root, ".gitignore")
    if os.path.isfile(gi):
        with open(gi, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line.rstrip("/"))
    return patterns


def _ignored(name, patterns):
    return any(fnmatch.fnmatch(name, p) for p in patterns)


def iter_files(root, ignore=()):
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")
                       and os.path.normpath(os.path.join(rel_dir, d)) not in SKIP_RELPATHS
                       and not _ignored(d, ignore)]
        for fn in filenames:
            if _ignored(fn, ignore):
                continue
            yield os.path.join(dirpath, fn)


def validate(root):
    """Walk root, run every check, return a flat list[Finding]."""
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        return [Finding("ERROR", root, None, "root does not exist or is not a directory")]
    findings = []
    ignore = load_gitignore(root)
    for abspath in iter_files(root, ignore):
        rel = os.path.relpath(abspath, root)
        try:
            with open(abspath, "rb") as fh:
                data_bytes = fh.read()
        except OSError:
            continue
        findings += check_context_budget(rel, data_bytes)
        try:
            text = data_bytes.decode("utf-8")
        except UnicodeDecodeError:
            continue
        findings += check_secrets(text, rel)
        findings += check_entropy(text, rel)
        if abspath.endswith(".md"):
            findings += check_links(abspath, text, root)
    findings += check_ontology(root, ignore)
    findings += check_owner_cards(root, ignore)
    findings += check_memory(root)
    findings += check_constitution(root, ignore)
    return findings


def _diff_in_workbench_skips(rel_from_root):
    """Mirror iter_files' directory skips (SKIP_DIRS, dot-dirs, SKIP_RELPATHS)
    for a base-tree path, so the diff scope matches the stateless walker's —
    deliberately WITHOUT .gitignore: ignoring a committed record must not
    waive its immutability."""
    dirs = rel_from_root.split("/")[:-1]
    if any(d in SKIP_DIRS or d.startswith(".") for d in dirs):
        return True
    skip_rel = {p.replace(os.sep, "/") for p in SKIP_RELPATHS}
    return any("/".join(dirs[:i + 1]) in skip_rel for i in range(len(dirs)))


def _committed_path_status(toplevel, parts, cache=None):
    """Walk toplevel/parts verifying each component exists under its EXACT
    committed name (a case-folding filesystem cannot hide a case-only rename
    of a record or any ancestor directory) and that no component is a symlink
    (a symlinked memory folder or record must not stand in for the committed
    one). Names are NFC-normalized on both sides — git core.precomposeunicode
    reports NFC while a mac filesystem may list NFD, and that mismatch must
    not fake a deletion. Returns 'ok', 'symlink', or 'missing'. Pass a dict as
    `cache` to reuse directory listings across records. Check-then-open is not
    atomic — a concurrent writer race is a documented non-goal
    (docs/known-limitations.md)."""
    if cache is None:
        cache = {}
    p = toplevel
    for part in parts:
        if p not in cache:
            try:
                cache[p] = {unicodedata.normalize("NFC", e) for e in os.listdir(p)}
            except OSError:
                cache[p] = None
        entries = cache[p]
        if entries is None or unicodedata.normalize("NFC", part) not in entries:
            return "missing"
        p = os.path.join(p, part)
        if os.path.islink(p):
            return "symlink"
    return "ok" if os.path.isfile(p) else "missing"


def memory_diff_findings(root, base):
    """Compare memory records that existed at <base> (a git ref) against the
    working tree. Scoped to memory folders under root. New records are fine;
    deletions and immutable-field edits are ERRORs. Driven by the BASE file
    list, so no working-tree skip can exempt a committed record."""
    try:
        # bytes + os.fsdecode: survives locale-undecodable repo paths; and
        # --show-prefix gives root's repo-relative path in git's canonical
        # casing, so a case-variant invocation cannot blind the scope filter
        rp = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel", "--show-prefix"],
                            capture_output=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [Finding("ERROR", root, None, "--diff requires a git repository")]
    rp_lines = os.fsdecode(rp).splitlines()
    if len(rp_lines) != 2 or not os.path.isdir(rp_lines[0]):
        # a newline/CR inside the repo path mis-splits this output; a wrong
        # scope would fail open, so refuse instead
        return [Finding("ERROR", root, None,
                        "--diff could not resolve the repository layout (unsupported path)")]
    toplevel = rp_lines[0]
    scope = rp_lines[1].strip("/") or "."
    try:
        subprocess.run(["git", "-C", toplevel, "rev-parse", "--verify", "--quiet",
                        "%s^{commit}" % base], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        # a typo'd base must not report a clean bill of health
        return [Finding("ERROR", root, None, "--diff base ref not found: %s" % base)]
    try:
        # -z: NUL-terminated, unquoted paths (immune to core.quotePath mangling
        # of non-ASCII names); os.fsdecode round-trips odd bytes losslessly
        raw = subprocess.run(["git", "-C", toplevel, "ls-tree", "-r", "--name-only", "-z", base],
                             capture_output=True, check=True).stdout
    except subprocess.CalledProcessError:
        return [Finding("ERROR", root, None, "--diff could not list the base tree for %s" % base)]
    findings = []
    listdir_cache = {}
    for bf in (os.fsdecode(b) for b in raw.split(b"\0") if b):
        if scope != "." and not bf.startswith(scope + "/"):
            continue
        parts = bf.split("/")
        if "memory" not in parts or not bf.endswith(".md") \
                or parts[-1] in {"_index.md", "README.md"}:
            continue
        rel = bf if scope == "." else bf[len(scope) + 1:]
        if _diff_in_workbench_skips(rel):
            continue
        abspath = os.path.join(toplevel, *parts)
        status = _committed_path_status(toplevel, parts, listdir_cache)
        if status == "symlink":
            findings.append(Finding("ERROR", bf, None,
                                    "memory record is or sits behind a symlink (cannot verify immutability)"))
            continue
        if status == "missing":
            findings.append(Finding("ERROR", bf, None,
                                    "memory record deleted (records are superseded, never deleted)"))
            continue
        show = subprocess.run(["git", "-C", toplevel, "show", "%s:%s" % (base, bf)],
                              capture_output=True)
        if show.returncode != 0:
            # the base LIST says it exists, so a fetch failure is never "new" —
            # fail closed rather than silently passing
            findings.append(Finding("ERROR", bf, None,
                                    "--diff could not read the base version of this record"))
            continue
        try:
            old = show.stdout.decode("utf-8")
        except UnicodeError:
            findings.append(Finding("ERROR", bf, None,
                                    "cannot verify immutability: base version is not valid UTF-8"))
            continue
        try:
            with open(abspath, encoding="utf-8") as fh:
                new = fh.read()
        except (UnicodeError, OSError):
            findings.append(Finding("ERROR", rel, None,
                                    "cannot verify immutability: working-tree record is unreadable or not valid UTF-8"))
            continue
        findings += check_memory_diff(old, new, rel)
    return findings


def main(argv):
    args = argv[1:]
    diff_base = None
    if "--diff" in args:
        i = args.index("--diff")
        if i + 1 >= len(args):
            print("ERROR  --diff requires a <base> git ref")
            return 2
        diff_base = args[i + 1]
        args = args[:i] + args[i + 2:]
    root = args[0] if args else "."
    findings = validate(root)
    if diff_base is not None:
        findings += memory_diff_findings(root, diff_base)
    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]
    for f in findings:
        loc = f.path + ((":%d" % f.line) if f.line else "")
        print("%-5s %s  %s" % (f.level, loc, f.message))
    print("\n%d error(s), %d warning(s)" % (len(errors), len(warns)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
