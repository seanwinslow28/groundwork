#!/usr/bin/env python3
"""groundwork validator — Python stdlib only (zero third-party deps, enforced).

Walks a repo tree and reports ERROR/WARN Findings. ERROR fails the gate.
Schema-specific checks (#5/#6/#7/#8) live in a later build slice; this module
is the generic foundation: frontmatter parsing, secrets, context budget,
referential integrity.
"""
import math
import os
import re
import sys
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


def iter_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")
                       and os.path.normpath(os.path.join(rel_dir, d)) not in SKIP_RELPATHS]
        for fn in filenames:
            yield os.path.join(dirpath, fn)


def validate(root):
    """Walk root, run every check, return a flat list[Finding]."""
    root = os.path.abspath(root)
    if not os.path.isdir(root):
        return [Finding("ERROR", root, None, "root does not exist or is not a directory")]
    findings = []
    for abspath in iter_files(root):
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
    return findings


def main(argv):
    root = argv[1] if len(argv) > 1 else "."
    findings = validate(root)
    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]
    for f in findings:
        loc = f.path + ((":%d" % f.line) if f.line else "")
        print("%-5s %s  %s" % (f.level, loc, f.message))
    print("\n%d error(s), %d warning(s)" % (len(errors), len(warns)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
