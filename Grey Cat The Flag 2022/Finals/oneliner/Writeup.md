## Files
[oneliner.py](Grey-Cat-The-Flag-2022/Finals/oneliner/oneliner.py)

## Method
Looking at [oneliner.py](Grey-Cat-The-Flag-2022/Finals/oneliner/oneliner.py), we see a nested expression consisting of ternary operator expressions. \
Some of the conditions test characters of the flag, and others are directly evaluable. We also know the flag has length `18`.

Rather than parsing the code from scratch, Python has a built-in module [`ast`]() which can be used to break down the semantics of the code for us. \
Since `ast` wraps the tree as a module, we 'unwrap' to get the underlying expression.
```py
import ast
file = open('oneliner.py')
line = file.readlines()[2]
tree = ast.parse(line).body[0].value
file.close()
```
We definitely need to reduce this nested ternary operator expression to a size we can interpret. \
To do this, there are a few ways of eliminating a ternary operator:
- If the test is unconditionally `True`, follow the true branch.
- If the test is unconditionally `False`, follow the false branch.
- If both branches have the same value, simplify to that value, regardless of the test.

How do we determine if a certain test is unconditionally `True` or `False`?
- The flag format is `grey{...}`. Since the flag length is `18`, we know the characters at index `0`, `1`, `2`, `3`, `4`, and `17`.
- There are many purely numerical calculations, we can extract the code section using offset attributes.

Write a recursive function to repeatedly do this reduction:
```py
def traverse(node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Compare):
        try:
            return eval(line[node.col_offset : node.end_col_offset])
        except NameError: # grey[idx] == 'char'
            char = {0: 'g', 1: 'r', 2: 'e', 3: 'y', 4:'{', 17: '}'}.get(node.left.slice.value)
            return node.comparators[0].value == char if char else line[node.col_offset : node.end_col_offset]
    if isinstance(node, ast.IfExp):
        ternary = {'cond': traverse(node.test), 'if': traverse(node.body), 'other': traverse(node.orelse)}
        if ternary['cond'] is True:
            return ternary['if']
        if ternary['cond'] is False:
            return ternary['other']
        if ternary['if'] == ternary['other']:
            return ternary['if']
        return ternary
    raise Exception(type(node))
```
Finally we dump the reduced expression and can extract each of the unknown flag characters from there.
```py
import json
print(json.dumps(traverse(tree), indent=2))
# {
#   "cond": {
#     "cond": {
#       "cond": {
#         "cond": {
#           "cond": {
#             "cond": {
#               "cond": {
#                 "cond": {
#                   "cond": {
#                     "cond": {
#                       "cond": {
#                         "cond": {
#                           "cond": {
#                             "cond": {
#                               "cond": {
#                                 "cond": "grey[16] == 'h'",
#                                 "if": "grey[15] == 'a'",
#                                 "other": false
#                               },
#                               "if": "grey[14] == '_'",
#                               "other": false
#                             },
#                             "if": "grey[13] == 'g'",
#                             "other": false
#                           },
#                           "if":"grey[12] == 'i'",
#                           "other": false
#                         },
#                        "if": "grey[11] == 'b'",
#                        "other": false
#                       },
#                       "if": "grey[10] == '_'",
#                       "other": false
#                     },
#                     "if": "grey[9] == 'e'",
#                     "other": false
#                   },
#                   "if": "grey[8] == 't'",
#                   "other": false
#                 },
#                 "if": "grey[7] == 'i'",
#                 "other": false
#               },
#               "if": "grey[6] == 'u'",
#               "other": false
#             },
#             "if": "grey[5] == 'q'",
#             "other": false
#           },
#           "if": true,
#           "other": false
#         },
#         "if": true,
#         "other": false
#       },
#       "if": true,
#       "other": false
#     },
#     "if": true,
#     "other": false
#   },
#   "if": true,
#   "other": false
# }
```
This challenge's generation script was generous, but we could also make the following reductions if needed:
- If the true branch is `True`, simplify to `node.test or node.orelse`.
- If the true branch is `False`, simplify to `(not node.test) and node.orelse`.
- If the false branch is `True`, simplify to `(not node.test) or node.body`.
- If the false branch is `False`, simplify to `node.test and node.orelse`.

## Script and Flag
[sol.py](Grey-Cat-The-Flag-2022/Finals/oneliner/sol.py) \
`grey{quite_big_ah}`
