import structtkinter as stk

stk.STk([
    stk.StyleSheet("examples/example1/stk/style.py", stk),
    stk.Div(classes=["blueball"]),
    stk.Div(classes=["frame"], children=[
        stk.Div(classes=["item"]),
        stk.Div(classes=["item"]),
        stk.Div(classes=["item"])
    ]),
    stk.Script("examples/example1/stk/script.py", stk)
])