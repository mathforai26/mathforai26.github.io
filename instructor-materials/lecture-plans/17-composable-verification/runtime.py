"""Generic textual-certificate checker for the Lecture 17 technical note.

All task semantics belong to the supplied verifier. Example generators and the
finite verifier fixture live in examples.py, never in this module.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Any

Template = list  # Validated finite trees; constructors are defined below.


def literal(s: str) -> Template:
    return ["text", s]


def var(name: str) -> Template:
    return ["var", name]


def join(*parts: str | Template) -> Template:
    return ["join", *[literal(p) if isinstance(p, str) else p for p in parts]]


def quoted(part: str | Template) -> Template:
    return ["quote", literal(part) if isinstance(part, str) else part]


def valid_string(s: Any) -> bool:
    if not isinstance(s, str):
        return False
    try:
        s.encode("utf-8")
        return True
    except UnicodeEncodeError:
        return False


def holes(t: Template) -> set[str]:
    if not isinstance(t, list) or not t or not isinstance(t[0], str):
        raise ValueError("invalid template")
    tag = t[0]
    if tag in ("text", "var") and len(t) == 2 and valid_string(t[1]):
        if tag == "var" and not t[1]:
            raise ValueError("empty variable name")
        return {t[1]} if tag == "var" else set()
    if tag == "quote" and len(t) == 2:
        return holes(t[1])
    if tag == "join":
        result: set[str] = set()
        for child in t[1:]:
            result.update(holes(child))
        return result
    raise ValueError("invalid template constructor")


def instantiate(t: Template, bindings: dict[str, str]) -> str:
    tag = t[0]
    if tag == "text":
        return t[1]
    if tag == "var":
        return bindings[t[1]]
    if tag == "join":
        return "".join(instantiate(child, bindings) for child in t[1:])
    if tag == "quote":
        return json.dumps(instantiate(t[1], bindings), ensure_ascii=True)
    raise ValueError("invalid template")


def correct(request: str | Template, answer: str | Template) -> Template:
    return join("The response ", quoted(answer),
                " correctly answers the request ", quoted(request), ".")


def rule(premises: list[Template], conclusion: Template) -> dict:
    return {"premises": premises, "conclusion": conclusion}


def rule_holes(r: dict) -> set[str]:
    if not isinstance(r, dict) or set(r) != {"premises", "conclusion"}:
        raise ValueError("invalid rule fields")
    if not isinstance(r["premises"], list):
        raise ValueError("invalid premises")
    result = holes(r["conclusion"])
    for premise in r["premises"]:
        result.update(holes(premise))
    return result


# Certificates retain their explicit trees; model queries use readable text.
from query_text import PROMPT, render_query


def query(r: dict, justification: str = "") -> str:
    rule_holes(r)
    if not valid_string(justification):
        raise ValueError("invalid justification")
    return render_query(r, justification)


def step(r: dict, bindings: dict, premises: list[int], justification: str = "") -> dict:
    return {"rule": r, "bindings": bindings, "premises": premises, "justification": justification}


def span(source: str | int, start: int, end: int) -> dict:
    """Half-open Unicode-codepoint interval. source is input, answer, or a prior claim."""
    return {"source": source, "start": start, "end": end}


def resolve(value: Any, request: str, answer: str, accepted: list[str]) -> str:
    if valid_string(value):
        return value
    if not isinstance(value, dict) or set(value) != {"source", "start", "end"}:
        raise ValueError("invalid binding value")
    src, start, end = value["source"], value["start"], value["end"]
    if src == "input":
        text = request
    elif src == "answer":
        text = answer
    elif type(src) is int and 0 <= src < len(accepted):
        text = accepted[src]
    else:
        raise ValueError("unavailable span source")
    if type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(text):
        raise ValueError("out-of-bounds span")
    return text[start:end]


@dataclass
class CheckResult:
    accepted: bool
    claims: list[str]
    calls: list[str]
    reason: str


def check(request: str, candidate: Any, verifier: Callable[[str], int], bound: int) -> CheckResult:
    """Check one finite parsed candidate. No task-specific branch occurs here."""
    claims: list[str] = []
    calls: list[str] = []

    def reject(reason: str) -> CheckResult:
        return CheckResult(False, claims, calls, reason)

    try:
        if not valid_string(request) or type(bound) is not int or bound < 0:
            return reject("invalid checker arguments")
        if not isinstance(candidate, dict) or set(candidate) != {"answer", "steps"}:
            return reject("invalid candidate fields")
        answer, steps = candidate["answer"], candidate["steps"]
        if not valid_string(answer) or not isinstance(steps, list):
            return reject("invalid answer or steps")
        for record in steps:
            if not isinstance(record, dict) or set(record) != {"rule", "bindings", "premises", "justification"}:
                return reject("invalid record fields")
            r, supplied, refs = record["rule"], record["bindings"], record["premises"]
            names = rule_holes(r)
            if not isinstance(supplied, dict) or set(supplied) != names:
                return reject("incorrect binding domain")
            if not isinstance(refs, list) or len(refs) != len(r["premises"]):
                return reject("incorrect premise count")
            if any(type(i) is not int or not 0 <= i < len(claims) for i in refs):
                return reject("premise is not an earlier record")
            bindings = {n: resolve(supplied[n], request, answer, claims) for n in names}
            for t, i in zip(r["premises"], refs):
                if instantiate(t, bindings) != claims[i]:
                    return reject("instantiated premise differs from referenced claim")
            q = query(r, record["justification"])
            if len(q.encode("utf-8")) > bound:
                return reject("complete query exceeds bound")
            calls.append(q)
            verdict = verifier(q)
            if type(verdict) is not int or verdict != 1:
                return reject("verifier did not accept")
            claims.append(instantiate(r["conclusion"], bindings))
        if not claims or claims[-1] != instantiate(correct(request, answer), {}):
            return reject("final claim is not bound to actual input and answer")
        return CheckResult(True, claims, calls, "accepted")
    except (ValueError, TypeError, KeyError, IndexError, RecursionError):
        return reject("malformed candidate")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError("invalid JSON constant: " + value)


def check_json(request: str, encoded: str, verifier: Callable[[str], int], bound: int) -> CheckResult:
    try:
        candidate = json.loads(encoded, object_pairs_hook=_unique_object,
                               parse_constant=_invalid_constant)
    except (ValueError, TypeError, RecursionError):
        return CheckResult(False, [], [], "malformed JSON")
    return check(request, candidate, verifier, bound)


def encode_certificate(answer: str, applications: list[tuple]) -> str:
    """Serialize explicit (rule, justification, substitution, premise_indices) steps.

    The caller has already chosen every inference and literal substitution.
    This function makes no semantic judgments and performs no proof search.
    """
    records = [step(r, dict(substitution), list(refs), justification)
               for r, justification, substitution, refs in applications]
    return json.dumps({"answer": answer, "steps": records}, ensure_ascii=True,
                      separators=(",", ":"), sort_keys=True)


def run(request: str, generator: Callable[[str, int], str],
        verifier: Callable[[str], int], bound: int) -> str:
    """Try successive encoded candidates until one is accepted.

    Termination is conditional on the generator producing an accepted candidate.
    An unresponsive generator stalls this simple sequential runtime.
    """
    attempt = 0
    while True:
        encoded = generator(request, attempt)
        if check_json(request, encoded, verifier, bound).accepted:
            return json.loads(encoded)["answer"]
        attempt += 1


def exhaustive_generator(request: str, attempt: int) -> str:
    """Length-lexicographic byte enumeration; not a practical search method."""
    if type(attempt) is not int or attempt < 0:
        raise ValueError("invalid attempt")
    offset, length, count = attempt, 0, 1
    while offset >= count:
        offset -= count
        length += 1
        count *= 256
    raw = offset.to_bytes(length, "big")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return "{}"  # A fixed malformed candidate; no valid encoding is skipped.
