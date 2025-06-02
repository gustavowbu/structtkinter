import structtkinter as stk

stk.STk([
    stk.Link(rel="stylesheet", href="examples/example1/stk/style.py", stk=stk),
    stk.Div(classes=["blueball"]),
    stk.Div(classes=["frame"], children=[
        stk.Div(classes=["item"]),
        stk.Div(classes=["item"]),
        stk.Div(classes=["item"])
    ]),
    stk.Script("examples/example1/stk/script.py", stk)
])
