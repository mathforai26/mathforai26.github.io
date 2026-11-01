"""Readable, reversible presentation of textual rules; no task interpretation."""

import re
import unicodedata

PROMPT = (
    "Is the following rule sound? Return 1 to certify soundness, or 0 to withhold certification.\n\n"
    "Each placeholder {{name}} ranges over every finite text. Repeated occurrences "
    "of a name receive the same text. Substitution is simultaneous: inserted text "
    "is never read as further template notation.\n\n"
    "Curly quotation marks “…” and ‘…’ mark a quotation operation: substitute inside them, "
    "then write the result as a canonical JSON string literal, escaping non-ASCII "
    "characters. Nested quotations apply this operation from the inside out. "
    "Straight quotation marks are ordinary literal text. A backslash escapes a "
    "literal brace, curly quotation mark, or backslash. The escapes \\n, \\r, \\t, "
    "\\uHHHH and \\UHHHHHHHH denote the corresponding characters; H is a hexadecimal digit. "
    "All other text and whitespace inside the fenced blocks is literal.\n\n"
    "For every assignment to the placeholders, if all premises are supported true "
    "assertions, the conclusion must also be a supported true assertion. With no "
    "premises, every instance of the conclusion must be supported true. Ill-defined "
    "or unsupported statements are not supported true assertions. Use the agreed "
    "meanings of the statements without adding task-specific assumptions. "
    "Any accompanying justification may be used to assess the rule."
)

STATEMENT_PROMPT = (
    "Is the following statement a supported true assertion? Return 1 to certify the statement, "
    "or 0 to withhold certification. Ill-defined or unsupported statements are not "
    "supported true assertions. Any accompanying justification may be used to assess the statement."
)


def escape_text(text, *, name=False):
    parts = []
    for c in text:
        if c in '\\{}“”‘’':
            parts.append('\\' + c)
        elif c == '\n' and not name:
            parts.append(c)
        elif c in '\n\r\t':
            parts.append({'\n': '\\n', '\r': '\\r', '\t': '\\t'}[c])
        elif unicodedata.category(c).startswith('C'):
            parts.append(('\\u%04x' if ord(c) <= 0xffff else '\\U%08x') % ord(c))
        else:
            parts.append(c)
    return ''.join(parts)


def render_template(template, depth=0):
    tag = template[0]
    if tag == 'text':
        return escape_text(template[1])
    if tag == 'var':
        return '{{' + escape_text(template[1], name=True) + '}}'
    if tag == 'join':
        return ''.join(render_template(t, depth) for t in template[1:])
    if tag == 'quote':
        opening, closing = ('“', '”') if depth % 2 == 0 else ('‘', '’')
        return opening + render_template(template[1], depth + 1) + closing
    raise ValueError('invalid template constructor')


def _escaped(text, pos):
    if pos + 1 >= len(text):
        raise ValueError('incomplete escape')
    c = text[pos + 1]
    if c in 'nrt':
        return {'n': '\n', 'r': '\r', 't': '\t'}[c], pos + 2
    if c in 'uU':
        width = 4 if c == 'u' else 8
        digits = text[pos + 2:pos + 2 + width]
        if len(digits) != width or not re.fullmatch('[0-9a-fA-F]+', digits):
            raise ValueError('invalid character escape')
        return chr(int(digits, 16)), pos + 2 + width
    if c not in '\\{}“”‘’':
        raise ValueError('unknown escape')
    return c, pos + 2


def parse_template(text):
    """Inverse up to association of joins and merging adjacent literal nodes."""
    def sequence(pos, closing=None):
        parts, literal = [], []
        def flush():
            if literal:
                parts.append(['text', ''.join(literal)])
                literal.clear()
        while pos < len(text):
            c = text[pos]
            if c == '\\':
                value, pos = _escaped(text, pos)
                literal.append(value)
            elif c in '“‘':
                flush()
                child, pos = sequence(pos + 1, '”' if c == '“' else '’')
                parts.append(['quote', child])
            elif c in '”’':
                if c != closing:
                    raise ValueError('unexpected end of quotation')
                flush()
                return ['join', *parts], pos + 1
            elif text.startswith('{{', pos):
                flush()
                pos += 2
                name = []
                while not text.startswith('}}', pos):
                    if pos >= len(text):
                        raise ValueError('unclosed placeholder')
                    if text[pos] == '\\':
                        value, pos = _escaped(text, pos)
                        name.append(value)
                    elif text[pos] in '{}“”‘’':
                        raise ValueError('unescaped delimiter in placeholder')
                    else:
                        name.append(text[pos]); pos += 1
                if not name:
                    raise ValueError('empty placeholder')
                parts.append(['var', ''.join(name)])
                pos += 2
            elif c in '{}':
                raise ValueError('unescaped brace')
            else:
                literal.append(c); pos += 1
        if closing is not None:
            raise ValueError('unclosed quotation')
        flush()
        return ['join', *parts], pos
    return sequence(0)[0]


def _template_has_hole(template):
    if template[0] == 'var':
        return True
    if template[0] in ('join', 'quote'):
        return any(_template_has_hole(child) for child in template[1:])
    return False


def is_direct_statement(rule):
    return not rule['premises'] and not _template_has_hole(rule['conclusion'])


def query_body(rule, justification=''):
    contents = [render_template(t) for t in rule['premises']]
    conclusion = render_template(rule['conclusion'])
    rendered_justification = escape_text(justification)
    runs = re.findall(r'`+', '\n'.join(contents + [conclusion, rendered_justification]))
    fence = '`' * max(3, 1 + max(map(len, runs), default=0))
    def block(label, text):
        return f'{label}:\n{fence}\n{text}\n{fence}'
    if is_direct_statement(rule):
        sections = [block('Statement', conclusion)]
    else:
        sections = [block(f'Premise {i}', t) for i, t in enumerate(contents, 1)]
        if not contents:
            sections.append('There are no premises.')
        sections.append(block('Conclusion', conclusion))
    if justification:
        sections.append(block('Justification', rendered_justification))
    return '\n\n'.join(sections)


def render_query(rule, justification=''):
    prompt = STATEMENT_PROMPT if is_direct_statement(rule) else PROMPT
    return prompt + '\n\n' + query_body(rule, justification)


def parse_query(question):
    """Read back the displayed rule and justification, for representation audits."""
    if question.startswith(STATEMENT_PROMPT + '\n\n'):
        direct_statement = True
        prompt = STATEMENT_PROMPT
    elif question.startswith(PROMPT + '\n\n'):
        direct_statement = False
        prompt = PROMPT
    else:
        raise ValueError('unknown query instructions')
    lines = question[len(prompt) + 2:].split('\n')
    pos, blocks, no_premises = 0, [], False
    if lines[0] == 'There are no premises.':
        no_premises = True
        pos = 2
    while pos < len(lines):
        label = lines[pos]
        fence = lines[pos + 1]
        if not re.fullmatch('`{3,}', fence):
            raise ValueError('invalid fence')
        pos += 2
        begin = pos
        while pos < len(lines) and lines[pos] != fence:
            pos += 1
        if pos == len(lines):
            raise ValueError('unclosed block')
        blocks.append((label, '\n'.join(lines[begin:pos])))
        pos += 1
        if pos < len(lines):
            if lines[pos] != '':
                raise ValueError('missing section separator')
            pos += 1
    premises, conclusion, justification = [], None, ''
    justification_seen = False
    for label, content in blocks:
        if direct_statement and label == 'Statement:' and conclusion is None:
            conclusion = parse_template(content)
        elif label == f'Premise {len(premises) + 1}:' and conclusion is None and not no_premises and not direct_statement:
            premises.append(parse_template(content))
        elif label == 'Conclusion:' and conclusion is None:
            conclusion = parse_template(content)
        elif label == 'Justification:' and conclusion is not None and not justification_seen and label == blocks[-1][0]:
            justification_seen = True
            tree = parse_template(content)
            if any(t[0] != 'text' for t in tree[1:]):
                raise ValueError('justification must be literal')
            justification = ''.join(t[1] for t in tree[1:])
        else:
            raise ValueError('invalid section order')
    if conclusion is None:
        raise ValueError('missing conclusion')
    return {'premises': premises, 'conclusion': conclusion}, justification
