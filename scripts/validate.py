#!/usr/bin/env python3
"""groundwork validator — Python stdlib only (zero third-party deps, enforced).

Walks a repo tree and reports ERROR/WARN Findings. ERROR fails the gate.
Schema-specific checks (#5/#6/#7/#8) live in a later build slice; this module
is the generic foundation: frontmatter parsing, secrets, context budget,
referential integrity.
"""
import datetime
import fnmatch
import json
import math
import os
import re
import shlex
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

SCHEMA_VERSION = 1  # bumped ONLY on a breaking schema change (#21). Never on additive commits.


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


def check_context_budget(path, num_bytes):
    """#13 thresholds over a measured byte count. Bytes are what a stdlib
    validator can compute deterministically; tokens are reported (len/4). This
    is applied to the ALWAYS-LOADED aggregate, not to arbitrary files — a Python
    script or a research note never enters an agent's context."""
    toks = est_tokens(num_bytes)
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


# Codex: "stops adding files once the combined size reaches the limit defined by
# project_doc_max_bytes (32 KiB by default)" — and truncates SILENTLY (no warning;
# openai/codex#7138 closed not-planned). Verified live 2026-07-27.
AGENTS_CHAIN_MAX_BYTES = 32 * 1024
# Claude Code: imports resolve "with a maximum depth of four hops".
CLAUDE_IMPORT_MAX_DEPTH = 4
# Claude Code truncates a skill's listed description at this many characters.
SKILL_DESCRIPTION_CAP = 1536
# Codex checks AGENTS.override.md before AGENTS.md at every level.
_AGENTS_NAMES = ("AGENTS.override.md", "AGENTS.md")

_IMPORT = re.compile(r"(?:(?<=\s)|^)@([^\s`]+)", re.M)
# The installed consumer's leading-front-matter regex, mirrored verbatim:
# /^---\s*\n([\s\S]*?)---\s*\n?/ (the closer may sit mid-line). Its \s is
# ECMAScript's, which is NEITHER a subset nor a superset of Python's (JS has
# U+FEFF; Python additionally has U+0085 and U+001C-001F) — so the class is
# spelled out and used on BOTH sides of every comparison (Codex round 23).
_ES_WS_CHARS = ("\t\n\x0b\f\r \u00a0\u1680"
                "\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007"
                "\u2008\u2009\u200a\u2028\u2029\u202f\u205f\u3000"
                "\ufeff")
_ES_WS_CLASS = "[" + re.escape(_ES_WS_CHARS) + "]"
_FRONT_MATTER = re.compile(
    "---{0}*\\n[\\s\\S]*?---{0}*\\n?".format(_ES_WS_CLASS))


def _es_strip(s):
    """Strip ECMAScript whitespace only — Python's str.strip() removes more
    (U+001C-001F, U+0085), which the consumer would keep inside an import
    target."""
    return s.strip(_ES_WS_CHARS)


_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_TICKS = re.compile(r"`+")
# Block-container markers a fence can nest under: blockquote, bullet, ordered.
# A list marker may be followed by 1-4 spaces (all part of the item's
# continuation width) or by end of line (an EMPTY item — content starts on the
# next line at marker width + 1). Codex round 7.
_CONTAINER = re.compile(r"^ {0,3}(> ?|(?:[-*+]|\d{1,9}[.)])(?: {1,4}|(?=$)))")
# Non-paragraph leaf starts: an ATX heading or a thematic break cannot host
# lazy continuation and interrupts a paragraph (Codex round 12). A thematic
# break also outranks list-marker interpretation ('- - -' is a break, not
# nested items — CommonMark precedence).
_ATX_HEADING = re.compile(r" {0,3}#{1,6}(?:[ \t]|$)")
_THEMATIC = re.compile(r" {0,3}(?:(?:\* *){3,}|(?:- *){3,}|(?:_ *){3,})[ \t]*$")
# A setext underline (only meaningful while a paragraph is open) turns the
# paragraph into a heading and closes it; it can never be lazy continuation.
_SETEXT = re.compile(r" {0,3}(?:=+|-+)[ \t]*$")
# HTML blocks (Codex rounds 13-15): a fence-looking line inside one is raw
# HTML content, not a fence. Types 1-5 run THROUGH blank lines and end on a
# line containing their end marker (which may be the opening line itself);
# type 6 (the CommonMark block-tag list, open or close) and type 7 (any
# complete tag ALONE on the line, and only outside a paragraph) run to the
# next blank line. Every type but 7 interrupts a paragraph, and every type
# ends when its containing block (list item / quote) ends.
_HTML1_START = re.compile(r" {0,3}<(?:script|pre|style|textarea)(?:[ \t>]|$)",
                          re.I)
_HTML1_END = re.compile(r"</(?:script|pre|style|textarea)>", re.I)
_HTML2_START = re.compile(r" {0,3}<!--")
_HTML2_END = re.compile(r"-->")
_HTML3_START = re.compile(r" {0,3}<\?")
_HTML3_END = re.compile(r"\?>")
_HTML4_START = re.compile(r" {0,3}<![A-Za-z]")
_HTML4_END = re.compile(r">")
_HTML5_START = re.compile(r" {0,3}<!\[CDATA\[")
_HTML5_END = re.compile(r"\]\]>")
_HTML6_START = re.compile(r" {0,3}</?([A-Za-z][A-Za-z0-9-]*)(?:[ \t>]|/>|$)")
_HTML7_LINE = re.compile(
    r" {0,3}(?:<[A-Za-z][A-Za-z0-9-]*"
    r"(?:\s+[A-Za-z_:][A-Za-z0-9_.:-]*"
    r"(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+))?)*"
    r"\s*/?>|</[A-Za-z][A-Za-z0-9-]*\s*>)[ \t]*$")
_HTML6_TAGS = frozenset("""address article aside base basefont blockquote
    body caption center col colgroup dd details dialog dir div dl dt fieldset
    figcaption figure footer form frame frameset h1 h2 h3 h4 h5 h6 head
    header hr html iframe legend li link main menu menuitem nav noframes ol
    optgroup option p param search section summary table tbody td tfoot th
    thead title tr track ul""".split())
_QUOTE_MARK = re.compile(r"^ {0,3}> ?")


def _fence_match(line):
    """A _FENCE match honoring CommonMark's backtick rule: a backtick fence's
    info string cannot contain a backtick. None when the line is not a fence."""
    m = _FENCE.match(line)
    if m and m.group(1)[0] == "`" and "`" in m.group(2):
        return None
    return m


def _new_markers(line):
    """Strip the container markers a line itself carries. Returns (chain,
    rest, code): each chain entry ("quote", 0) or ("list",
    continuation_columns). A list marker followed by 1-4 spaces continues at
    the columns the whole marker occupied. Followed by 5+ spaces (the item
    starts with indented CODE) or by end of line (an empty item), continuation
    resets to the bare marker's width + 1 — CommonMark's rule, and getting it
    wrong made a genuine fence at that indent read as live text (Codex rounds
    7-8). `code` is True when the rest is indented-code content: it is live
    text, never a fence opener — fence-matching it would let the NEXT genuine
    fence read as its closer and expose what that fence contains (round 9)."""
    chain = []
    while True:
        m = _CONTAINER.match(line)
        if not m:
            return chain, line, False
        g = m.group(1)
        end = m.end()
        rest = line[end:]
        if g.startswith(">"):
            chain.append(("quote", 0))
            line = rest
            continue
        marker_end = end - (len(g) - len(g.rstrip(" ")))
        if rest.startswith(" "):
            # 5+ spaces after the marker: the rest is indented-code content,
            # not further markers and not a fence
            chain.append(("list", marker_end + 1))
            return chain, rest, True
        if end == len(line):
            chain.append(("list", marker_end + 1))
            return chain, rest, False
        chain.append(("list", end))
        line = rest


def _consume(chain, line):
    """Consume as much of `chain`'s continuation prefix as the line offers, in
    order. Returns (count, rest). A quote continues via its '>' marker; a list
    item continues via its continuation columns (tabs already expanded). The
    ORDERED chain is what makes nesting come out right (Codex rounds 5-6):
    quote depth alone missed list boundaries, list-then-quote continuation
    indent, and a fence line that carries only its item's indentation."""
    count = 0
    for kind, width in chain:
        if kind == "quote":
            m = _QUOTE_MARK.match(line)
            if not m:
                break
            line = line[m.end():]
        else:
            consumed = 0
            while consumed < width and consumed < len(line) \
                    and line[consumed] == " ":
                consumed += 1
            if consumed < width:
                break
            line = line[consumed:]
        count += 1
    return count, line


def _strip_spans(text):
    """Remove inline code spans: a run of N backticks closed by the NEXT run of
    EXACTLY N (CommonMark — a longer run's tail is not a closer, which the old
    find()-based scan got wrong). An unterminated run is literal text and is
    kept. `text` is one paragraph; a span may cross line endings within it.

    Each stripped span leaves a single backtick behind: bare removal would join
    the span's neighbors into a new token, so stripping "@`doc:\\n`AGENTS.md"
    would SYNTHESIZE "@AGENTS.md" and satisfy the drift check while Claude Code
    imported nothing (fail-open). A backtick placeholder is safe in both
    directions — _IMPORT targets cannot start with one and an @ preceded by one
    is not an import — so ambiguity still resolves toward a loud false ERROR."""
    runs = [(m.start(), m.end()) for m in _TICKS.finditer(text)]
    out = []
    pos = 0
    ri = 0
    while ri < len(runs):
        start, end = runs[ri]
        n = end - start
        close = next((rj for rj in range(ri + 1, len(runs))
                      if runs[rj][1] - runs[rj][0] == n), None)
        if close is None:
            ri += 1
            continue
        out.append(text[pos:start])
        out.append("`")
        pos = runs[close][1]
        ri = close + 1
    out.append(text[pos:])
    return "".join(out)


def _strip_code(text):
    """Blank out fenced code blocks and inline code spans, the way a CommonMark
    reader does — Claude Code's import parser "skips Markdown code spans and
    fenced code blocks".

    Why a scanner and not a regex: a regex that knows only ``` fences fails
    OPEN. An `@AGENTS.md` inside a ~~~ block would be read as a real import, so
    a CLAUDE.md that merely *documents* the import would satisfy the root-file
    drift check while Claude Code loaded nothing.

    Deliberate bias: when the two consumers disagree, OVER-strip. Missing a real
    import makes the drift check ERROR (loud, safe); seeing a fake one makes it
    pass (silent drift). The cost is that a backslash-escaped backtick reads as
    opening a span — documented in docs/known-limitations.md.

    Spans are matched within a PARAGRAPH (a run of non-blank, non-fence lines):
    a CommonMark code span may cross line endings, so per-line scanning would
    fail open on a multiline span, while a blank line ends the paragraph and no
    span crosses it.

    Fences nested in block containers (`> ~~~`, `- ```` ``` ````) are fences
    too. A fence opened inside a blockquote closes when the quote's `>` lines
    stop (a code block cannot lazily continue), and the ending line is
    reprocessed — it may itself open a new top-level fence."""
    out = []
    para = []  # non-fence lines accumulated until a paragraph boundary

    def _flush():
        if para:
            out.append(_strip_spans("\n".join(para)))
            del para[:]

    fence = None   # (char, length) of the currently open fence
    f_chain = []   # ordered containers the open fence sits in
    ctx = []       # containers opened by EARLIER lines, still open.
    # ctx tracks CommonMark block structure across lines (Codex round 6): a
    # fence line inside an item may carry only indentation. Blank lines and
    # lazy paragraph continuation keep ctx alive; a dedented line after
    # anything else ends the unconsumed containers (round 10: keeping a stale
    # list context turned top-level indented code into a false fence whose
    # 'closer' consumed a genuine fence opener — a silent fail-open).
    para_open = False  # the previous line was paragraph text (lazy-continuable)
    html_open = None   # "blank": HTML block until a blank; regex: until its end
    h_chain = []       # containers the open HTML block sits in
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        # tabs participate in CommonMark block structure at a tab stop of 4
        line = lines[i].expandtabs(4)
        if fence is None:
            if not line.strip():
                _flush()
                out.append(line)
                para_open = False
                if html_open == "blank":
                    html_open = None  # types 6/7 end at a blank; 1-5 span it
                i += 1
                continue
            if html_open is not None:
                cnt, _r = _consume(h_chain, line)
                if cnt < len(h_chain):
                    # the containing block ended, and the HTML block with it —
                    # reprocess this line outside it
                    html_open = None
                    continue
                # raw HTML-block content — live text, never a fence opener
                para.append(line)
                if html_open != "blank" and html_open.search(line):
                    html_open = None
                i += 1
                continue
            cnt, rest = _consume(ctx, line)
            html_end = None
            if _THEMATIC.match(rest) or (para_open and _SETEXT.match(rest)):
                new, code = [], False
                block_start = True
            else:
                new, rest, code = _new_markers(rest)
                block_start = bool(_ATX_HEADING.match(rest)) or \
                    bool(_THEMATIC.match(rest))
                if not code and not block_start:
                    if _HTML1_START.match(rest):
                        html_end = _HTML1_END
                    elif _HTML2_START.match(rest):
                        html_end = _HTML2_END
                    elif _HTML5_START.match(rest):
                        html_end = _HTML5_END
                    elif _HTML4_START.match(rest):
                        html_end = _HTML4_END
                    elif _HTML3_START.match(rest):
                        html_end = _HTML3_END
                    else:
                        h6 = _HTML6_START.match(rest)
                        if h6 and h6.group(1).lower() in _HTML6_TAGS:
                            html_end = "blank"
                        elif not para_open and _HTML7_LINE.match(rest):
                            html_end = "blank7"
                # every type but 7 interrupts a paragraph (7 is only
                # recognized outside one)
                block_start = block_start or \
                    (html_end is not None and html_end != "blank7")
            # fence recognition comes BEFORE the lazy check: fenced code —
            # like a heading or thematic break — interrupts a paragraph, so
            # none of them is ever lazy text
            m = None if code else _fence_match(rest)
            if m is None and not block_start and cnt < len(ctx) \
                    and not new and para_open:
                # lazy continuation: a paragraph line may continue the open
                # containers without their prefix — plain text, ctx kept
                para.append(line)
                i += 1
                continue
            if cnt < len(ctx) or new:
                ctx = ctx[:cnt] + new
            if m:
                _flush()
                fence = (m.group(1)[0], len(m.group(1)))
                f_chain = ctx
                para_open = False
                out.append("")
            elif html_end is not None:
                para.append(line)
                para_open = False
                if html_end in ("blank", "blank7"):
                    html_open = "blank"
                    h_chain = ctx
                elif html_end.search(rest):
                    pass  # end condition met on the opening line itself
                else:
                    html_open = html_end
                    h_chain = ctx
            else:
                para.append(line)
                # a paragraph is open only when this line can host lazy
                # continuation: not a heading or thematic break, not
                # indented-code content (the 5+-space marker case or, outside
                # a paragraph, a 4+-column rest), and not a blank-content
                # marker-only line
                para_open = (not code) and (not block_start) and \
                    bool(rest.strip()) and \
                    (para_open or not rest.startswith("    "))
            i += 1
            continue
        # A blank line is fence content unless a blockquote in the chain ends
        # at it (a blank ends a quote, but not a fenced block in a list item).
        if not line.strip() and not any(k == "quote" for k, _w in f_chain):
            out.append("")
            i += 1
            continue
        # Container termination comes BEFORE closer matching (Codex rounds
        # 4-5): a line that fails to continue every container the fence was
        # opened under ends that container and the fence with it, and must be
        # REPROCESSED — it may itself open a new fence at a shallower level
        # ('> - ~~~' then '> ~~~' reopens at the quote level; '> ~~~' then
        # bare '~~~' reopens at the top level).
        cnt, rest = _consume(f_chain, line)
        if cnt < len(f_chain):
            fence = None
            continue
        # a closing fence: same character, at least as long, no info string —
        # matched on the rest AFTER the chain's prefix, so '> ```' inside a
        # top-level fence and '> > ```' inside a '> '-deep fence stay content.
        m = _fence_match(rest)
        if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= fence[1] \
                and not m.group(2).strip():
            fence = None
        out.append("")
        i += 1
    _flush()
    return "\n".join(out)


def _agents_file(dirpath):
    """The instruction file Codex would read at this level, honoring the
    override precedence. None when the level contributes nothing."""
    for name in _AGENTS_NAMES:
        p = os.path.join(dirpath, name)
        if os.path.isfile(p):
            return p
    return None


def _file_size(path):
    """Size via an opened descriptor, not a bare stat: a stat-able but
    unreadable file (e.g. mode 000) must read as unmeasurable, not as its
    size — the chain check fails closed on None."""
    try:
        with open(path, "rb") as fh:
            return os.fstat(fh.fileno()).st_size
    except OSError:
        return None


def check_agents_chain(root, ignore=()):
    """#13 hard ERROR. Codex "concatenates files from the root down, joining them
    with blank lines" and stops once the total reaches project_doc_max_bytes
    (32 KiB). Past the cap the tail is silently dropped — that is DATA LOSS, not
    bloat, and no harness warns about it, so the validator is the missing warning.

    Only the repo-side chain is measurable; a user's own ~/.codex/AGENTS.md counts
    against the same 32 KiB and is invisible here (docs/known-limitations.md)."""
    findings = []
    for dirpath, dirnames, _filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")
                       and os.path.normpath(os.path.join(rel_dir, d)) not in SKIP_RELPATHS
                       and not _ignored(d, ignore)]
        leaf = _agents_file(dirpath)
        if leaf is None:
            continue
        parts = [] if rel_dir == "." else rel_dir.split(os.sep)
        sizes = []
        unreadable = None
        for i in range(len(parts) + 1):
            f = _agents_file(os.path.join(root, *parts[:i]))
            if f is None:
                continue
            n = _file_size(f)
            if n is None:
                unreadable = f
                break
            if n:  # "Codex skips empty files"
                sizes.append(n)
        if unreadable is not None:
            findings.append(Finding("ERROR", os.path.relpath(unreadable, root), None,
                                    "cannot size this instruction file — the AGENTS.md chain "
                                    "budget cannot be verified (#13)"))
            continue
        total = sum(sizes) + 2 * max(len(sizes) - 1, 0)  # joined with blank lines
        if total > AGENTS_CHAIN_MAX_BYTES:
            findings.append(Finding(
                "ERROR", os.path.relpath(leaf, root), None,
                "AGENTS.md chain reaching this directory is %d bytes, over Codex's "
                "%d-byte project_doc_max_bytes — everything past the cap is silently "
                "truncated (#13)" % (total, AGENTS_CHAIN_MAX_BYTES)))
    return findings


def _always_loaded_bytes(root):
    """#13's always-loaded surface as (label, bytes) pairs: the root AGENTS.md,
    the root CLAUDE.md and everything it imports, unscoped .claude/rules/*.md,
    always-apply .cursor/rules/*.mdc, and each skill's description capped at
    Claude Code's listing truncation.

    Both rules directories are opened BY PATH on purpose: iter_files skips every
    dot-directory, so a walker-based version would measure nothing and pass.

    Returns (items, findings): a file this check cannot read or parse surfaces
    as a finding rather than being silently dropped from the aggregate —
    nothing else scans dot-directories, so silence here would be fail-open."""
    items = []
    findings = []

    root_real = os.path.realpath(root)
    counted = set()

    def _take(abspath, rel_label, num_bytes):
        """Count a file once. AGENTS.md is reachable both as the root
        instruction file and as CLAUDE.md's import; no harness loads it twice,
        and double-counting can only push a legitimate repo past the ERROR
        threshold."""
        real = os.path.realpath(abspath)
        if real in counted or not num_bytes:
            return False
        counted.add(real)
        items.append((rel_label, num_bytes))
        return True

    # The root instruction file goes into `counted` BEFORE imports are
    # followed, so CLAUDE.md's '@AGENTS.md' import dedupes against it.
    f = _agents_file(root)
    if f is not None:
        n = _file_size(f)
        if n is None:
            findings.append(Finding(
                "ERROR", os.path.relpath(f, root), None,
                "cannot read this instruction file — the always-loaded budget "
                "cannot be verified (#13)"))
        else:
            _take(f, os.path.relpath(f, root), n)

    seen = set()

    # Depth 0 is CLAUDE.md itself; each import edge is one hop, and Claude Code
    # resolves imports "with a maximum depth of four hops" — so a file four
    # edges away still loads and must be counted. Breadth-first on purpose:
    # BFS guarantees the FIRST visit to a file is at its shallowest depth, so
    # a shared import declared late in a deep chain still gets its children
    # expanded when it is also reachable within the hop budget (depth-first
    # with a seen-set would lock in the deep first visit and undercount).
    queue = [(os.path.join(root, "CLAUDE.md"), 0)]
    qi = 0
    while qi < len(queue):
        abspath, depth = queue[qi]
        qi += 1
        if depth > CLAUDE_IMPORT_MAX_DEPTH or not os.path.isfile(abspath):
            continue
        real = os.path.realpath(abspath)
        if real in seen:
            continue
        seen.add(real)
        rel = os.path.relpath(abspath, root)
        text, rd = _read_utf8(abspath, rel)
        findings.extend(rd)
        if text is None:
            continue
        # _take may decline (already counted as the root instruction file);
        # imports are still expanded — the file loads once, but what it
        # imports is real context either way.
        _take(abspath, rel, len(text.encode("utf-8")))
        base = os.path.dirname(abspath)
        for target in _IMPORT.findall(_strip_code(text)):
            if target.startswith("~") or os.path.isabs(target):
                continue  # outside the repo: real context, but not measurable here
            nxt = os.path.normpath(os.path.join(base, target))
            if os.path.realpath(nxt).startswith(root_real + os.sep):
                queue.append((nxt, depth + 1))

    for rel_dir, ext, mode in ((os.path.join(".claude", "rules"), ".md", "claude"),
                               (os.path.join(".cursor", "rules"), ".mdc", "cursor")):
        d = os.path.join(root, rel_dir)
        if not os.path.isdir(d):
            continue

        def _walk_err(exc, _rel=rel_dir):
            # an unlistable rules directory must not silently vanish from
            # the aggregate (fail closed, #13 — Codex round 26)
            findings.append(Finding(
                "ERROR", _rel, None,
                "cannot list this rules directory — the always-loaded "
                "budget cannot be verified (#13)"))

        for dirpath, _dn, filenames in os.walk(d, onerror=_walk_err):
            for fn in sorted(filenames):
                if not fn.endswith(ext):
                    continue
                abspath = os.path.join(dirpath, fn)
                rel = os.path.relpath(abspath, root)
                data, fm = _load_frontmatter(abspath, rel)
                findings.extend(fm)
                if data is None:
                    continue
                if mode == "claude":
                    # path-scoped rules load on file match, not at launch
                    if not _blank(data.get("paths")):
                        continue
                else:
                    aa = data.get("alwaysApply")
                    if not (isinstance(aa, str) and aa.strip().lower() == "true"):
                        continue
                n = _file_size(abspath)
                if n:
                    _take(abspath, rel, n)

    sdir = os.path.join(root, "skills")
    if os.path.isdir(sdir) and not os.path.islink(sdir):
        try:
            names = sorted(os.listdir(sdir))
        except OSError:
            names = []
            findings.append(Finding(
                "ERROR", "skills", None,
                "cannot list the skills directory — the always-loaded "
                "budget cannot be verified (#13)"))
        for name in names:
            sp = os.path.join(sdir, name, "SKILL.md")
            try:
                os.stat(sp)
            except (FileNotFoundError, NotADirectoryError):
                continue
            except OSError:
                # isfile() swallows EACCES, so a mode-000 skill package would
                # silently vanish from the aggregate (Codex round 27)
                findings.append(Finding(
                    "ERROR", os.path.relpath(sp, root), None,
                    "cannot stat this skill — the always-loaded budget "
                    "cannot be verified (#13)"))
                continue
            if not os.path.isfile(sp):
                continue
            rel = os.path.relpath(sp, root)
            data, fm = _load_frontmatter(sp, rel)
            findings.extend(fm)
            if data is None:
                continue
            desc = data.get("description")
            if isinstance(desc, str) and desc.strip():
                # The cap is 1,536 CHARACTERS (Claude Code's listing
                # truncation); truncate characters first, then measure the
                # bytes those characters occupy — a bytes-side min() would
                # undercount multibyte descriptions.
                items.append((rel + " (description)",
                              len(desc[:SKILL_DESCRIPTION_CAP].encode("utf-8"))))
    return items, findings


def check_always_loaded_budget(root):
    """#13's aggregate: what every session pays for before anyone types anything.
    WARN ~20K est. tokens, ERROR ~50K. Skill BODIES are excluded on purpose —
    they load only when a skill is invoked."""
    items, findings = _always_loaded_bytes(root)
    budget = check_context_budget("(always-loaded surface)",
                                  sum(n for _lbl, n in items))
    if budget and items:
        top = ", ".join("%s %dB" % (lbl, n)
                        for lbl, n in sorted(items, key=lambda it: -it[1])[:3])
        f = budget[0]
        budget[0] = Finding(f.level, f.path, f.line, f.message + " — largest: " + top)
    return findings + budget


def check_root_files(root):
    """§6 root-file set. AGENTS.md is canonical. Claude Code reads CLAUDE.md and
    NOT AGENTS.md (verified live 2026-07-27), so CLAUDE.md must point at it —
    either the documented '@AGENTS.md' import or a symlink resolving to it.
    Two root files that each look canonical are two sources of truth, and that
    drift is exactly what this catches. Silent when there is no AGENTS.md."""
    findings = []
    agents = os.path.join(root, "AGENTS.md")
    if not os.path.isfile(agents):
        return findings

    claude = os.path.join(root, "CLAUDE.md")
    if not os.path.lexists(claude):
        findings.append(Finding(
            "ERROR", "CLAUDE.md", None,
            "AGENTS.md is present but CLAUDE.md is missing — Claude Code reads CLAUDE.md, "
            "not AGENTS.md; add a CLAUDE.md whose content is '@AGENTS.md' (§6)"))
    elif os.path.islink(claude):
        if os.path.realpath(claude) != os.path.realpath(agents):
            findings.append(Finding(
                "ERROR", "CLAUDE.md", None,
                "CLAUDE.md is a symlink that does not resolve to AGENTS.md — the root files "
                "have drifted into separate sources of truth (§6)"))
    else:
        text, rd = _read_utf8(claude, "CLAUDE.md")
        findings += rd
        if text is not None:
            # This ERROR-level guarantee is satisfied ONLY when the FIRST
            # non-blank line after optional YAML front matter is the
            # standalone canonical '@AGENTS.md' at under 4 columns of indent
            # (Codex rounds 15-20: any construct ABOVE the line can change
            # its token — code, HTML, comments, multiline link/image/
            # definition destinations — and betting on token classification
            # keeps losing. With nothing above it, the line is a paragraph,
            # or a heading if underlined, and both are import-scanned under
            # every reading; 4+ columns would be an indented code token).
            # Front matter is stripped with the CONSUMER'S OWN regex (Codex
            # rounds 21-22): /^---\s*\n([\s\S]*?)---\s*\n?/ — the closer may
            # sit MID-LINE ('key: ---'), so no line-based reading can mirror
            # it. The regex uses the explicit ECMAScript whitespace class
            # (_ES_WS_CHARS — neither a subset nor a superset of Python's
            # \s), so the boundary lands exactly where the consumer's does. No match (unclosed) strips nothing, and the
            # literal '---' fails the first-content-line test below.
            fm = _FRONT_MATTER.match(text)
            body = text[fm.end():] if fm else text
            satisfied = False
            for ln in body.split("\n"):
                x = ln.expandtabs(4)
                if not _es_strip(x):
                    continue
                satisfied = _es_strip(x) == "@AGENTS.md" and \
                    not x.startswith("    ")
                break
            if not satisfied:
                targets = _IMPORT.findall(_strip_code(text))
                abs_agents = [t for t in targets
                              if (os.path.isabs(t) or t.startswith("~"))
                              and os.path.basename(t) == "AGENTS.md"]
                if abs_agents:
                    findings.append(Finding(
                        "ERROR", "CLAUDE.md", None,
                        "CLAUDE.md imports AGENTS.md by absolute path (%s) — that resolves "
                        "only on the machine that wrote it; use the repo-relative "
                        "'@AGENTS.md' (§6)" % abs_agents[0]))
                else:
                    findings.append(Finding(
                        "ERROR", "CLAUDE.md", None,
                        "CLAUDE.md does not import AGENTS.md — the root files have drifted "
                        "into separate sources of truth; its content should be "
                        "'@AGENTS.md' (§6; the first content line must be the "
                        "standalone '@AGENTS.md' import)"))

    cdir = os.path.join(root, ".cursor", "rules")
    if not os.path.isdir(cdir):
        findings.append(Finding(
            "WARN", os.path.join(".cursor", "rules"), None,
            "no .cursor/rules/*.mdc pointer — Cursor loads .mdc rules from this directory; "
            "add an always-apply rule pointing at AGENTS.md (§6)"))
        return findings

    pointer = False
    for dirpath, _dn, filenames in os.walk(cdir):
        for fn in sorted(filenames):
            if not fn.endswith(".mdc"):
                continue
            abspath = os.path.join(dirpath, fn)
            rel = os.path.relpath(abspath, root)
            data, fm = _load_frontmatter(abspath, rel)
            findings += fm
            if data is None:
                continue
            aa = data.get("alwaysApply")
            if not (isinstance(aa, str) and aa.strip().lower() == "true"):
                continue
            text, _rd = _read_utf8(abspath, rel)
            if text is not None and "AGENTS.md" in text:
                pointer = True
    if not pointer:
        findings.append(Finding(
            "WARN", os.path.join(".cursor", "rules"), None,
            "no always-apply .cursor/rules/*.mdc rule references AGENTS.md — Cursor users "
            "get no route to the canonical instructions (§6)"))
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


_EXEC_HEADER = ("Activity", "Direction", "Deep record")
_EXEC_DELIM_CELL = re.compile(r"^-{3,}$")
# No cell may carry HTML, a code span, an escape, or a cell pipe.
_EXEC_CELL_OK = re.compile(r"^[^<>|\\`]*$")
# Activity and Direction go further: plain text, so no link or image syntax and
# no emphasis markers. Only the Deep record cell may carry markup, and only the
# one anchored link form below (Codex review of slice 2.2a: the cell rule used
# to be shared, which let '![img](x)' and '**bold**' into an Activity cell while
# ontologies/README.md claimed cells were plain text).
#
# Ban the SYNTAX, not the characters it is spelled with. Banning '[', ']' and
# '_' outright rejected legitimate activity names — "Coverage [EMEA]",
# "SOC_2 compliance" — which is a cost the canonical form was never meant to
# impose (Codex re-review of slice 2.2a).
_EXEC_LINKISH = re.compile(r"\]\(")   # the signature of a link or an image
# '*' cannot appear in plain prose without opening emphasis. '_' can: CommonMark
# does not read INTRAWORD '_' as emphasis, so "SOC_2" is text while "_x_" is not.
_EXEC_EMPHASIS = re.compile(r"\*|(?<![0-9A-Za-z])_|_(?![0-9A-Za-z])")
# A link reference definition anywhere in the file makes every bracketed span in
# every cell a potential link. Rather than enumerate bracket spellings — the
# whack-a-mole this grammar exists to end — forbid the definition, which makes
# every bracket provably literal. That is what keeps "Coverage [EMEA]" legal.
#
# Recognizing definitions is CommonMark emulation: they nest in containers
# ("> [r]: /url", "- [r]: /url"), wrap their labels across lines, and defer
# their destination to the next line, so a line-anchored regex misses them
# (Codex review of slice 2.2b). But every definition's label-closing line
# carries the two-character sequence "]:" — the colon must immediately follow
# the label — so THAT is the signature banned on every line outside the table.
# Deliberately over-tight, like the pipe rule: a fenced example or a
# destinationless "[r]:" line is rejected too, the latter because a definition
# may put its destination on the following line.
_LINK_REF_SIG = "]:"


def _is_plain_text(cell):
    """True when a cell carries no link, image, or emphasis syntax."""
    return not _EXEC_LINKISH.search(cell) and not _EXEC_EMPHASIS.search(cell)
_EXEC_LINK = re.compile(r"^\[[^\[\]]+\]\(([^()\s]+)\)$")
# EXACTLY the em dash. A hyphen, an en dash, or an empty cell are near misses,
# not synonyms — tolerating them is the GFM-style permissiveness this grammar
# exists to remove (Codex review of slice 2.2a).
_EXEC_NO_RECORD = "—"


def _canonical_row(line):
    """The three cells of one canonical table line, or None when the line is not
    canonical: it must start with '|', end with '|', hold exactly three cells
    between them, and carry no escapes, HTML, or code spans. Leading whitespace
    is NOT tolerated — an indented line is a code block to a markdown reader.

    Per-cell ROLE rules (plain text vs. the one legal link form) belong to the
    caller, which knows whether it is looking at a header, a delimiter, or a
    data row."""
    s = line.rstrip()
    if len(s) < 2 or not s.startswith("|") or not s.endswith("|"):
        return None
    cells = [c.strip() for c in s[1:-1].split("|")]
    if len(cells) != 3 or not all(_EXEC_CELL_OK.match(c) for c in cells):
        return None
    return cells


def parse_exec_table(text, path="<unknown>"):
    """Parse the ONE canonical executive-view table. Returns (rows, findings);
    rows are (activity, direction_lower, deep_link_or_None, line_no).

    DOCTRINE — #11 applied to the second structured surface. This is a
    RESTRICTED GRAMMAR, not a markdown-table parser. groundwork owns this format
    (its own generator writes it), so the honest design is to define one exact
    shape and ERROR on everything else, exactly as the frontmatter reader does:
    "any other syntax ERRORs". Emulating GFM here cost eight review rounds and
    still diverged, because GFM is a large spec and each round only closes the
    case it found. Under a canonical grammar the whole class — decoy tables,
    fenced or comment-wrapped examples, blockquoted or non-leading-pipe rows,
    delimiter arity and position, boundary pipes, duplicate columns, span-vs-cell
    precedence, indentation, column deletion — is not handled. It is unreachable.

    Absence of a table is NOT a finding here; check_ontology decides whether an
    empty worksheet is silent (#5) or a missing table is an error."""
    rows, findings = [], []
    lines = text.split("\n")
    for i, ln in enumerate(lines):
        if _LINK_REF_SIG in ln and "|" not in ln:
            findings.append(Finding(
                "ERROR", path, i + 1,
                "an executive view carries no link reference definition — it would make "
                "every bracketed cell a potential link, and ']:' outside the table is "
                "its signature; write the one Deep record link inline instead "
                "(#5 canonical form)"))
    if findings:
        return rows, findings
    pipe_lines = [i for i, ln in enumerate(lines) if "|" in ln]
    if not pipe_lines:
        return rows, findings

    start = pipe_lines[0]
    end = start
    while end + 1 < len(lines) and "|" in lines[end + 1]:
        end += 1
    outside = [i for i in pipe_lines if i > end]
    if outside:
        # Point at the FIRST line outside the block and name the block itself:
        # reporting the last pipe line sent the author to a legitimate table row
        # when the stray pipe was the line that opened the block (Codex review
        # of slice 2.2a).
        findings.append(Finding(
            "ERROR", path, outside[0] + 1,
            "an executive view holds exactly one activity table; a table block was "
            "read from line %d to line %d, and this line carries a '|' outside it "
            "(#5 canonical form)" % (start + 1, end + 1)))
        return rows, findings

    header = _canonical_row(lines[start])
    if header is None or tuple(header) != _EXEC_HEADER:
        findings.append(Finding(
            "ERROR", path, start + 1,
            "executive-view table header must be exactly "
            "'| Activity | Direction | Deep record |' — spelling and case included "
            "(#5 canonical form)"))
        return rows, findings

    if end < start + 2:
        findings.append(Finding(
            "ERROR", path, start + 1,
            "executive-view table needs its delimiter row and at least one activity "
            "row (#5 canonical form)"))
        return rows, findings

    delim = _canonical_row(lines[start + 1])
    if delim is None or not all(_EXEC_DELIM_CELL.match(c) for c in delim):
        findings.append(Finding(
            "ERROR", path, start + 2,
            "the row under the header must be the delimiter '|---|---|---|' — no "
            "alignment colons, exactly three cells (#5 canonical form)"))
        return rows, findings

    for j in range(start + 2, end + 1):
        cells = _canonical_row(lines[j])
        if cells is None:
            findings.append(Finding(
                "ERROR", path, j + 1,
                "executive-view row is not canonical — exactly three plain-text cells "
                "between a leading and a trailing '|' (#5 canonical form)"))
            continue
        activity, direction, deep = cells
        if not _is_plain_text(activity) or not _is_plain_text(direction):
            findings.append(Finding(
                "ERROR", path, j + 1,
                "Activity and Direction cells are plain text — no link or image "
                "syntax, no emphasis markers (#5 canonical form)"))
            continue
        link = None
        if deep != _EXEC_NO_RECORD:
            m = _EXEC_LINK.match(deep)
            if m is None:
                findings.append(Finding(
                    "ERROR", path, j + 1,
                    "Deep record cell must be exactly '—' (an em dash) or exactly one "
                    "link '[text](path)' (#5 canonical form)"))
                continue
            link = m.group(1)
        rows.append((activity, direction.lower(), link, j + 1))
    return rows, findings


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
            rows, table_findings = ((), [])
            if exec_text is not None:
                rows, table_findings = parse_exec_table(exec_text, rel_exec)
            findings += table_findings
            if exec_text is not None and exec_text.strip() and not rows \
                    and not table_findings:
                findings.append(Finding("ERROR", rel_exec, None,
                                        "executive view has no activity table — a canonical "
                                        "'| Activity | Direction | Deep record |' table with at "
                                        "least one row is required (#5 exec tier)"))
            for activity, direction, link, ln in rows:
                if not activity:
                    findings.append(Finding("ERROR", rel_exec, ln,
                                            "executive-view row has an empty Activity cell"))
                if direction not in DIRECTIONS:
                    findings.append(Finding("ERROR", rel_exec, ln,
                                            "Direction must be 'up' or 'down', got %r" % direction))
                if link:
                    target = os.path.normpath(
                        os.path.join(fdir, link.split("#", 1)[0]))
                    linked.add(os.path.realpath(target))
        for df in deep_files:
            dpath = os.path.join(fdir, df)
            if not os.path.isfile(dpath):
                # a directory (or FIFO) named x.md would crash or block the read
                findings.append(Finding("ERROR", os.path.join(rel_fdir, df), None,
                                        "ontology entry ending in .md is not a regular file"))
                continue
            findings += check_deep_record(dpath, root)
            if os.path.realpath(dpath) not in linked:
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
            # Ritual provenance is thinking-quality, not a safety invariant, so
            # it sits in the WARN tier (1.5a deferral, decided 2026-07-23).
            for field in ("ritual", "scarcity", "surviving_job"):
                if _blank(data.get(field)):
                    findings.append(Finding("WARN", rel, None,
                                            "missing '%s' (incomplete thinking — the five-question "
                                            "worksheet's provenance)" % field))

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


def _hook_command_target(command, root):
    """Best-effort: pull the script path out of a hook command string.
    Splits with shell quoting rules (the shipped snippet quotes the path so
    roots with spaces survive word-splitting), strips a leading interpreter,
    and resolves ${CLAUDE_PROJECT_DIR} to root."""
    if not isinstance(command, str) or not command.strip():
        return None
    # pipelines, redirections, and command chaining can discard the decision
    # JSON — the hook would run but Claude would never receive the deny
    if re.search(r"[|;&<>]", command):
        return None
    try:
        parts = shlex.split(command)
    except ValueError:  # unbalanced quoting — not a runnable command
        return None
    if not parts:
        return None
    # drop a leading interpreter (python3, python, bash, sh, node, ...)
    if parts and os.path.basename(parts[0]) in {"python3", "python", "bash", "sh", "node"}:
        parts = parts[1:]
    if not parts:
        return None
    target = parts[0].replace("${CLAUDE_PROJECT_DIR}", root).replace("$CLAUDE_PROJECT_DIR", root)
    if not os.path.isabs(target):
        target = os.path.join(root, target)
    return os.path.normpath(target)


def _matcher_covers_bash(matcher):
    """Claude Code matchers are tool-name regexes; an absent/empty/'*' matcher
    matches every tool. An invalid regex covers nothing (fail closed)."""
    if matcher is None or matcher in ("", "*"):
        return True
    if not isinstance(matcher, str):
        return False
    try:
        return re.fullmatch(matcher, "Bash") is not None
    except re.error:
        return False


def check_hooks(root):
    """Existence-check the enforcement claim: a hook set whose command path does not
    resolve is a named-but-unwired guard — false safety, worse than an admitted gap.
    The registration itself is part of the claim: the gate must be wired under
    PreToolUse with a matcher that covers Bash, or it cannot block anything."""
    findings = []
    hooks_dir = os.path.join(root, "governance", "hooks")
    rel_dir = os.path.relpath(hooks_dir, root)
    if not os.path.isdir(hooks_dir):
        # a dangling symlink (or one to a file) is not an absent hook set
        if os.path.islink(hooks_dir):
            findings.append(Finding("ERROR", rel_dir, None,
                                    "governance/hooks is a symlink to nothing usable — "
                                    "not an absent hook set, a broken one"))
        return findings
    # a symlinked artifact is not the committed, auditable file the claim names
    if os.path.islink(hooks_dir):
        findings.append(Finding("ERROR", rel_dir, None,
                                "governance/hooks is a symlink — the hook set must be the "
                                "committed artifact, not an external alias"))
    snippet = os.path.join(hooks_dir, "settings.snippet.json")
    if os.path.isfile(snippet) and os.path.islink(snippet):
        findings.append(Finding("ERROR", os.path.join(rel_dir, "settings.snippet.json"), None,
                                "hook settings snippet is a symlink — not the committed artifact"))
    if not os.path.isfile(snippet):
        # the most unwired guard of all: nothing can be installed
        findings.append(Finding("ERROR", os.path.join(rel_dir, "settings.snippet.json"), None,
                                "hook set has no settings.snippet.json (nothing to install — "
                                "a named-but-unwired guard is false safety)"))
    else:
        rel_snip = os.path.relpath(snippet, root)
        data, parsed = None, False
        try:
            with open(snippet, encoding="utf-8") as fh:
                data = json.load(fh)
            parsed = True
        except (ValueError, OSError) as exc:
            findings.append(Finding("ERROR", rel_snip, None,
                                    "hook settings snippet is not valid JSON (%s)" % exc))
        if parsed and not isinstance(data, dict):
            findings.append(Finding("ERROR", rel_snip, None,
                                    "hook settings snippet is not a JSON object "
                                    "(nothing Claude Code can install)"))
        if isinstance(data, dict):
            events = data.get("hooks")
            declared = 0
            pre_bash = 0
            for event, entries in (events.items() if isinstance(events, dict) else ()):
                if not isinstance(entries, list):
                    continue
                for group in entries:
                    if not isinstance(group, dict):
                        continue
                    for hook in group.get("hooks", []) if isinstance(group.get("hooks"), list) else []:
                        if not isinstance(hook, dict) or hook.get("type") != "command":
                            continue
                        declared += 1
                        target = _hook_command_target(hook.get("command"), root)
                        # only the gate script itself counts as the Bash registration —
                        # an unrelated PreToolUse hook must not front for an unwired gate
                        if event == "PreToolUse" and _matcher_covers_bash(group.get("matcher")) \
                                and target == os.path.normpath(os.path.join(hooks_dir, "action_class_gate.py")):
                            pre_bash += 1
                        if target is None:
                            findings.append(Finding("ERROR", rel_snip, None,
                                                    "hook declares no runnable command"))
                        elif not os.path.isfile(target):
                            findings.append(Finding("ERROR", rel_snip, None,
                                                    "hook command not found: %s (a named-but-unwired "
                                                    "guard is false safety)" % hook.get("command")))
                        elif os.path.islink(target):
                            findings.append(Finding("ERROR", rel_snip, None,
                                                    "hook command target is a symlink: %s (not the "
                                                    "committed, auditable artifact)" % hook.get("command")))
            if declared == 0:
                findings.append(Finding("WARN", rel_snip, None,
                                        "hook settings snippet declares no command hooks"))
            # independent of `declared`: an empty hook set is still an unwired guard
            if pre_bash == 0:
                findings.append(Finding("ERROR", rel_snip, None,
                                        "no PreToolUse hook with a matcher covering Bash targets "
                                        "action_class_gate.py — the gate cannot block a command "
                                        "before it runs"))
    if not os.path.isfile(os.path.join(hooks_dir, "review-gate.md")):
        findings.append(Finding("WARN", os.path.join(rel_dir, "review-gate.md"), None,
                                "hook set has no review-gate.md — the non-Claude degradation (#19) is undocumented"))
    return findings


_PROV_FORWARD = {
    "observed": {"observed", "confirmed", "superseded"},
    "inferred": {"inferred", "confirmed", "superseded"},
    "confirmed": {"confirmed", "superseded"},
    "superseded": {"superseded"},
}


def check_version_pin(root):
    """#21 skew gate. A company root carries groundwork.pin; skew = engine - pinned.
    Pull never ERRORs content for being old; a breaking gap is one migration ERROR."""
    findings = []
    for abspath in iter_files(root, load_gitignore(root)):
        if os.path.basename(abspath) != "groundwork.pin":
            continue
        rel = os.path.relpath(abspath, root)
        data, fm = _load_frontmatter(abspath, rel)
        findings += fm
        if data is None:
            continue  # unreadable pin already ERRORed via _read_utf8

        sv = data.get("schema_version")
        if _blank(sv):
            findings.append(Finding("ERROR", rel, None, "version pin missing 'schema_version'"))
            continue
        if not isinstance(sv, str):
            findings.append(Finding("ERROR", rel, None,
                                    "version pin 'schema_version' must be a single integer"))
            continue
        try:
            pinned = int(sv.strip())
        except ValueError:
            findings.append(Finding("ERROR", rel, None,
                                    "version pin 'schema_version' is not an integer: %r" % sv))
            continue

        if _blank(data.get("generated_by_commit")):
            findings.append(Finding("WARN", rel, None,
                                    "version pin missing 'generated_by_commit' (provenance)"))

        skew = SCHEMA_VERSION - pinned
        if skew >= 1:
            findings.append(Finding("ERROR", rel, None,
                                    "content is schema v%d, engine is v%d — see MIGRATIONS.md for v%d->v%d"
                                    % (pinned, SCHEMA_VERSION, pinned, SCHEMA_VERSION)))
        elif skew < 0:
            findings.append(Finding("WARN", rel, None,
                                    "engine is schema v%d but this content is pinned at v%d — pull the engine; "
                                    "validity is not asserted against a newer schema" % (SCHEMA_VERSION, pinned)))
        # skew == 0: content is current; each check's own severity stands (silent here)
    return findings


def check_symlinked_dirs(root):
    """Make the stateless walker's skip of symlinked directories LOUD. os.walk does
    not descend into symlinked dirs, so their contents would go unchecked silently."""
    findings = []
    ignore = load_gitignore(root)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        kept = []
        for d in dirnames:
            rel = os.path.normpath(os.path.join(rel_dir, d))
            if d in SKIP_DIRS or d.startswith(".") or rel in SKIP_RELPATHS or _ignored(d, ignore):
                continue  # legitimately not scanned
            if os.path.islink(os.path.join(dirpath, d)):
                findings.append(Finding("WARN", rel, None,
                                        "symlinked directory is not traversed by the stateless validator; "
                                        "its contents are unchecked (the --diff layer backstops memory records)"))
            else:
                kept.append(d)
        dirnames[:] = kept  # do not descend into skipped or symlinked dirs
    return findings


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


BLAST_RADIUS = {"track1-body", "escalating"}


def check_proposals(root, ignore=()):
    """#17/#18 proposal-file schema. Diff-based declared-vs-actual matching is 1.5d-ii;
    this checks the static schema, the routing domain, and the pending-only lifecycle."""
    findings = []
    base = os.path.join(root, "proposals")
    if not os.path.isdir(base) or _ignored("proposals", ignore):
        return findings
    try:
        names = sorted(os.listdir(base))
    except OSError as e:
        return [Finding("ERROR", "proposals", None,
                        "cannot list proposals/ — fail closed: %s" % e)]
    for name in names:
        if not name.endswith(".md") or name in {"README.md", "_index.md"} or _ignored(name, ignore):
            continue
        abspath = os.path.join(base, name)
        rel = os.path.relpath(abspath, root)
        data, fm = _load_frontmatter(abspath, rel)
        findings += fm
        if data is None:
            continue

        target = data.get("target")
        target_is_rule = False
        target_is_skill = False
        t = None
        if _blank(target):
            findings.append(Finding("ERROR", rel, None, "proposal missing 'target' (the skill or rule it changes)"))
        elif not isinstance(target, str):
            findings.append(Finding("ERROR", rel, None, "proposal 'target' must be a single path"))
        else:
            # Normalize before classifying: a lexical alias like
            # skills/../governance/constitution/x.md must not launder a rule
            # into the skills/ bucket (rules never auto-apply).
            t = os.path.normpath(target.strip().replace("\\", "/")).replace("\\", "/")
            target_is_skill = t.startswith("skills/")
            target_is_rule = t.startswith("governance/constitution/")
            if not (target_is_skill or target_is_rule):
                findings.append(Finding("ERROR", rel, None,
                                        "proposal 'target' must be a skill (skills/) or a constitution rule "
                                        "(governance/constitution/); other artifacts keep their own governance (#17)"))
            elif not os.path.isfile(os.path.join(root, t)):
                findings.append(Finding("ERROR", rel, None, "proposal 'target' not found: %s" % t))
            else:
                # Filesystem aliases too (1.4b precedent): classification is by
                # where the target RESOLVES, not just how it is spelled — a
                # symlink under skills/ pointing at a rule must fail closed.
                resolved = os.path.relpath(
                    os.path.realpath(os.path.join(root, t)),
                    os.path.realpath(root)).replace("\\", "/")
                bucket = "skills/" if target_is_skill else "governance/constitution/"
                if not resolved.startswith(bucket):
                    findings.append(Finding("ERROR", rel, None,
                                            "proposal 'target' resolves outside %s (symlink or filesystem "
                                            "alias: %s) — fail closed (#17)" % (bucket, resolved)))
                    target_is_rule = target_is_rule or resolved.startswith("governance/constitution/")

        br = data.get("blast_radius")
        if _blank(br):
            findings.append(Finding("ERROR", rel, None, "proposal missing 'blast_radius' (track1-body | escalating)"))
        elif not (isinstance(br, str) and br in BLAST_RADIUS):
            findings.append(Finding("ERROR", rel, None,
                                    "invalid 'blast_radius' %r (one of %s)" % (br, sorted(BLAST_RADIUS))))
        elif br == "track1-body" and target_is_rule:
            findings.append(Finding("ERROR", rel, None,
                                    "a constitution rule can never be 'track1-body' — rules never auto-apply; "
                                    "they are escalating by construction (#17)"))
        elif br == "track1-body" and target_is_skill and not t.endswith("/SKILL.md"):
            findings.append(Finding("ERROR", rel, None,
                                    "'track1-body' touches only the SKILL.md body — %s is not a SKILL.md; "
                                    "description, card, and every other change is escalating (#17)" % t))

        status = data.get("status")
        if _blank(status):
            pass
        elif not isinstance(status, str):
            findings.append(Finding("ERROR", rel, None,
                                    "proposal 'status' must be the scalar string 'pending' "
                                    "(proposals/ is pending-only, #18) — got %r" % (status,)))
        elif status.strip() != "pending":
            findings.append(Finding("ERROR", rel, None,
                                    "proposals/ is pending-only; an applied proposal evaporates into the "
                                    "consent commit (#18) — status is %r" % status))

        reason = data.get("reason")
        if _blank(reason) or not isinstance(reason, str):
            findings.append(Finding("WARN", rel, None,
                                    "incomplete proposal: missing 'reason' (one scalar line) — belongs as an "
                                    "org-memory working note until it fills (#17)"))
        ev = data.get("evidence")
        if _blank(ev):
            findings.append(Finding("WARN", rel, None,
                                    "incomplete proposal: missing 'evidence' links — demote to a working note (#17)"))
        else:
            for e in (ev if isinstance(ev, list) else [ev]):
                if isinstance(e, str) and e.strip() and not os.path.isfile(os.path.join(root, e.strip())):
                    findings.append(Finding("WARN", rel, None, "evidence link not found: %s" % e.strip()))

        # #17 completeness includes the diff itself: the proposal file IS the
        # review file, so a body with no substantive content (no Diff / Why)
        # is incomplete. The frontmatter parsed above, so the file is UTF-8.
        text, _rd = _read_utf8(abspath, rel)
        body = []
        if text is not None:
            lines = text.split("\n")
            if lines and lines[0].strip() == "---":
                for i in range(1, len(lines)):
                    if lines[i].strip() == "---":
                        body = lines[i + 1:]
                        break
        # Strip multiline HTML comments first (an unterminated opener hides
        # everything after it) — _substantive_line only sees one-line comments.
        body_text = re.sub(r"<!--.*?(-->|\Z)", "", "\n".join(body), flags=re.S)
        if not any(_substantive_line(ln) for ln in body_text.split("\n")):
            findings.append(Finding("WARN", rel, None,
                                    "incomplete proposal: empty body — the diff and reasoning live in the "
                                    "file (## Diff / ## Why); demote to a working note (#17)"))
        else:
            # #17: a complete proposal carries the diff itself, statically — a
            # '## Diff' section with content (matching declared-vs-actual is
            # 1.5d-ii).
            m = re.search(r"^## Diff\b(.*?)(?=^## |\Z)", body_text, flags=re.S | re.M)
            if not (m and any(_substantive_line(ln) for ln in m.group(1).split("\n"))):
                findings.append(Finding("WARN", rel, None,
                                        "incomplete proposal: no '## Diff' content — a complete proposal "
                                        "carries its diff (#17); demote to a working note"))
    return findings


def check_changelog(root, ignore=()):
    """#17 governance changelog: append-only index of auto-applied track-1 changes.
    Validates entry format; append-only enforcement is the --diff mode (1.5d-ii)."""
    findings = []
    path = os.path.join(root, "governance", "changelog.md")
    if not os.path.isfile(path) or _ignored("governance", ignore) or _ignored("changelog.md", ignore):
        return findings
    rel = os.path.relpath(path, root)
    text, rd = _read_utf8(path, rel)
    findings += rd
    if text is None:
        return findings
    for lineno, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if not s.startswith("- "):
            continue
        fields = [c.strip() for c in s[2:].split("|")]
        if len(fields) != 5 or not all(fields):
            findings.append(Finding("WARN", rel, lineno,
                                    "malformed changelog entry (want: date | skill | gist | agent | sha)"))
            continue
        date_s, skill_s, _gist, _agent, sha_s = fields
        if _parse_date(date_s) is None:
            findings.append(Finding("WARN", rel, lineno, "changelog entry has an unparseable date: %r" % date_s))
        skill_norm = os.path.normpath(skill_s.replace("\\", "/")).replace("\\", "/")
        if not skill_norm.startswith("skills/"):
            findings.append(Finding("WARN", rel, lineno,
                                    "changelog entry skill path should be under skills/ (auto-apply is track-1 skills only)"))
        elif not skill_norm.endswith("/SKILL.md"):
            findings.append(Finding("WARN", rel, lineno,
                                    "changelog entry should point at a SKILL.md (auto-apply is body-only SKILL.md edits)"))
        elif os.path.isfile(os.path.join(root, skill_norm)):
            # Symlink parity with check_proposals: a path spelled skills/ that
            # resolves elsewhere in the current tree is an alias, not a skill.
            resolved = os.path.relpath(
                os.path.realpath(os.path.join(root, skill_norm)),
                os.path.realpath(root)).replace("\\", "/")
            if not resolved.startswith("skills/"):
                findings.append(Finding("WARN", rel, lineno,
                                        "changelog entry skill path is a filesystem alias resolving outside "
                                        "skills/ (%s)" % resolved))
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", sha_s):
            findings.append(Finding("WARN", rel, lineno, "changelog entry commit sha looks malformed: %r" % sha_s))
    return findings


def _governed_class(rel):
    """Classify a path (relative to a governed root) into #17's routing domain:
    'rule' (any constitution file), 'skill-md' (a package's own SKILL.md),
    'skill-other' (anything else inside a skill package — the Owner's Card and
    every nested file), or None (not governed by the proposal routing at all).
    Top-level docs under skills/ (e.g. skills/work-package-spec.md) are not part
    of a package and are not governed.

    Directory names match case-insensitively (Codex r1): on a case-folding
    filesystem, Governance/ IS governance/, so exact-case matching would let a
    case-rename launder a rule out of the routing domain. On a case-sensitive
    filesystem the case-variant is a different path, and classifying it governed
    merely escalates — the safe direction. Only the canonical SKILL.md spelling
    is ever auto-apply-eligible; a case-variant lands on skill-other."""
    parts = rel.split("/")
    low = [p.casefold() for p in parts]
    if len(parts) >= 3 and low[0] == "governance" and low[1] == "constitution" \
            and low[-1].endswith(".md"):
        return "rule"
    if len(parts) >= 3 and low[0] == "skills":
        if len(parts) == 3 and parts[2] == "SKILL.md":
            return "skill-md"
        return "skill-other"
    return None


def classify_governed_change(kind, cls, old_text, new_text):
    """PURE #17 blast-radius classification of ONE changed governed file. `kind`
    is 'added' or 'modified' (deletions are the caller's, see #18 note below);
    `cls` comes from _governed_class. Returns (radius, detail) with radius in
    BLAST_RADIUS, or (None, None) when nothing actually changed.

    Reasoning to carry: 'track1-body' is the ONLY auto-apply-eligible verdict, so
    every uncertain path must resolve to 'escalating'. A misclassification in that
    direction costs a human review; the other direction lets an unreviewed change
    land. Unparseable frontmatter, a missing or invalid action_class, a nested or
    non-SKILL.md package file, a brand-new SKILL.md (its description is a new
    selection surface) — all escalate."""
    if kind == "modified":
        # No-op first, for EVERY class: the caller's candidate set is the whole
        # base tree, so an untouched rule must not read as an escalating change.
        # Line endings are normalized (a CRLF base blob against a text-mode read
        # is not a rewrite); anything beyond that is a change.
        old_n = (old_text or "").replace("\r\n", "\n").replace("\r", "\n")
        new_n = (new_text or "").replace("\r\n", "\n").replace("\r", "\n")
        if old_n == new_n:
            return None, None
    if cls == "rule":
        return "escalating", "a constitution rule (rules never auto-apply, #17)"
    if cls == "skill-other":
        return "escalating", "a skill-package file other than SKILL.md (Owner's Card / package content)"
    if kind == "added":
        return "escalating", "a new SKILL.md (its description is a new selection surface)"

    old_fm, old_body, _old_parse = _frontmatter_and_body(old_text or "", "base")
    new_fm, new_body, new_parse = _frontmatter_and_body(new_text or "", "new")
    if any(f.level == "ERROR" for f in new_parse):
        return "escalating", "unparseable SKILL.md frontmatter (cannot prove the change is body-only)"
    if old_fm != new_fm:
        return "escalating", "SKILL.md frontmatter (description / action class / governance fields)"

    old_b = old_body.replace("\r\n", "\n").replace("\r", "\n").strip()
    new_b = new_body.replace("\r\n", "\n").replace("\r", "\n").strip()
    if old_b == new_b:
        return None, None

    # Frontmatter is identical here, so old and new action_class agree; read it
    # once and require it to be a valid class before conceding track-1.
    ac = new_fm.get("action_class")
    if not isinstance(ac, str) or ac not in ACTION_CLASSES:
        return "escalating", ("SKILL.md body of a skill with no valid action_class "
                              "(cannot prove track-1)")
    if ac in TRACK2_CLASSES:
        return "escalating", "SKILL.md body of a track-2 (%s) skill" % ac
    return "track1-body", "SKILL.md body of a track-1 (%s) skill" % ac


def _changelog_append_only(old_text, new_text):
    """PURE. #17's changelog is an append-only index: every line committed at base
    must survive, in order, as the head of the new file. Trailing blank lines on
    the base side are ignored (an append lands after them). Line endings are
    normalized first so a CRLF base blob is not a phantom rewrite."""
    def _lines(t):
        return t.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    old_lines = _lines(old_text)
    while old_lines and not old_lines[-1].strip():
        old_lines.pop()
    return _lines(new_text)[:len(old_lines)] == old_lines


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
    findings += check_hooks(root)
    findings += check_version_pin(root)
    findings += check_symlinked_dirs(root)
    findings += check_proposals(root, ignore)
    findings += check_changelog(root, ignore)
    findings += check_agents_chain(root, ignore)
    findings += check_always_loaded_budget(root)
    findings += check_root_files(root)
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
    not fake a deletion. Returns 'ok', 'symlink', 'missing', or 'unreadable' —
    an unlistable ancestor is NOT a deletion (Codex r1: conflating them would
    route an unclassifiable change through the caller's deletion path). Pass a
    dict as `cache` to reuse directory listings across records. Check-then-open
    is not atomic — a concurrent writer race is a documented non-goal
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
        if entries is None:
            return "unreadable"
        if unicodedata.normalize("NFC", part) not in entries:
            return "missing"
        p = os.path.join(p, part)
        if os.path.islink(p):
            return "symlink"
    return "ok" if os.path.isfile(p) else "missing"


def _git_diff_context(root, base):
    """Resolve the git layout and the BASE file list once, with 1.4b's hardening:
    byte-safe paths, canonical-casing scope prefix, a verified base ref, and a
    NUL-separated ls-tree listing. Returns (ctx, findings); ctx is None exactly
    when the findings are fatal. Shared by every --diff mode so the plumbing is
    hardened in one place."""
    try:
        # bytes + os.fsdecode: survives locale-undecodable repo paths; and
        # --show-prefix gives root's repo-relative path in git's canonical
        # casing, so a case-variant invocation cannot blind the scope filter
        rp = subprocess.run(["git", "-C", root, "rev-parse", "--show-toplevel", "--show-prefix"],
                            capture_output=True, check=True).stdout
    except (subprocess.CalledProcessError, OSError):
        return None, [Finding("ERROR", root, None, "--diff requires a git repository")]
    rp_lines = os.fsdecode(rp).splitlines()
    if len(rp_lines) != 2 or not os.path.isdir(rp_lines[0]):
        # a newline/CR inside the repo path mis-splits this output; a wrong
        # scope would fail open, so refuse instead
        return None, [Finding("ERROR", root, None,
                              "--diff could not resolve the repository layout (unsupported path)")]
    toplevel = rp_lines[0]
    scope = rp_lines[1].strip("/") or "."
    try:
        subprocess.run(["git", "-C", toplevel, "rev-parse", "--verify", "--quiet",
                        "%s^{commit}" % base], capture_output=True, check=True)
    except (subprocess.CalledProcessError, OSError):
        # a typo'd base must not report a clean bill of health
        return None, [Finding("ERROR", root, None, "--diff base ref not found: %s" % base)]
    try:
        # -z: NUL-terminated, unquoted paths (immune to core.quotePath mangling
        # of non-ASCII names); os.fsdecode round-trips odd bytes losslessly
        raw = subprocess.run(["git", "-C", toplevel, "ls-tree", "-r", "--name-only", "-z", base],
                             capture_output=True, check=True).stdout
    except (subprocess.CalledProcessError, OSError):
        return None, [Finding("ERROR", root, None, "--diff could not list the base tree for %s" % base)]
    return {"toplevel": toplevel, "scope": scope,
            "base_files": [os.fsdecode(b) for b in raw.split(b"\0") if b]}, []


def _git_show(toplevel, base, repo_path):
    """The base version of one committed file as text, or None when it cannot be
    read (fetch failure, a git launch error, or non-UTF-8). Callers treat None
    as fail-closed: the base LIST says the file exists, so an unreadable base is
    never 'new'."""
    try:
        show = subprocess.run(["git", "-C", toplevel, "show", "%s:%s" % (base, repo_path)],
                              capture_output=True)
    except OSError:
        return None
    if show.returncode != 0:
        return None
    try:
        return show.stdout.decode("utf-8")
    except UnicodeError:
        return None


def memory_diff_findings(root, base):
    """Compare memory records that existed at <base> (a git ref) against the
    working tree. Scoped to memory folders under root. New records are fine;
    deletions and immutable-field edits are ERRORs. Driven by the BASE file
    list, so no working-tree skip can exempt a committed record."""
    ctx, ctx_findings = _git_diff_context(root, base)
    if ctx is None:
        return ctx_findings
    toplevel, scope = ctx["toplevel"], ctx["scope"]
    findings = []
    listdir_cache = {}
    for bf in ctx["base_files"]:
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
        if status == "unreadable":
            findings.append(Finding("ERROR", bf, None,
                                    "cannot verify immutability: a directory on this record's path is "
                                    "unreadable — fail closed"))
            continue
        if status == "missing":
            findings.append(Finding("ERROR", bf, None,
                                    "memory record deleted (records are superseded, never deleted)"))
            continue
        old = _git_show(toplevel, base, bf)
        if old is None:
            # the base LIST says it exists, so a fetch failure (or an
            # undecodable blob) is never "new" — fail closed
            findings.append(Finding("ERROR", bf, None,
                                    "cannot verify immutability: the base version of this record is "
                                    "unreadable or not valid UTF-8"))
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


def _has_symlink_component(root, rel):
    """True when any component of root/rel is a symlink. A symlinked rule, skill,
    or ancestor directory cannot be classified honestly (it can point one place
    and be spelled another), so the caller fails closed."""
    p = root
    for part in rel.split("/"):
        p = os.path.join(p, part)
        if os.path.islink(p):
            return True
    return False


def _walk_working_tree(root):
    """iter_files' walk (same SKIP_DIRS / dot-dir / SKIP_RELPATHS pruning, and
    deliberately NO .gitignore), but an unlistable directory becomes an ERROR
    instead of a silent prune (Codex r1): a directory the scan cannot descend
    into could hide a new governed file or a pin, and silence would fail open.
    Returns (abspaths, findings)."""
    files, findings = [], []

    def onerror(err):
        bad = getattr(err, "filename", None) or root
        rel = os.path.relpath(bad, root).replace(os.sep, "/")
        findings.append(Finding("ERROR", rel, None,
                                "--diff cannot scan this directory (unreadable) — a governed "
                                "change could hide here, so fail closed"))

    for dirpath, dirnames, filenames in os.walk(root, onerror=onerror):
        rel_dir = os.path.relpath(dirpath, root)
        dirnames[:] = [d for d in dirnames
                       if d not in SKIP_DIRS and not d.startswith(".")
                       and os.path.normpath(os.path.join(rel_dir, d)) not in SKIP_RELPATHS]
        for fn in filenames:
            files.append(os.path.join(dirpath, fn))
    return files, findings


def _pin_dirs(root, base_files, scope, wt_files):
    """Governed roots: every directory carrying a #21 groundwork.pin, collected
    from the BASE tree AND the working tree (wt_files, one shared scan). Both
    sides matter — deleting the pin in the same diff must not un-govern the
    change that deleted it. Returned as root-relative directories, where "" is
    root itself. .gitignore is deliberately NOT honored: a pin hidden behind an
    ignore rule must not un-govern content."""
    dirs = set()
    for bf in base_files:
        if scope != "." and not bf.startswith(scope + "/"):
            continue
        rel = bf if scope == "." else bf[len(scope) + 1:]
        if os.path.basename(rel) == "groundwork.pin":
            dirs.add(os.path.dirname(rel).replace("\\", "/"))
    for abspath in wt_files:
        if os.path.basename(abspath) != "groundwork.pin":
            continue
        rel = os.path.relpath(abspath, root).replace(os.sep, "/")
        dirs.add(os.path.dirname(rel))
    return dirs


def _pending_proposal_radii(root, gov_rel):
    """{realpath(target) -> set(declared blast_radius)} for the pending proposals
    in <governed root>/proposals/. Targets resolve through the filesystem
    (realpath) and must stay contained in the governed root, so a symlink or a
    '../' alias can never point one place and match another — the same
    both-layers discipline check_proposals uses. Anything malformed is simply
    absent from the map, which makes the change it would have covered fail
    closed (no match -> the escalating ERROR fires)."""
    out = {}
    gov_abs = os.path.join(root, *gov_rel.split("/")) if gov_rel else root
    pdir = os.path.join(gov_abs, "proposals")
    if not os.path.isdir(pdir) or os.path.islink(pdir):
        return out
    try:
        names = sorted(os.listdir(pdir))
    except OSError:
        return out
    gov_real = os.path.realpath(gov_abs)
    for name in names:
        if not name.endswith(".md") or name in {"README.md", "_index.md"}:
            continue
        ppath = os.path.join(pdir, name)
        if os.path.islink(ppath):
            continue  # a symlinked proposal file cannot authorize anything —
            # its content lives elsewhere and can change after review (Codex r1)
        data, _f = _load_frontmatter(ppath, name)
        if data is None:
            continue
        status = data.get("status")
        if isinstance(status, str) and status.strip() and status.strip() != "pending":
            continue  # not pending; check_proposals already ERRORs on the lifecycle
        target, br = data.get("target"), data.get("blast_radius")
        if not isinstance(target, str) or not isinstance(br, str) or br not in BLAST_RADIUS:
            continue
        tabs = os.path.join(gov_abs, os.path.normpath(target.strip().replace("\\", "/")))
        if not os.path.isfile(tabs):
            continue
        treal = os.path.realpath(tabs)
        if not treal.startswith(gov_real + os.sep):
            continue
        out.setdefault(treal, set()).add(br)
    return out


def _changelog_appended_targets(root, gov_abs, appended_lines):
    """Realpaths of the skills named by changelog lines APPENDED since base. An
    old line for the same skill does not excuse a new edit, so only the appended
    span counts. Targets must resolve INSIDE the governed root (the same
    containment discipline as proposal targets) — a line whose path escapes the
    root names nothing here."""
    targets = set()
    gov_real = os.path.realpath(gov_abs)
    for line in appended_lines:
        s = line.strip()
        if not s.startswith("- "):
            continue
        fields = [c.strip() for c in s[2:].split("|")]
        if len(fields) != 5:
            continue
        p = os.path.join(gov_abs, os.path.normpath(fields[1].replace("\\", "/")))
        if not os.path.isfile(p):
            continue
        rp = os.path.realpath(p)
        if rp.startswith(gov_real + os.sep):
            targets.add(rp)
    return targets


def blast_radius_diff_findings(root, base):
    """#18's blast-radius tripwire. On --diff, classify every changed skill/rule
    under a governed root (a directory carrying a #21 groundwork.pin) and require
    each ESCALATING change to trace to a pending proposal whose DECLARED
    blast_radius matches what the diff ACTUALLY touches. A track-1 body-only
    change wants its changelog line (WARN — a stateless validator cannot tell an
    agent auto-apply from the maintainer's own edit); the changelog itself is
    append-only (ERROR).

    What this cannot do: prove a human truthfully reviewed anything. That is the
    commit bit's job (#18) — see docs/known-limitations.md."""
    ctx, ctx_findings = _git_diff_context(root, base)
    if ctx is None:
        return ctx_findings
    toplevel, scope, base_files = ctx["toplevel"], ctx["scope"], ctx["base_files"]
    findings = []

    base_rels = {}
    for bf in base_files:
        if scope != "." and not bf.startswith(scope + "/"):
            continue
        base_rels[(bf if scope == "." else bf[len(scope) + 1:])] = bf

    # One shared working-tree scan: the pin discovery, the candidate union, and
    # the unreadable-directory ERRORs all come from it. Scan trouble is reported
    # even when the result looks dormant — an unlistable directory could be
    # hiding the very pin that would activate the tripwire.
    wt_files, wt_findings = _walk_working_tree(root)
    findings += wt_findings

    gov_roots = _pin_dirs(root, base_files, scope, wt_files)
    if not gov_roots:
        return findings  # no company instance in scope: the tripwire is dormant

    def _fold(s):
        # NFC first (git reports NFC while a mac filesystem lists NFD — the
        # same mismatch _committed_path_status already bridges), then casefold.
        return unicodedata.normalize("NFC", s).casefold()

    def governed_classes(rel):
        # EVERY containing root's classification (Codex r1+r2): picking one
        # root — even the deepest with a non-None class — lets a planted inner
        # pin reshape the inner path and downgrade an outer rule to a skill.
        # A change must be licensed under each root that governs it; a
        # pathological double-root only ever ADDS review, never removes it.
        #
        # Containment matches COMPONENT-WISE under NFC+casefold (Codex r2+r3):
        # a case- or normalization-rename of the pinned directory must not walk
        # the tree out of its governed root, and component matching is immune
        # to length-changing folds (ß -> ss) that would misalign a string
        # slice. Within one depth, an exact-case root is authoritative when it
        # matches (Codex r3): two genuinely distinct case-sibling roots on a
        # case-sensitive filesystem must not cross-demand each other's
        # proposals — that gate would be unsatisfiable. The folded fallback
        # applies exactly when no exact root claims the path (the rename case).
        parts = rel.split("/")
        fparts = [_fold(p) for p in parts]
        by_depth = {}
        for g in gov_roots:
            gparts = g.split("/") if g else []
            n = len(gparts)
            if len(parts) <= n:
                continue
            if fparts[:n] != [_fold(p) for p in gparts]:
                continue
            by_depth.setdefault(n, []).append((parts[:n] == gparts, g))
        out = []
        for n, entries in sorted(by_depth.items()):
            cls = _governed_class("/".join(parts[n:]))
            if cls is None:
                continue
            chosen = [g for exact, g in entries if exact] or [g for _e, g in entries]
            for g in chosen:
                out.append((g, cls))
        return out

    # --- Pass 1: the changelog per governed root (append-only + appended span).
    appended_targets = {}
    for g in sorted(gov_roots):
        gov_abs = os.path.join(root, *g.split("/")) if g else root
        cl_rel = (g + "/" if g else "") + "governance/changelog.md"
        appended_targets[g] = set()
        bf = base_rels.get(cl_rel)
        if bf is None:
            continue  # no committed ledger at base: nothing to protect yet
        old = _git_show(toplevel, base, bf)
        if old is None:
            findings.append(Finding("ERROR", cl_rel, None,
                                    "cannot verify the governance changelog: its base version is "
                                    "unreadable or not valid UTF-8"))
            continue
        abspath = os.path.join(root, *cl_rel.split("/"))
        if _has_symlink_component(root, cl_rel):
            findings.append(Finding("ERROR", cl_rel, None,
                                    "the governance changelog is or sits behind a symlink "
                                    "(cannot verify it is append-only)"))
            continue
        if not os.path.isfile(abspath):
            findings.append(Finding("ERROR", cl_rel, None,
                                    "the governance changelog was deleted — it is an append-only "
                                    "index of auto-applied changes (#17)"))
            continue
        new, rd = _read_utf8(abspath, cl_rel)
        if new is None:
            findings += rd
            continue
        if not _changelog_append_only(old, new):
            findings.append(Finding("ERROR", cl_rel, None,
                                    "the governance changelog is append-only — an existing entry was "
                                    "edited, reordered, or removed (#17)"))
            continue
        old_lines = old.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        while old_lines and not old_lines[-1].strip():
            old_lines.pop()
        new_lines = new.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        appended_targets[g] = _changelog_appended_targets(root, gov_abs, new_lines[len(old_lines):])

    # --- Pass 2: every changed governed file.
    candidates = set(base_rels)
    for abspath in wt_files:
        candidates.add(os.path.relpath(abspath, root).replace(os.sep, "/"))

    proposals_cache = {}
    for rel in sorted(candidates):
        if _diff_in_workbench_skips(rel):
            continue
        pairs = governed_classes(rel)
        if not pairs:
            continue

        abspath = os.path.join(root, *rel.split("/"))
        bf = base_rels.get(rel)
        if bf is not None:
            status = _committed_path_status(toplevel, bf.split("/"), None)
            if status == "symlink":
                findings.append(Finding("ERROR", rel, None,
                                        "governed file is or sits behind a symlink (cannot classify "
                                        "its blast radius)"))
                continue
            if status == "unreadable":
                # NOT the deletion WARN: an unlistable ancestor makes the change
                # unclassifiable, and unclassifiable resolves to fail-closed.
                findings.append(Finding("ERROR", rel, None,
                                        "cannot classify this change: a directory on its path is "
                                        "unreadable — fail closed"))
                continue
            if status == "missing":
                findings.append(Finding("WARN", rel, None,
                                        "governed file deleted — retiring a rule or skill is escalating, "
                                        "and its record is the maintainer's consent commit; a proposal "
                                        "cannot name a target that no longer exists (#18)"))
                continue
            old = _git_show(toplevel, base, bf)
            if old is None:
                findings.append(Finding("ERROR", rel, None,
                                        "cannot classify this change: the base version is unreadable "
                                        "or not valid UTF-8"))
                continue
            kind = "modified"
        else:
            if _has_symlink_component(root, rel):
                findings.append(Finding("ERROR", rel, None,
                                        "governed file is or sits behind a symlink (cannot classify "
                                        "its blast radius)"))
                continue
            if not os.path.isfile(abspath):
                continue
            old, kind = None, "added"

        new, rd = _read_utf8(abspath, rel)
        if new is None:
            findings += rd
            continue

        for g, cls in pairs:
            radius, detail = classify_governed_change(kind, cls, old, new)
            if radius is None:
                continue

            if g not in proposals_cache:
                proposals_cache[g] = _pending_proposal_radii(root, g)
            radii = proposals_cache[g].get(os.path.realpath(abspath), set())
            prefix = (g + "/") if g else ""

            if radius == "escalating":
                if not radii:
                    findings.append(Finding("ERROR", rel, None,
                                            "escalating change (%s) with no pending proposal — an escalating "
                                            "change reaches the main line only through a reviewable proposal "
                                            "in %sproposals/ (#18)" % (detail, prefix)))
                elif "escalating" not in radii:
                    findings.append(Finding("ERROR", rel, None,
                                            "declared-vs-actual blast-radius mismatch: the pending proposal "
                                            "declares 'track1-body' but this change actually touches %s — "
                                            "that is escalating (#18)" % detail))
            elif not radii and os.path.realpath(abspath) not in appended_targets.get(g, set()):
                findings.append(Finding("WARN", rel, None,
                                        "track-1 body-only change with no new governance changelog entry — "
                                        "an agent auto-apply must append its line (#17); a maintainer's own "
                                        "edit needs none"))
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
        mem = memory_diff_findings(root, diff_base)
        findings += mem
        # Both diff modes resolve the git context independently, so a fatal
        # context ERROR (bad ref, not a repo) arrives identically from each —
        # print it once. Dedupe against the memory pass ONLY (Codex r2): a
        # stateless finding that legitimately recurs in the blast pass must
        # not be swallowed.
        mem_set = set(mem)
        findings += [f for f in blast_radius_diff_findings(root, diff_base) if f not in mem_set]
    errors = [f for f in findings if f.level == "ERROR"]
    warns = [f for f in findings if f.level == "WARN"]
    for f in findings:
        loc = f.path + ((":%d" % f.line) if f.line else "")
        print("%-5s %s  %s" % (f.level, loc, f.message))
    print("\n%d error(s), %d warning(s)" % (len(errors), len(warns)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
