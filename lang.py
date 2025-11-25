class STRING:
    def __init__(self, v): self.value = v
    def __repr__(self): return f"STRING({self.value!r})"

class KEYWORD:
    def __init__(self, v): self.value = v
    def __repr__(self): return f"KEYWORD({self.value!r})"

class IDENTIFIER:
    def __init__(self, v): self.value = v
    def __repr__(self): return f"IDENTIFIER({self.value!r})"

class OPERATOR:
    def __init__(self, v): self.value = v
    def __repr__(self): return f"OPERATOR({self.value!r})"

class EOL:
    def __repr__(self): return "EOL()"
keywords = {'if', 'elif', 'else', 'while', 'for', 'fn', 'out', 'in'}

operators = [
    '==', '!=', '>=', '<=', '**', '//', '..',  # multi-char first
    '+', '-', '*', '/', '%', '=', '<', '>', ':', ','
]

def sourceToAst(code: str):
    tokens = []
    lines = code.splitlines()
    ops_sorted = sorted(operators, key=len, reverse=True)

    i = 0
    total = len(lines)

    while i < total:
        line = lines[i]

        # ignore fully empty lines (no EOL for these)
        if not line.strip():
            i += 1
            continue

        stripped = line.lstrip()

        # ---------------- FULL LINE COMMENTS ----------------
        if (stripped.startswith("#")
            or stripped.startswith("//")
            or stripped.startswith(">")):
            tokens.append(EOL())
            i += 1
            continue

        # ---------------- MULTILINE COMMENTS ----------------
        if stripped.startswith("/*"):
            while True:
                if stripped.endswith("*/"):
                    break
                i += 1
                if i >= total:
                    break
                stripped = lines[i].strip()
            tokens.append(EOL())
            i += 1
            continue

        # ---------------- NORMAL LINE PARSING ----------------
        pos = 0
        L = len(line)

        while pos < L:
            ch = line[pos]

            # ========== STRING ==========
            if ch == '"':
                pos += 1
                s = ""
                while True:
                    if pos >= len(line):
                        s += "\n"
                        i += 1
                        if i >= total:
                            break
                        line = lines[i]
                        pos = 0
                        L = len(line)
                        continue
                    # handle escaped quote
                    if line[pos] == "\\" and pos+1 < L and line[pos+1] == '"':
                        s += '"'
                        pos += 2
                        continue
                    if line[pos] == '"':
                        pos += 1
                        break
                    s += line[pos]
                    pos += 1


                tokens.append(STRING(s))
                continue

            # ========== OPERATORS ==========
            matched = False
            for op in ops_sorted:
                if line.startswith(op, pos):
                    tokens.append(OPERATOR(op))
                    pos += len(op)
                    matched = True
                    break
            if matched:
                continue

            # ========== IDENTIFIER / KEYWORD ==========
            if ch.isalnum() or ch == "_":
                start = pos
                while pos < L and (line[pos].isalnum() or line[pos] == "_"):
                    pos += 1
                word = line[start:pos]

                if word in keywords:
                    tokens.append(KEYWORD(word))
                else:
                    tokens.append(IDENTIFIER(word))

                continue

            # ignore whitespace
            pos += 1

        tokens.append(EOL())
        i += 1

    return tokens

code = '''
# Simple variable assignment
x = 10
y = "this is a string with operators = + - * / and quotes inside: \\"nested\\""

# Multiline string
multiline = "
this is
a multi-line
string with = + // ** operators
and line breaks
"

# Comments of all types
/* multiline comment
spanning multiple lines */
> single line comment
// another comment

# If-elif-else block
if x >= 10
    y = "big number"
elif x < 10
    y = "small number"
else
    y = "just right"

# For loop with range
for i in 1..3
    x = x + i

# Nested operators and compact spacing
z= x**2 // 3 +5-1..10

# Function definition
fn add(a, b)
    out a + b

# Single-line function
fn sub(a,b): out a - b

# Lambda
f = fn x: x * 2
'''

tokens = sourceToAst(code)
for t in tokens:
    print(t)

def transpile(tokens):
    py_lines = []
    line = []
    for tok in tokens:
        if isinstance(tok, EOL):
            if line:
                py_lines.append(" ".join(line))
                line = []
            continue
        if isinstance(tok, KEYWORD):
            if tok.value == "fn":
                line.append("def")
            else:
                line.append(tok.value)
        elif isinstance(tok, IDENTIFIER):
            line.append(tok.value)
        elif isinstance(tok, STRING):
            line.append(f'"{tok.value}"')
        elif isinstance(tok, OPERATOR):
            line.append(tok.value)
    return "\n".join(py_lines)

print(transpile(tokens))