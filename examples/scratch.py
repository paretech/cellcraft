import cellcraft as cc

p1 = cc.CellPattern("-|;|-")
p2 = cc.CellPattern("XO;OX")

canvas = cc.LogicalCanvas(width=6, height=6, fill=".").place(p1, 0, 0).place(p2, -2, -2)
