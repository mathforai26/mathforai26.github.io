"""Textual rule templates shared by the untrusted example generators."""

from runtime import correct, instantiate, join, quoted, rule, var


def text(template):
    return template if isinstance(template, str) else instantiate(template, {})


def under(context, statement):
    return join("Under the rules and facts in ", quoted(context),
                ", the following Boolean statement is well-defined and true:\n", quoted(statement))


def meaningful(context, statement):
    return join("Under the rules and facts in ", quoted(context), ", the text ",
                quoted(statement), " is a well-defined Boolean statement.")


def both(p, q):
    return join("Both of the following statements hold:\n", quoted(p), "\n", quoted(q))


def either(p, q):
    return join("At least one of the following statements holds:\n", quoted(p), "\n", quoted(q))


def iff(p, q):
    return join("The following statements are equivalent:\n", quoted(p), "\n", quoted(q))


def closed(statement):
    return statement


C, P, Q = var("C"), var("P"), var("Q")
AND_INTRO = rule([under(C, P), under(C, Q)], under(C, both(P, Q)))
AND_LEFT = rule([under(C, both(P, Q))], under(C, P))
AND_RIGHT = rule([under(C, both(P, Q))], under(C, Q))
OR_INTRO = rule([under(C, P), meaningful(C, Q)], under(C, either(P, Q)))
IFF_USE = rule([under(C, iff(P, Q)), under(C, Q)], under(C, P))
PLAIN_AND_INTRO = rule([P, Q], both(P, Q))
LOGIC_RULES = [AND_INTRO, AND_LEFT, AND_RIGHT, OR_INTRO, IFF_USE, PLAIN_AND_INTRO]


def numeral(n):
    return join("The text ", quoted(n), " is the canonical decimal numeral for a "
                "nonnegative integer: either 0 or a digit from 1 through 9 "
                "followed by zero or more digits from 0 through 9.")


def expression(op, a, b):
    if op == "min":
        return join("min(", a, ", ", b, ")")
    return join("(", a, " ", op, " ", b, ")")


def value(expr, result):
    return join("The text ", quoted(expr), " is a well-formed closed expression "
                "using canonical decimal numerals for integers, the Boolean constants "
                "true and false, and the following operations with their usual typed "
                "meanings: addition (+), multiplication (*), subtraction (-), "
                "comparison (< and >=), conjunction (and), disjunction (or), "
                "and minimum (min). Binary operations are fully parenthesized; "
                "minimum is written min(a, b). It evaluates to the value represented by ",
                quoted(result), ". This result text is a canonical decimal numeral "
                "for an integer or a Boolean literal, matching the expression's type.")


OPS = ("+", "*", "-", "min", "<", ">=", "and", "or")


def calculation(op, a, b, result):
    if op in ("and", "or"):
        inputs = "Boolean literals, each either true or false"
        output = "a Boolean literal, either true or false"
    else:
        inputs = "canonical decimal numerals for integers"
        output = ("a Boolean literal, either true or false" if op in ("<", ">=")
                  else "a canonical decimal numeral for an integer")
    return join("The texts ", quoted(a), " and ", quoted(b), " are ", inputs,
                ". Applying the usual ", op, " operation to the values they denote gives "
                "the value represented by ", quoted(result), ", which is ", output, ".")


LITERAL_VALUE = rule([closed(numeral(var("n")))], closed(value(var("n"), var("n"))))
EVALUATE = {
    op: rule([closed(value(var("A"), var("a"))),
              closed(value(var("B"), var("b"))),
              closed(calculation(op, var("a"), var("b"), var("c")))],
             closed(value(expression(op, var("A"), var("B")), var("c"))))
    for op in OPS
}


def number_question(request, expr):
    return join("The request ", quoted(request), " asks a numerical question equivalent "
                "to finding the value of the "
                "well-formed closed arithmetic expression ", quoted(expr),
                ", whose value is a nonnegative integer. For every canonical "
                "nonnegative decimal numeral n, n correctly answers the request "
                "if and only if it denotes that value.")


def boolean_question(request, expr):
    return join("The request ", quoted(request), " asks a yes/no question equivalent "
                "to whether the well-formed closed Boolean expression ", quoted(expr),
                ' is true. The answer "Yes." is correct exactly when the expression is true; '
                'the answer "No." is correct exactly when the expression is false.')


def same_number_question(first, second):
    return join("The requests ", quoted(first), " and ", quoted(second),
                " are well-defined questions asking for a nonnegative integer, "
                "and have exactly the same correct canonical nonnegative decimal numeral answers.")


def asks_for_value(request, expr):
    return join("The request ", quoted(request), " asks for the value, written as a "
                "canonical decimal numeral, of the arithmetic expression ", quoted(expr), ".")


def expression_value(expr, result):
    return join("The arithmetic expression ", quoted(expr), " has the value represented "
                "by the canonical decimal numeral ", quoted(result), ".")


NUMBER_REFORM = rule([closed(same_number_question(var("x"), var("z"))),
                      closed(number_question(var("z"), var("e")))],
                     closed(number_question(var("x"), var("e"))))
NUMBER_ANSWER = rule([closed(number_question(var("x"), var("e"))),
                      closed(value(var("e"), var("y")))], correct(var("x"), var("y")))
SIMPLE_NUMBER_ANSWER = rule([asks_for_value(var("x"), var("e")),
                             expression_value(var("e"), var("y"))],
                            correct(var("x"), var("y")))
BOOLEAN_ANSWER = {
    truth: rule([closed(boolean_question(var("x"), var("e"))),
                 closed(value(var("e"), truth))], correct(var("x"), answer))
    for truth, answer in (("true", "Yes."), ("false", "No."))
}


def scalar(value):
    if type(value) is bool:
        return "true" if value else "false"
    return str(value)


def compute(op, a, b):
    if op == "+":
        return a + b
    if op == "*":
        return a * b
    if op == "-":
        return a - b
    if op == "min":
        return min(a, b)
    if op == "<":
        return a < b
    if op == ">=":
        return a >= b
    if op == "and":
        return a and b
    if op == "or":
        return a or b
    raise ValueError(op)
