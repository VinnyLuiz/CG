INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

SCN_XMIN, SCN_XMAX = -1, 1
SCN_YMIN, SCN_YMAX = -1, 1

def compute_out_code_scn(x, y):
    code = INSIDE
    if x < SCN_XMIN: code |= LEFT
    elif x > SCN_XMAX: code |= RIGHT
    if y < SCN_YMIN: code |= BOTTOM
    elif y > SCN_YMAX: code |= TOP
    return code

def cohen_sutherland_clip_scn(x0, y0, x1, y1):
    out_code0 = compute_out_code_scn(x0, y0)
    out_code1 = compute_out_code_scn(x1, y1)
    while True:
        if not (out_code0 | out_code1):
            return (x0, y0, x1, y1)
        elif out_code0 & out_code1:
            return None
        else:
            out_code_out = out_code0 if out_code0 else out_code1
            if out_code_out & TOP:
                x = x0 + (x1 - x0) * (SCN_YMAX - y0) / (y1 - y0)
                y = SCN_YMAX
            elif out_code_out & BOTTOM:
                x = x0 + (x1 - x0) * (SCN_YMIN - y0) / (y1 - y0)
                y = SCN_YMIN
            elif out_code_out & RIGHT:
                y = y0 + (y1 - y0) * (SCN_XMAX - x0) / (x1 - x0)
                x = SCN_XMAX
            elif out_code_out & LEFT:
                y = y0 + (y1 - y0) * (SCN_XMIN - x0) / (x1 - x0)
                x = SCN_XMIN
            if out_code_out == out_code0:
                x0, y0 = x, y
                out_code0 = compute_out_code_scn(x0, y0)
            else:
                x1, y1 = x, y
                out_code1 = compute_out_code_scn(x1, y1)

def liang_barsky_clip_scn(x0, y0, x1, y1):
    dx = x1 - x0
    dy = y1 - y0
    p = [-dx, dx, -dy, dy]
    q = [x0 - SCN_XMIN, SCN_XMAX - x0, y0 - SCN_YMIN, SCN_YMAX - y0]
    u1, u2 = 0.0, 1.0
    for i in range(4):
        if p[i] == 0:
            if q[i] < 0:
                return None
        else:
            u = q[i] / p[i]
            if p[i] < 0:
                if u > u1: u1 = u
            else:
                if u < u2: u2 = u
    if u1 > u2:
        return None
    return (x0 + u1 * dx, y0 + u1 * dy, x0 + u2 * dx, y0 + u2 * dy)

def clip_point_scn(x, y):
    return SCN_XMIN <= x <= SCN_XMAX and SCN_YMIN <= y <= SCN_YMAX

def sutherland_hodgman_scn(pontos):
    def clip_edge(pontos, edge_fn, intersect_fn):
        result = []
        prev = pontos[-1]
        for curr in pontos:
            if edge_fn(curr):
                if not edge_fn(prev):
                    result.append(intersect_fn(prev, curr))
                result.append(curr)
            elif edge_fn(prev):
                result.append(intersect_fn(prev, curr))
            prev = curr
        return result

    def left(p):   return p[0] >= SCN_XMIN
    def right(p):  return p[0] <= SCN_XMAX
    def bottom(p): return p[1] >= SCN_YMIN
    def top(p):    return p[1] <= SCN_YMAX

    def intersect_left(p1, p2):
        x, y = p1
        x2, y2 = p2
        xint = SCN_XMIN
        yint = y + (y2 - y) * (SCN_XMIN - x) / (x2 - x)
        return (xint, yint)

    def intersect_right(p1, p2):
        x, y = p1
        x2, y2 = p2
        xint = SCN_XMAX
        yint = y + (y2 - y) * (SCN_XMAX - x) / (x2 - x)
        return (xint, yint)

    def intersect_bottom(p1, p2):
        x, y = p1
        x2, y2 = p2
        yint = SCN_YMIN
        xint = x + (x2 - x) * (SCN_YMIN - y) / (y2 - y)
        return (xint, yint)

    def intersect_top(p1, p2):
        x, y = p1
        x2, y2 = p2
        yint = SCN_YMAX
        xint = x + (x2 - x) * (SCN_YMAX - y) / (y2 - y)
        return (xint, yint)

    for edge_fn, intersect_fn in [
        (left, intersect_left), (right, intersect_right),
        (bottom, intersect_bottom), (top, intersect_top)
    ]:
        pontos = clip_edge(pontos, edge_fn, intersect_fn)
        if not pontos: break
    return pontos