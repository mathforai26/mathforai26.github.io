"""Untrusted example generators and a finite table of verifier judgments."""

from __future__ import annotations

import json
from pathlib import Path

from runtime import (check, correct, instantiate, join, literal, query, quoted,
                     resolve, rule, span, step, var)
import example_rules as er


class Builder:
    """Certificate construction belongs to the untrusted generator."""

    def __init__(self, request: str, answer: str):
        self.request = request
        self.candidate = {"answer": answer, "steps": []}
        self.labels = {}
        self._numbers = {}
        self._values = {}

    def add(self, r, bindings=None, premises=None, justification=""):
        records = self.candidate["steps"]
        records.append(step(r, bindings or {}, premises or [], justification))
        return len(records) - 1

    def number(self, n):
        n = str(n)
        if n not in self._numbers:
            self._numbers[n] = self.add(rule([], er.closed(er.numeral(n))))
        return self._numbers[n]

    def evaluate(self, tree):
        if not isinstance(tree, tuple):
            expr, result = er.scalar(tree), tree
            if expr not in self._values:
                if type(tree) is bool:
                    index = self.add(rule([], er.closed(er.value(expr, expr))))
                else:
                    premise = self.number(tree)
                    index = self.add(er.LITERAL_VALUE, {"n": expr}, [premise])
                self._values[expr] = (result, index)
            return expr, *self._values[expr]
        op, left, right = tree
        a_expr, a, a_index = self.evaluate(left)
        b_expr, b, b_index = self.evaluate(right)
        expr = er.text(er.expression(op, a_expr, b_expr))
        if expr not in self._values:
            result = er.compute(op, a, b)
            aa, bb, cc = er.scalar(a), er.scalar(b), er.scalar(result)
            fact = self.add(rule([], er.closed(er.calculation(op, aa, bb, cc))))
            index = self.add(er.EVALUATE[op],
                             {"A": a_expr, "B": b_expr, "a": aa, "b": bb, "c": cc},
                             [a_index, b_index, fact])
            self._values[expr] = (result, index)
        return expr, *self._values[expr]


def proposed_block_span(request, opening, closing):
    """An untrusted generator proposes endpoints; CHECK only copies and matches."""
    start = request.index(opening) + len(opening)
    return span("input", start, request.index(closing, start))


DESK_REQUEST = (
    "Give me 40 single-sentence instructions for tidying a desk. Each instruction "
    "must describe a concrete action, be understandable without the other "
    "instructions, and contain at most twelve words. Count words by splitting "
    "on whitespace. Put one instruction on each line."
)

DESK_ACTIONS = [
    "Place loose pens in a pen holder.",
    "Stack loose notebooks neatly on the desk.",
    "Put loose paper clips in a small container.",
    "Place erasers together in a drawer.",
    "Return scissors to a designated drawer.",
    "Put sticky notes in a single stack.",
    "Move empty mugs from the desk to the kitchen.",
    "Put discarded wrappers in a wastebasket.",
    "Stack unread letters in a designated tray.",
    "File receipts in a labeled folder.",
    "Place charging cables in a designated drawer.",
    "Put loose batteries in a storage container.",
    "Place keys in a designated dish.",
    "Return books to a bookshelf.",
    "Put rulers together in a drawer.",
    "Wipe dust from the desktop with a dry cloth.",
    "Place coasters together near the desk corner.",
    "Put spare headphones in a storage pouch.",
    "Stack business cards in a card holder.",
    "Place loose envelopes in a stationery tray.",
    "Put binder clips in a small container.",
    "Return markers to a marker holder.",
    "Place pencils in a pencil cup.",
    "Move the stapler to a designated desk corner.",
    "Put spare staples in a drawer.",
    "Arrange folders upright in a file organizer.",
    "Place loose photographs in a protective envelope.",
    "Return the tape dispenser to its designated spot.",
    "Put charging adapters together in a storage box.",
    "Place unused index cards in a single stack.",
    "Move empty food containers away from the desk.",
    "Place a desk calendar beside the monitor.",
    "Put the calculator in a designated drawer.",
    "Gather loose rubber bands into a small container.",
    "Place the keyboard squarely in front of the monitor.",
    "Position the mouse beside the keyboard.",
    "Return the hole punch to a designated drawer.",
    "Put unused labels in a stationery folder.",
    "Place external storage drives in a designated case.",
    "Move scattered bookmarks into a single container.",
]


def desk_form(e):
    return join("The text ", quoted(e), " contains no newline and consists of one "
                "sentence with at most twelve whitespace-separated words.")


def desk_meaning(e):
    return join("The text ", quoted(e), " describes a concrete action for tidying "
                "a desk and is understandable without other instructions.")


def good(e):
    return er.both(desk_form(e), desk_meaning(e))


def all_good(entries, count):
    return join("The text ", quoted(count), " contains only bars. The text ",
                quoted(entries), " has exactly as many lines as there are bars, "
                "with each line ending in a newline. Each line, excluding its "
                "terminating newline, is one sentence with at most twelve "
                "whitespace-separated words, describes a concrete action for "
                "tidying a desk, and is understandable without the other instructions.")


def desk_specification(request):
    return join("Every text consisting of exactly forty newline-terminated lines, "
                "each line, excluding its terminating newline, consisting of one sentence "
                "with at most twelve whitespace-separated "
                "words, describing a concrete action for tidying a desk, and understandable "
                "without the other lines, correctly answers the request ", quoted(request), ".")


DESK_SPECIFICATION = rule([], desk_specification(DESK_REQUEST))
DESK_BASE = rule([], er.closed(all_good("", "")))
DESK_APPEND = rule([er.closed(all_good(var("L"), var("n"))), er.closed(good(var("e")))],
                   er.closed(all_good(join(var("L"), var("e"), "\n"), join(var("n"), "|"))))
DESK_FINISH = rule([desk_specification(var("x")), all_good(var("L"), "|" * 40)],
                   correct(var("x"), var("L")))


def desk_example(actions=None):
    actions = DESK_ACTIONS if actions is None else actions
    b = Builder(DESK_REQUEST, "".join(s + "\n" for s in actions))
    specification = b.add(DESK_SPECIFICATION)
    b.labels["answer_requirements"] = specification
    previous = b.add(DESK_BASE)
    prefix = ""
    for i, action in enumerate(actions):
        form = b.add(rule([], er.closed(desk_form(action))))
        meaning = b.add(rule([], er.closed(desk_meaning(action))))
        leaf = b.add(er.PLAIN_AND_INTRO,
                     {"P": er.text(desk_form(action)), "Q": er.text(desk_meaning(action))},
                     [form, meaning])
        previous = b.add(DESK_APPEND, {"L": prefix, "n": "|" * i, "e": action},
                         [previous, leaf])
        prefix += action + "\n"
    b.labels["complete_output"] = previous
    b.add(DESK_FINISH, {"x": span("input", 0, len(b.request)), "L": prefix},
          [specification, previous])
    return b


SIMPLE_TAX_REQUEST = (
    "An applicant meets the standard qualification exactly when they are "
    "resident and have income below the limit.\n\n"
    "An applicant is eligible exactly when both conditions hold: they meet "
    "the standard qualification or are a qualifying student; and they have "
    "not received benefit B. These are the complete eligibility conditions.\n\n"
    "I am resident, my income is below the limit, and I have not received "
    "benefit B. I do not know whether I am a qualifying student.\n\n"
    "Am I eligible under these rules?"
)


def under_simple_tax(claim):
    return er.under(SIMPLE_TAX_REQUEST, claim)


RESIDENT = "The applicant is resident."
LOW_INCOME = "The applicant has income below the limit."
STANDARD = "The applicant meets the standard qualification."
STUDENT = "The applicant is a qualifying student."
NO_BENEFIT = "The applicant has not received benefit B."
ELIGIBLE = "The applicant is eligible."
RESIDENT_LOW = er.text(er.both(RESIDENT, LOW_INCOME))
STANDARD_OR_STUDENT = er.text(er.either(STANDARD, STUDENT))
ELIGIBILITY_CONDITION = er.text(er.both(STANDARD_OR_STUDENT, NO_BENEFIT))
SIMPLE_TAX_INTERPRET = [
    rule([], under_simple_tax(er.both(er.both(RESIDENT, LOW_INCOME), NO_BENEFIT))),
    rule([], under_simple_tax(er.iff(STANDARD, er.both(RESIDENT, LOW_INCOME)))),
    rule([], under_simple_tax(er.iff(ELIGIBLE, er.both(er.either(STANDARD, STUDENT), NO_BENEFIT)))),
    rule([], er.meaningful(SIMPLE_TAX_REQUEST, STUDENT)),
]
SIMPLE_TAX_FINISH = rule([under_simple_tax(ELIGIBLE)],
                         correct(SIMPLE_TAX_REQUEST, "Yes, you are eligible."))


def simple_tax_example():
    b = Builder(SIMPLE_TAX_REQUEST, "Yes, you are eligible.")
    facts, qualification_rule, eligibility_rule, student_type = [b.add(r) for r in SIMPLE_TAX_INTERPRET]
    b.labels.update(input_facts=facts, qualification_definition=qualification_rule,
                    eligibility_definition=eligibility_rule, student_statement=student_type)
    bindings = {"C": SIMPLE_TAX_REQUEST, "P": RESIDENT_LOW, "Q": NO_BENEFIT}
    resident_low = b.add(er.AND_LEFT, bindings, [facts])
    no_benefit = b.add(er.AND_RIGHT, bindings, [facts])
    standard = b.add(er.IFF_USE,
                     {"C": SIMPLE_TAX_REQUEST, "P": STANDARD, "Q": RESIDENT_LOW},
                     [qualification_rule, resident_low])
    disjunction = b.add(er.OR_INTRO,
                        {"C": SIMPLE_TAX_REQUEST, "P": STANDARD, "Q": STUDENT},
                        [standard, student_type])
    condition = b.add(er.AND_INTRO,
                      {"C": SIMPLE_TAX_REQUEST, "P": STANDARD_OR_STUDENT, "Q": NO_BENEFIT},
                      [disjunction, no_benefit])
    eligible = b.add(er.IFF_USE,
                     {"C": SIMPLE_TAX_REQUEST, "P": ELIGIBLE, "Q": ELIGIBILITY_CONDITION},
                     [eligibility_rule, condition])
    b.labels["eligibility"] = eligible
    b.add(SIMPLE_TAX_FINISH, premises=[eligible])
    return b


def math_question(a, b, c):
    return join("What do you get if you multiply the sum of ", a, " and ", b,
                " by ", c, "?")


def math_instruction(a, b, c):
    return join("Add ", a, " and ", b, ", then multiply the result by ", c, ".")


MATH_SPECIFICATION = rule([er.closed(er.numeral(var(n))) for n in ("a", "b", "c")],
                 er.closed(er.number_question(math_question(var("a"), var("b"), var("c")),
                     er.expression("*", er.expression("+", var("a"), var("b")), var("c")))))
MATH_REPHRASE = rule([er.closed(er.numeral(var(n))) for n in ("a", "b", "c")],
                     er.closed(er.same_number_question(
                         math_instruction(var("a"), var("b"), var("c")),
                         math_question(var("a"), var("b"), var("c")))))


def math_example(a=17, b=25, c=3, *, rephrased=False):
    constructor = math_instruction if rephrased else math_question
    request = er.text(constructor(str(a), str(b), str(c)))
    out = Builder(request, str((a + b) * c))
    numbers = [out.number(n) for n in (a, b, c)]
    start_a = len("What do you get if you multiply the sum of ")
    start_b = start_a + len(str(a)) + len(" and ")
    start_c = start_b + len(str(b)) + len(" by ")
    bindings = ({"a": str(a), "b": str(b), "c": str(c)} if rephrased else
                {"a": span("input", start_a, start_a + len(str(a))),
                 "b": span("input", start_b, start_b + len(str(b))),
                 "c": span("input", start_c, start_c + len(str(c)))})
    specification = out.add(MATH_SPECIFICATION, bindings, numbers)
    expr, result, evaluation = out.evaluate(("*", ("+", a, b), c))
    if rephrased:
        equivalent = out.add(MATH_REPHRASE, {"a": str(a), "b": str(b), "c": str(c)}, numbers)
        specification = out.add(er.NUMBER_REFORM,
                          {"x": span("input", 0, len(request)),
                           "z": er.text(math_question(str(a), str(b), str(c))), "e": expr},
                          [equivalent, specification])
    out.labels["answer_condition"] = specification
    out.labels["evaluation"] = evaluation
    out.add(er.NUMBER_ANSWER,
            {"x": span("input", 0, len(request)), "e": expr,
             "y": span("answer", 0, len(str(result)))}, [specification, evaluation])
    return out


def simple_math_example(a=17, b=25, c=3):
    """A three-record certificate that leaves the short calculation intact."""
    request = er.text(math_question(str(a), str(b), str(c)))
    expr = er.text(er.expression("*", er.expression("+", str(a), str(b)), str(c)))
    answer = str((a + b) * c)
    out = Builder(request, answer)
    interpretation = out.add(rule([], er.asks_for_value(request, expr)))
    calculation = out.add(rule([], er.expression_value(expr, answer)))
    out.labels.update(interpretation=interpretation, calculation=calculation)
    out.add(er.SIMPLE_NUMBER_ANSWER,
            {"x": span("input", 0, len(request)), "e": expr,
             "y": span("answer", 0, len(answer))},
            [interpretation, calculation])
    return out


TAX_HEADER = (
    "Apply only the complete fictional code supplied below. All case statements "
    "describe the same applicant. Quoted flag names denote exact strings. "
    "Part E lists all additional exclusions. The applicant is excluded under Part E "
    "if any listed clause applies. "
    "Every statement in the Case block is supplied as a fact. "
    "The Definitions block applies throughout this request.\n"
)
DEFINITIONS_START, DEFINITIONS_END = "Definitions:\n", "End definitions.\n"
EXCLUSIONS_START, EXCLUSIONS_END = "Part E:\n", "End Part E.\n"
CASE_START, CASE_END = "Case:\n", "End case.\n"
ALLOWANCES_START, ALLOWANCES_END = "Part A:\n", "End Part A.\n"
TAX_QUESTION = "Question: Is the applicant eligible for credit C?"
TAX_CORE = (
    "Section 10. The applicant is eligible for credit C exactly when the applicant "
    "is resident under section 40, has assessable income under section 112 below "
    "20000, has not received benefit B, and is not excluded under section 950 "
    "or Part E.\n"
    "Section 40. The applicant is resident exactly when the applicant has at least "
    "183 days of residence.\n"
    "Section 112. Assessable income is earnings minus the deduction under section 113.\n"
    "Section 113. The deduction is the smaller of approved training expenses and 500.\n"
    "Section 950. An applicant younger than 18 is excluded.\n"
)
def case_text(days, earnings, expenses, age, received=False):
    benefit = ("The applicant has received benefit B.\n" if received else
               "The applicant has not received benefit B.\n")
    return join("The applicant has ", days, " days of residence, earnings of ",
                earnings, ", approved training expenses of ", expenses,
                ", and age ", age, ". ", benefit)


CASE_YES = er.text(case_text("190", "20300", "700", "23"))
CASE_NO = er.text(case_text("190", "20300", "700", "17"))


def exclusion(name):
    return join("An applicant with disqualification flag ", quoted(name), " is excluded.\n")


def flag_fact(name):
    return join("Disqualification flag ", quoted(name), " is false.\n")


def pair(e, f):
    return join("The text ", quoted(e), " is exactly one clause of the form "
                "'An applicant with disqualification flag NAME is excluded.' "
                "followed by a newline, where NAME is a canonical JSON string literal. "
                "The text ", quoted(f), " is exactly 'Disqualification flag NAME is false.' "
                "followed by a newline, with the identical NAME. The quoted name denotes a string.")


def all_exclusions(e, f):
    return join("The text ", quoted(e), " consists entirely of zero or more clauses "
                "'An applicant with disqualification flag NAME is excluded.' followed "
                "by a newline. The text ", quoted(f), " consists of the same number "
                "of statements 'Disqualification flag NAME is false.' followed by "
                "a newline, in corresponding order with identical NAME in each pair. "
                "Every NAME is a canonical JSON string literal denoting a string. "
                "Consequently none of these exclusions applies to this applicant "
                "under these supplied facts.")


def full_tax_question(exclusions, case, facts):
    return join(TAX_HEADER, DEFINITIONS_START, TAX_CORE, DEFINITIONS_END,
                EXCLUSIONS_START, exclusions, EXCLUSIONS_END,
                CASE_START, case, facts, CASE_END, TAX_QUESTION)


EXCLUSION_PAIR = rule([], er.closed(pair(exclusion(var("t")), flag_fact(var("t")))))
EXCLUSION_BASE = rule([], er.closed(all_exclusions("", "")))
EXCLUSION_APPEND = rule([er.closed(all_exclusions(var("E"), var("F"))),
                         er.closed(pair(var("e"), var("f")))],
                        er.closed(all_exclusions(join(var("E"), var("e")),
                                                 join(var("F"), var("f")))))


def tax_expression(days, earnings, expenses, age, received=False):
    conditions = [er.expression(">=", days, "183"),
                  er.expression("<", er.expression("-", earnings,
                                                  er.expression("min", expenses, "500")), "20000"),
                  "false" if received else "true",
                  er.expression(">=", age, "18")]
    return er.expression("and", conditions[0],
                         er.expression("and", conditions[1],
                                       er.expression("and", conditions[2], conditions[3])))


FULL_TAX_SPECIFICATION = {
    received: rule([er.closed(er.numeral(var(n))) for n in ("d", "w", "t", "a")]
                   + [er.closed(all_exclusions(var("E"), var("F")))],
                   er.closed(er.boolean_question(
                       full_tax_question(var("E"),
                           case_text(var("d"), var("w"), var("t"), var("a"), received), var("F")),
                       tax_expression(var("d"), var("w"), var("t"), var("a"), received))))
    for received in (False, True)
}
FULL_TAX_RULES = [EXCLUSION_PAIR, EXCLUSION_BASE, EXCLUSION_APPEND, *FULL_TAX_SPECIFICATION.values()]


def full_tax_example(names=("overseas-credit", "duplicate-award", "late-filing"), young=False,
                     *, days=190, earnings=20300, expenses=700, age=None, received=False):
    age = (17 if young else 23) if age is None else age
    case = er.text(case_text(str(days), str(earnings), str(expenses), str(age), received))
    eligible = days >= 183 and earnings - min(expenses, 500) < 20000 and not received and age >= 18
    entries = [(er.text(exclusion(name)), er.text(flag_fact(name))) for name in names]
    exceptions = "".join(e for e, _ in entries)
    facts = "".join(f for _, f in entries)
    request = er.text(full_tax_question(exceptions, case, facts))
    out = Builder(request, "Yes." if eligible else "No.")
    previous = out.add(EXCLUSION_BASE)
    e_prefix = f_prefix = ""
    for name, (e, f) in zip(names, entries):
        leaf = out.add(EXCLUSION_PAIR, {"t": name})
        previous = out.add(EXCLUSION_APPEND,
                           {"E": e_prefix, "F": f_prefix, "e": e, "f": f}, [previous, leaf])
        e_prefix += e
        f_prefix += f
    out.labels["complete_exclusions"] = previous
    numbers = [out.number(n) for n in (days, earnings, expenses, age)]
    flags = proposed_block_span(request, CASE_START, CASE_END)
    flags["start"] += len(case)
    specification = out.add(FULL_TAX_SPECIFICATION[received],
                      {"E": proposed_block_span(request, EXCLUSIONS_START, EXCLUSIONS_END),
                       "F": flags, "d": str(days), "w": str(earnings),
                       "t": str(expenses), "a": str(age)}, numbers + [previous])
    tree = ("and", (">=", days, 183),
            ("and", ("<", ("-", earnings, ("min", expenses, 500)), 20000),
             ("and", not received, (">=", age, 18))))
    expr, result, evaluation = out.evaluate(tree)
    out.labels["answer_condition"] = specification
    out.labels["evaluation"] = evaluation
    out.add(er.BOOLEAN_ANSWER[er.scalar(result)],
            {"x": span("input", 0, len(request)), "e": expr}, [specification, evaluation])
    return out


ALLOWANCE_CORE = (
    "Section 10. The applicant is eligible for credit C exactly when the applicant "
    "is resident under section 40, has assessable income under section 112 below "
    "20000, has not received benefit B, and is not excluded under section 950 "
    "or Part E.\n"
    "Section 40. The applicant is resident exactly when the applicant has at least "
    "183 days of residence.\n"
    "Section 112. Assessable income is the remaining income computed under section 113.\n"
    "Section 113. Start with earnings as remaining income. Apply every provision "
    "in Part A exactly once, in the order written.\n"
    "Section 950. An applicant younger than 18 is excluded.\n"
)


def allowance(amount):
    return join("Deduct an allowance of ", amount, ", capped at the remaining income.\n")


def income_cap(amount):
    return join("Cap the remaining income at ", amount, ".\n")


def provision_text(provision):
    if isinstance(provision, tuple):
        kind, amount = provision
        if kind != "cap":
            raise ValueError(kind)
        return er.text(income_cap(str(amount)))
    return er.text(allowance(str(provision)))


def allowance_run(provisions, initial, final):
    return join("The texts ", quoted(initial), " and ", quoted(final),
                " are canonical decimal numerals for nonnegative integers. The text ",
                quoted(provisions), " consists entirely of zero or more newline-terminated "
                "provisions, each either 'Deduct an allowance of N, capped at the remaining "
                "income.' or 'Cap the remaining income at N.', where each N is a canonical "
                "nonnegative decimal numeral. "
                "Starting with the value represented by ", quoted(initial),
                " as remaining income, apply every provision once in order. A deduction "
                "subtracts the smaller of N and the remaining income. A cap replaces "
                "the remaining income by its minimum with N. The final remaining income "
                "is the value represented by ", quoted(final), ".")


ALLOWANCE_BASE = rule([er.numeral(var("w"))], allowance_run("", var("w"), var("w")))
ALLOWANCE_APPEND = rule(
    [allowance_run(var("A"), var("w"), var("z")), er.numeral(var("n")),
     er.calculation("min", var("z"), var("n"), var("h")),
     er.calculation("-", var("z"), var("h"), var("r"))],
    allowance_run(join(var("A"), allowance(var("n"))), var("w"), var("r")))
CAP_APPEND = rule(
    [allowance_run(var("A"), var("w"), var("z")), er.numeral(var("n")),
     er.calculation("min", var("z"), var("n"), var("r"))],
    allowance_run(join(var("A"), income_cap(var("n"))), var("w"), var("r")))


def allowance_case(days, earnings, age, received=False):
    benefit = ("has received" if received else "has not received")
    return join("The applicant has ", days, " days of residence, earnings of ",
                earnings, ", and age ", age, ". The applicant ", benefit, " benefit B.\n")


def allowance_question(provisions, exclusions, case, facts):
    return join(TAX_HEADER, DEFINITIONS_START, ALLOWANCE_CORE, DEFINITIONS_END,
                ALLOWANCES_START, provisions, ALLOWANCES_END,
                EXCLUSIONS_START, exclusions, EXCLUSIONS_END,
                CASE_START, case, facts, CASE_END, TAX_QUESTION)


def allowance_condition(days, income, age, received=False):
    return er.expression("and", er.expression(">=", days, "183"),
                         er.expression("and", er.expression("<", income, "20000"),
                                       er.expression("and", "false" if received else "true",
                                                     er.expression(">=", age, "18"))))


ALLOWANCE_SPECIFICATION = {
    received: rule([allowance_run(var("A"), var("w"), var("z")),
                    all_exclusions(var("E"), var("F")),
                    er.numeral(var("d")), er.numeral(var("a"))],
                   er.boolean_question(
                       allowance_question(var("A"), var("E"),
                           allowance_case(var("d"), var("w"), var("a"), received), var("F")),
                       allowance_condition(var("d"), var("z"), var("a"), received)))
    for received in (False, True)
}


def long_code_example(amounts=(1,) * 301, *, days=190, earnings=20300, age=23,
                      received=False, names=()):
    """The generator computes balances and proposes each calculation as a claim."""
    amounts = tuple(amounts)
    provisions = "".join(provision_text(n) for n in amounts)
    entries = [(er.text(exclusion(name)), er.text(flag_fact(name))) for name in names]
    exceptions = "".join(e for e, _ in entries)
    facts = "".join(f for _, f in entries)
    case = er.text(allowance_case(str(days), str(earnings), str(age), received))
    request = er.text(allowance_question(provisions, exceptions, case, facts))
    out = Builder(request, "")
    initial = out.number(earnings)
    previous = out.add(ALLOWANCE_BASE, {"w": str(earnings)}, [initial])
    prefix, remaining = "", earnings
    for provision in amounts:
        amount = provision[1] if isinstance(provision, tuple) else provision
        number = out.number(amount)
        deduction = min(remaining, amount)
        cap = out.add(rule([], er.calculation("min", str(remaining), str(amount), str(deduction))))
        if isinstance(provision, tuple):
            result = deduction
            previous = out.add(CAP_APPEND,
                               {"A": prefix, "w": str(earnings), "z": str(remaining),
                                "n": str(amount), "r": str(result)}, [previous, number, cap])
        else:
            result = remaining - deduction
            subtract = out.add(rule([], er.calculation("-", str(remaining), str(deduction), str(result))))
            previous = out.add(ALLOWANCE_APPEND,
                               {"A": prefix, "w": str(earnings), "z": str(remaining),
                                "n": str(amount), "h": str(deduction), "r": str(result)},
                               [previous, number, cap, subtract])
        prefix += provision_text(provision)
        remaining = result
    out.labels["complete_provisions"] = previous
    exclusions = out.add(EXCLUSION_BASE)
    e_prefix = f_prefix = ""
    for name, (e, f) in zip(names, entries):
        leaf = out.add(EXCLUSION_PAIR, {"t": name})
        exclusions = out.add(EXCLUSION_APPEND,
                             {"E": e_prefix, "F": f_prefix, "e": e, "f": f}, [exclusions, leaf])
        e_prefix += e
        f_prefix += f
    out.labels["complete_exclusions"] = exclusions
    numbers = [out.number(n) for n in (days, age)]
    flags = proposed_block_span(request, CASE_START, CASE_END)
    flags["start"] += len(case)
    specification = out.add(ALLOWANCE_SPECIFICATION[received],
                      {"A": proposed_block_span(request, ALLOWANCES_START, ALLOWANCES_END),
                       "E": proposed_block_span(request, EXCLUSIONS_START, EXCLUSIONS_END),
                       "F": flags, "d": str(days),
                       "w": str(earnings), "z": str(remaining), "a": str(age)},
                      [previous, exclusions] + numbers)
    tree = ("and", (">=", days, 183),
            ("and", ("<", remaining, 20000), ("and", not received, (">=", age, 18))))
    expr, result, evaluation = out.evaluate(tree)
    out.candidate["answer"] = "Yes." if result else "No."
    out.labels["answer_condition"] = specification
    out.labels["evaluation"] = evaluation
    out.add(er.BOOLEAN_ANSWER[er.scalar(result)],
            {"x": span("input", 0, len(request)), "e": expr}, [specification, evaluation])
    return out


def fixed_library():
    """A reproducible table for the displayed examples and scale checks."""
    representatives = [desk_example(), simple_tax_example(), simple_math_example(),
                       math_example(), math_example(rephrased=True),
                       full_tax_example(), full_tax_example(young=True),
                       full_tax_example(received=True), full_tax_example(days=182),
                       full_tax_example(earnings=21000), full_tax_example(earnings=300),
                       full_tax_example(earnings=20500),
                       full_tax_example(days=183, age=18, expenses=0, earnings=19999),
                       long_code_example(), long_code_example((1,) * 300),
                       long_code_example((), earnings=0),
                       long_code_example((500, 1), earnings=300),
                       long_code_example((1,), received=True),
                       long_code_example((("cap", 20000), 1)),
                       long_code_example((1, ("cap", 20000)))]
    rules = er.LOGIC_RULES + list(er.EVALUATE.values())
    for example in representatives:
        rules += [record["rule"] for record in example.candidate["steps"]]
    for a in (False, True):
        for b in (False, True):
            rules.append(rule([], er.closed(er.calculation("and", er.scalar(a), er.scalar(b),
                                                           er.scalar(a and b)))))
    return frozenset(query(r) for r in rules)


LIBRARY = fixed_library()
BOUND = max(len(q.encode("utf-8")) for q in LIBRARY)


def fixture(q):
    return int(q in LIBRARY)


def rejected_examples():
    """Concrete unsuccessful proposals, checked with the same runtime and fixture."""
    cases = {}

    def add(name, example, description, reason):
        cases[name] = (example, description, reason)

    add("desk-missing-entry", desk_example(DESK_ACTIONS[:-1]),
        "Return 39 suitable instructions and try to use the forty-entry finishing rule.",
        "instantiated premise differs from referenced claim")

    example = simple_tax_example()
    example.candidate["answer"] = "No, you are ineligible."
    add("simple-tax-wrong-answer", example,
        "Establish eligibility but return the opposite answer.",
        "final claim is not bound to actual input and answer")

    example = math_example()
    example.candidate["answer"] = "127"
    add("arithmetic-wrong-answer", example,
        "Establish the value 126 but return 127 using the same finishing rule.",
        "instantiated premise differs from referenced claim")

    example = math_example()
    example.candidate["answer"] = "127"
    product = example.labels["evaluation"]
    calculation = example.candidate["steps"][product]["premises"][-1]
    example.candidate["steps"][calculation]["rule"] = rule([], er.calculation("*", "42", "3", "127"))
    example.candidate["steps"][product]["bindings"]["c"] = "127"
    add("arithmetic-false-calculation", example,
        "Claim that 42 times 3 is 127, then consistently use 127 in the remaining records.",
        "verifier did not accept")

    example = full_tax_example(names=("overseas-credit", "duplicate-award"))
    example.request = full_tax_example().request.replace(
        'Disqualification flag "late-filing" is false.',
        'Disqualification flag "late-filing" is true.')
    bindings = example.candidate["steps"][example.labels["answer_condition"]]["bindings"]
    bindings["E"] = proposed_block_span(example.request, EXCLUSIONS_START, EXCLUSIONS_END)
    bindings["F"] = proposed_block_span(example.request, CASE_START, CASE_END)
    bindings["F"]["start"] += len(er.text(case_text("190", "20300", "700", "23")))
    example.candidate["steps"][-1]["bindings"]["x"] = span("input", 0, len(example.request))
    add("full-tax-omitted-exclusion", example,
        "Return Yes after certifying only the first two exclusions; the input's third flag is true.",
        "instantiated premise differs from referenced claim")

    example = long_code_example((1,) * 300)
    example.request = long_code_example().request
    bindings = example.candidate["steps"][example.labels["answer_condition"]]["bindings"]
    for name, opening, closing in (("A", ALLOWANCES_START, ALLOWANCES_END),
                                    ("E", EXCLUSIONS_START, EXCLUSIONS_END),
                                    ("F", CASE_START, CASE_END)):
        bindings[name] = proposed_block_span(example.request, opening, closing)
    bindings["F"]["start"] += len(er.text(allowance_case("190", "20300", "23")))
    example.candidate["steps"][-1]["bindings"]["x"] = span("input", 0, len(example.request))
    add("long-code-omitted-provision", example,
        "Return No using a calculation for 300 deductions when the supplied code contains 301.",
        "instantiated premise differs from referenced claim")

    example = long_code_example((("cap", 20000), 1))
    example.request = long_code_example((1, ("cap", 20000))).request
    add("long-code-reordered-provisions", example,
        "Return Yes using cap-then-deduct calculations for an input that says deduct-then-cap.",
        "instantiated premise differs from referenced claim")

    example = long_code_example()
    example.candidate["steps"] = [step(rule([], correct(example.request, "Yes.")), {}, [])]
    example.labels = {}
    add("long-code-oversized-query", example,
        "Ask the verifier to approve the correct answer directly with the entire long request quoted.",
        "complete query exceeds bound")
    return cases


def rejection_trace(example, description, expected_reason):
    result = check(example.request, example.candidate, fixture, BOUND)
    assert not result.accepted and result.reason == expected_reason, result.reason
    failed = len(result.claims) if len(result.claims) < len(example.candidate["steps"]) else None
    trace = {"input": example.request, "candidate": example.candidate,
             "description": description, "accepted": result.accepted,
             "reason": result.reason, "failed_record": failed,
             "accepted_claims": result.claims,
             "checking_questions": result.calls,
             "verdicts": [fixture(q) for q in result.calls]}
    if result.reason == "instantiated premise differs from referenced claim":
        record = example.candidate["steps"][failed]
        bindings = {name: resolve(value, example.request, example.candidate["answer"], result.claims)
                    for name, value in record["bindings"].items()}
        for premise, reference in zip(record["rule"]["premises"], record["premises"]):
            expected = instantiate(premise, bindings)
            if expected != result.claims[reference]:
                trace["failed_comparison"] = {"required_premise": expected,
                                               "referenced_record": reference,
                                               "referenced_claim": result.claims[reference]}
                break
    elif result.reason == "final claim is not bound to actual input and answer":
        trace["failed_comparison"] = {"required_goal": instantiate(
            correct(example.request, example.candidate["answer"]), {}),
            "established_claim": result.claims[-1]}
    elif result.reason == "complete query exceeds bound":
        record = example.candidate["steps"][failed]
        q = query(record["rule"], record["justification"])
        trace["unsent_query"] = q
        trace["unsent_query_bytes"] = len(q.encode())
        trace["bound_bytes"] = BOUND
    return trace


def query_samples():
    return {"desk-specification": DESK_SPECIFICATION,
            "desk-judgment": desk_example().candidate["steps"][2]["rule"],
            "contextual-conjunction": er.AND_INTRO,
            "simple-tax-facts": SIMPLE_TAX_INTERPRET[0],
            "arithmetic-simple-interpretation": simple_math_example().candidate["steps"][0]["rule"],
            "arithmetic-simple-calculation": simple_math_example().candidate["steps"][1]["rule"],
            "arithmetic-simple-composition": er.SIMPLE_NUMBER_ANSWER,
            "arithmetic-specification": MATH_SPECIFICATION,
            "arithmetic-calculation": rule([], er.calculation("+", "17", "25", "42")),
            "full-tax-specification": FULL_TAX_SPECIFICATION[False],
            "long-code-append": ALLOWANCE_APPEND,
            "long-code-cap": CAP_APPEND,
            "long-code-specification": ALLOWANCE_SPECIFICATION[False],
            "boolean-answer": er.BOOLEAN_ANSWER["true"]}


def note_outputs(stats):
    from query_text import query_body, render_template
    from note_assets import assets
    samples = query_samples()
    queries = {name: query(r) for name, r in samples.items()}
    displays = {"query-logic": query_body(er.AND_INTRO),
                "query-arithmetic-simple-interpretation": query_body(samples["arithmetic-simple-interpretation"]),
                "query-arithmetic-simple-calculation": query_body(samples["arithmetic-simple-calculation"]),
                "query-arithmetic-simple-composition": query_body(samples["arithmetic-simple-composition"]),
                "query-arithmetic": query_body(MATH_SPECIFICATION),
                "query-calculation": query_body(samples["arithmetic-calculation"]),
                "assertion-context": render_template(er.under(var("C"), var("p"))),
                "query-desk": query_body(samples["desk-judgment"]),
                "input-full-tax": full_tax_example().request,
                "assertion-desk-specification": render_template(desk_specification(var("x"))),
                "assertion-allowance-run": render_template(allowance_run(var("A"), var("w"), var("z")))}
    return assets(queries, displays, stats, len(LIBRARY), BOUND)


def export():
    directory = Path(__file__).parent / "traces"
    directory.mkdir(exist_ok=True)
    catalogue = sorted(LIBRARY)
    ids = {q: i for i, q in enumerate(catalogue)}
    (directory / "checking-questions.json").write_text(
        json.dumps({"bound_bytes": BOUND, "questions": catalogue}, indent=2) + "\n")
    stats = {}
    examples = {"desk": desk_example(), "simple-tax": simple_tax_example(),
                "arithmetic-simple": simple_math_example(),
                "arithmetic": math_example(), "arithmetic-rephrased": math_example(rephrased=True),
                "full-tax-yes": full_tax_example(), "full-tax-no": full_tax_example(young=True),
                "full-tax-benefit": full_tax_example(received=True),
                "full-tax-income": full_tax_example(earnings=20500),
                "long-code-301": long_code_example(),
                "long-code-300": long_code_example((1,) * 300),
                "cap-then-deduct": long_code_example((("cap", 20000), 1)),
                "deduct-then-cap": long_code_example((1, ("cap", 20000)))}
    for name, example in examples.items():
        result = check(example.request, example.candidate, fixture, BOUND)
        assert result.accepted, (name, result.reason)
        trace = {"input": example.request, "candidate": example.candidate,
                 "claims": result.claims, "milestones": example.labels, "checking_question_ids": [ids[q] for q in result.calls]}
        (directory / (name + ".json")).write_text(json.dumps(trace, indent=2) + "\n")
        stats[name] = {"input_bytes": len(example.request.encode()),
                       "answer_bytes": len(example.candidate["answer"].encode()),
                       "records": len(result.claims),
                       "max_query_bytes": max(len(q.encode()) for q in result.calls)}
        if name.startswith("long-code-"):
            stats[name]["code_bytes"] = len(example.request.split("Part E:\n")[0].encode()) - len(TAX_HEADER.encode())
    for name, example in {
        "full-tax-512": full_tax_example(tuple("flag-" + str(i) for i in range(512))),
        "full-tax-long-name": full_tax_example(("x" * (2 * BOUND),))
    }.items():
        result = check(example.request, example.candidate, fixture, BOUND)
        assert result.accepted, (name, result.reason)
        stats[name] = {"input_bytes": len(example.request.encode()),
                       "records": len(result.claims),
                       "max_query_bytes": max(len(q.encode()) for q in result.calls)}
    (directory / "statistics.json").write_text(json.dumps(stats, indent=2) + "\n")
    for relative, content in note_outputs(stats).items():
        path = Path(__file__).parent / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    for i, q in enumerate(catalogue):
        (directory / "queries" / f"{i:03d}.txt").write_text(q + "\n")
    rejected = directory / "rejected"
    rejected.mkdir(exist_ok=True)
    rejection_summary = {}
    for name, (example, description, reason) in rejected_examples().items():
        trace = rejection_trace(example, description, reason)
        (rejected / (name + ".json")).write_text(json.dumps(trace, indent=2) + "\n")
        rejection_summary[name] = {key: trace[key] for key in
                                  ("description", "accepted", "reason", "failed_record")}
        rejection_summary[name]["proposed_answer"] = example.candidate["answer"]
        rejection_summary[name]["accepted_records"] = len(trace["accepted_claims"])
    (rejected / "index.json").write_text(json.dumps(rejection_summary, indent=2) + "\n")
    print(json.dumps({"bound_bytes": BOUND, "distinct_questions": len(LIBRARY),
                      "examples": stats, "rejected_examples": rejection_summary}, indent=2))


if __name__ == "__main__":
    export()
