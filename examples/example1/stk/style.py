import structtkinter as stk

def style(stk: stk):

    stk.Style(".blueball",
        background_color="blue",
        border_radius=10,
        width=20,
        height=20,
    )

    stk.Style(".frame",
        background_color="gray",
        border_radius=10,
        width="fit-content",
    )

    stk.Style(".item",
        background_color="yellow",
        border_radius=20,
        width=50,
        height=50,
    )