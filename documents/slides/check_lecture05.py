"""Checks for the ORIGINAL lecture core, not the authors' MicroPy implementation.

Run: python3 documents/slides/check_lecture05.py
Compare an independent recursive evaluator with the explicit continuation
machine used in the slides. Check all core constructs, state restoration,
left-to-right effects, and every nonempty Boolean list through length nine.
"""

from itertools import product
import math
import random
import unittest


TRUE, FALSE, UNIT, FAIL = "true", "false", "unit", "fail"


def var(x):
    return ("var", x)


def app(f, *args):
    return ("app", f, *args)


def truth(b):
    return TRUE if b else FALSE


def evaluate(e, heap, env, defs):
    """Big-step reference, with copy-on-write heaps."""
    if isinstance(e, str):
        return e, heap
    tag, *args = e
    if tag == "var":
        return env[args[0]], heap
    if tag == "app":
        name, *es = args
        values = []
        for sub in es:
            value, heap = evaluate(sub, heap, env, defs)
            values.append(value)
        params, body = defs[name]
        assert len(params) == len(values)
        return evaluate(body, heap, dict(zip(params, values)), defs)
    if tag == "if":
        value, heap = evaluate(args[0], heap, env, defs)
        return evaluate(args[1] if value == TRUE else args[2], heap, env, defs)
    if tag == "seq":
        _, heap = evaluate(args[0], heap, env, defs)
        return evaluate(args[1], heap, env, defs)
    if tag == "try":
        value, new_heap = evaluate(args[0], heap, env, defs)
        if value == FAIL:
            return evaluate(args[1], heap, env, defs)
        return value, new_heap
    if tag == "eq":
        left, heap = evaluate(args[0], heap, env, defs)
        right, heap = evaluate(args[1], heap, env, defs)
        return truth(left == right), heap
    if tag in ("has", "get"):
        obj, heap = evaluate(args[0], heap, env, defs)
        key = obj, args[1]
        return (truth(key in heap) if tag == "has" else heap[key]), heap
    if tag == "set":
        obj, heap = evaluate(args[0], heap, env, defs)
        value, heap = evaluate(args[2], heap, env, defs)
        return UNIT, {**heap, (obj, args[1]): value}
    raise AssertionError(e)


def execute(expr, heap, env, defs):
    """Small-step environment/continuation machine specified in the slides."""
    heap, env, stack, e = dict(heap), dict(env), [], expr
    for steps in range(100000):
        if isinstance(e, tuple):
            tag, *args = e
            if tag == "var":
                e = env[args[0]]
            elif tag == "app":
                name, *es = args
                if es:
                    stack.append(("args", name, [], es[1:]))
                    e = es[0]
                else:
                    params, e = defs[name]
                    assert not params
                    stack.append(("return", env))
                    env = {}
            elif tag in ("if", "seq"):
                stack.append((tag, *args[1:]))
                e = args[0]
            elif tag == "try":
                stack.append(("try", heap, args[1]))
                e = args[0]
            elif tag == "eq":
                stack.append(("eqL", args[1]))
                e = args[0]
            elif tag in ("has", "get"):
                stack.append((tag, args[1]))
                e = args[0]
            elif tag == "set":
                stack.append(("setL", args[1], args[2]))
                e = args[0]
            else:
                raise AssertionError(tag)
            continue

        if not stack:
            return e, heap, env, steps
        tag, *args = stack.pop()
        if tag == "return":
            env = args[0]
        elif tag == "args":
            name, values, es = args
            values = values + [e]
            if es:
                stack.append(("args", name, values, es[1:]))
                e = es[0]
            else:
                params, e = defs[name]
                assert len(params) == len(values)
                stack.append(("return", env))
                env = dict(zip(params, values))
        elif tag == "if":
            e = args[0] if e == TRUE else args[1]
        elif tag == "seq":
            e = args[0]
        elif tag == "try":
            if e == FAIL:
                heap, e = args
        elif tag == "eqL":
            stack.append(("eqR", e))
            e = args[0]
        elif tag == "eqR":
            e = truth(args[0] == e)
        elif tag == "has":
            e = truth((e, args[0]) in heap)
        elif tag == "get":
            e = heap[e, args[0]]
        elif tag == "setL":
            stack.append(("setR", e, args[0]))
            e = args[1]
        elif tag == "setR":
            heap = {**heap, (args[0], args[1]): e}
            e = UNIT
        else:
            raise AssertionError(tag)
    raise AssertionError("Step budget exhausted")


V = var("x")
FLIP = ("seq", ("set", V, "bit", ("if", ("get", V, "bit"), FALSE, TRUE)),
        ("if", ("has", V, "next"), app("flip", ("get", V, "next")), UNIT))
DEFS = {"id": (["x"], V), "flip": (["x"], FLIP),
        "first": (["x", "y"], V), "constant": ([], TRUE)}


class SemanticsTests(unittest.TestCase):
    def compare(self, e, heap=None, env=None):
        heap = {} if heap is None else heap
        env = {"x": "outer"} if env is None else env
        value, new_heap = evaluate(e, heap, env, DEFS)
        got, got_heap, got_env, steps = execute(e, heap, env, DEFS)
        self.assertEqual((got, got_heap), (value, new_heap))
        self.assertEqual(got_env, env)
        return got, got_heap, steps

    def test_scope_and_nested_calls(self):
        self.assertEqual(self.compare(app("id", app("id", "inner")))[0], "inner")
        self.assertEqual(self.compare(("seq", app("id", "inner"), V))[0], "outer")
        self.assertEqual(self.compare(app("constant"))[0], TRUE)

    def test_all_lists_through_length_nine(self):
        count = 0
        for n in range(1, 10):
            for bits in product((FALSE, TRUE), repeat=n):
                heap = {(f"o{j}", "bit"): b for j, b in enumerate(bits)}
                heap.update({(f"o{j}", "next"): f"o{j+1}" for j in range(n-1)})
                heap[("untouched", "a")] = "v"
                value, final, _ = self.compare(app("flip", "o0"), heap)
                self.assertEqual(value, UNIT)
                expected = {**heap, **{(f"o{j}", "bit"): truth(b != TRUE)
                                      for j, b in enumerate(bits)}}
                self.assertEqual(final, expected)
                count += 1
        self.assertEqual(count, 1022)

    def test_rollback_and_repeated_writes(self):
        heap = {("o", "a"): FALSE}
        attempt = ("seq", ("set", "o", "a", TRUE),
                   ("seq", ("set", "o", "a", UNIT), FAIL))
        self.assertEqual(self.compare(("try", attempt, ("get", "o", "a")), heap)[:2],
                         (FALSE, heap))
        success = ("try", ("seq", ("set", "o", "a", TRUE), UNIT), FALSE)
        self.assertEqual(self.compare(success, heap)[:2], (UNIT, {("o", "a"): TRUE}))
        nested = ("try", ("seq", ("set", "o", "a", TRUE),
                  ("try", ("seq", ("set", "o", "a", UNIT), FAIL), FAIL)),
                  ("get", "o", "a"))
        self.assertEqual(self.compare(nested, heap)[:2], (FALSE, heap))

    def test_left_to_right_argument_effects(self):
        heap = {("o", "a"): FALSE}
        e = app("first", ("seq", ("set", "o", "a", TRUE), "o"), ("get", "o", "a"))
        self.assertEqual(self.compare(e, heap)[:2], ("o", {("o", "a"): TRUE}))
        e = app("first", ("get", "o", "a"), ("set", "o", "a", TRUE))
        self.assertEqual(self.compare(e, heap)[:2], (FALSE, {("o", "a"): TRUE}))

    def test_generated_core_expressions(self):
        rng = random.Random(654)
        def generate(depth):
            if depth == 0:
                return rng.choice([TRUE, FALSE, UNIT, FAIL, "o", V])
            tag = rng.choice(["if", "seq", "try", "eq", "get", "has", "set", "app"])
            if tag == "app":
                return app("id", generate(depth-1))
            if tag in ("get", "has"):
                return (tag, "o", "a")
            if tag == "set":
                return (tag, "o", "a", generate(depth-1))
            return (tag, *(generate(depth-1) for _ in range(3 if tag == "if" else 2)))
        for _ in range(2000):
            self.compare(generate(4), {("o", "a"): FALSE})

    def test_retrieval_margin(self):
        for m in (2, 10, 100, 1000):
            eps = 0.01
            margin = math.log((m-1)*(1-eps)/eps)
            weight = 1 / (1 + (m-1)*math.exp(-margin))
            self.assertAlmostEqual(weight, 1-eps)

    def test_reported_totals(self):
        self.assertEqual(sum([9, 9, 9, 9, 180, 36]), 252)
        self.assertEqual(sum([2250, 3060, 12753, 24379, 172251, 10015]), 224708)


if __name__ == "__main__":
    unittest.main(verbosity=2)
