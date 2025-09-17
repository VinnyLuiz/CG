from tranformacoes import Window
# Region Codes
CENTER, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8
# Bordas da Window
XMIN, XMAX, YMIN, YMAX = -1.0, 1.0, -1.0, 1.0

def clip_ponto(x_scn, y_scn):
    return XMIN <= x_scn <= XMAX and YMIN <= y_scn <= YMAX

def clip_reta_CS(x0, y0, x1, y1):
    """Algoritmo de clipping de Coher-Sutherland"""
    def get_region_code(x, y):
        region_code = CENTER
        if x < XMIN:
            region_code |= LEFT
        elif x > XMAX:
            region_code |= RIGHT
        if y < YMIN:
            region_code |= BOTTOM
        elif y > YMAX:
            region_code |= TOP
        return region_code

    rc_0 = get_region_code(x0, y0)
    rc_1 = get_region_code(x1, y1)
    aceitar = False

    # Se os RCs forem 0 está no centro e pode desenhar
    while True:
        if rc_0 == 0 and rc_1 == 0:
            aceitar = True
            break
        # Caso nenhum RC está em 0 rejeita
        elif (rc_0 & rc_1) != 0:
            break
        # Caso um deles esteja dentro
        else:
            rc_modificar = rc_0 if rc_0 != 0 else rc_1
            if rc_modificar & TOP:
                if (y1 - y0) == 0:
                    break
                x = x0 + (x1 - x0) * (YMAX - y0) / (y1 - y0)
                y = YMAX
            elif rc_modificar & BOTTOM:
                if (y1 - y0) == 0:
                    break
                x = x0 + (x1 - x0) * (YMIN - y0) / (y1 - y0)
                y = YMIN
            elif rc_modificar & RIGHT:
                if (x1 - x0) == 0:
                    break
                y = y0 + (y1 - y0) * (XMAX - x0) / (x1 - x0)
                x = XMAX
            elif rc_modificar & LEFT:
                if (x1 - x0) == 0:
                    break
                y = y0 + (y1 - y0) * (XMIN - x0) / (x1 - x0)
                x = XMIN
            if rc_modificar == rc_0:
                x0, y0 = x, y
                rc_0 = get_region_code(x0, y0)
            else:
                x1, y1 = x, y
                rc_1 = get_region_code(x1, y1)
    if aceitar:
        return x0, y0, x1, y1
    return None

def clip_reta_NLN(x0, y0, x1, y1):
    """Clipping de retas utilizando Nicholl-Lee-Nicholl"""
    # Reutilizando o clip_ponto pra checar se está dentro da window
    if clip_ponto(x0, y0) and clip_ponto(x1, y1):
        return(x0, y0, x1, y1)

    def intersect(x0, y0, x1, y1, borda):
        if borda == "LEFT":
            if x1 == x0: return None
            t = (XMIN - x0) / (x1 - x0)
            return XMIN, y0 + t * (y1 - y0)
        elif borda == "RIGHT":
            if x1 == x0: return None
            t = (XMAX - x0) / (x1 - x0)
            return XMAX, y0 + t * (y1 - y0)
        elif borda == "BOTTOM":
            if y1 == y0: return None
            t = (YMIN - y0) / (y1 - y0)
            return x0 + t * (x1 - x0), YMIN
        elif borda == "TOP":
            if y1 == y0: return None
            t = (YMAX - y0) / (y1 - y0)
            return x0 + t * (x1 - x0), YMAX

    p0 = 0
    if x0 < XMIN: p0 |= 1  # LEFT
    elif x0 > XMAX: p0 |= 2  # RIGHT
    if y0 < YMIN: p0 |= 4  # BOTTOM
    elif y0 > YMAX: p0 |= 8  # TOP

    p1 = 0
    if x1 < XMIN: p1 |= 1
    elif x1 > XMAX: p1 |= 2
    if y1 < YMIN: p1 |= 4
    elif y1 > YMAX: p1 |= 8

    # Rejeita se p0 e p1 estão fora
    if (p0 & p1) != 0:
        return None

    pontos = [(x0, y0), (x1, y1)]
    for i in range(2):
        x, y = pontos[i]
        if not clip_ponto(x, y):
            if x < XMIN: inter = intersect(x0, y0, x1, y1, "LEFT")
            elif x > XMAX: inter = intersect(x0, y0, x1, y1, "RIGHT")
            elif y < YMIN: inter = intersect(x0, y0, x1, y1, "BOTTOM")
            elif y > YMAX: inter = intersect(x0, y0, x1, y1, "TOP")
            else: inter = None
            if inter is None:
                return None
            pontos[i] = inter

    (x0clip, y0clip), (x1clip, y1clip) = pontos
    if clip_ponto(x0clip, y0clip) and clip_ponto(x1clip, y1clip):
        return (x0clip, y0clip, x1clip, y1clip)
    return None

def clip_poligono(lista_coordenadas_scn):
    """Clipping de polígonos Sutherland-Hodgman"""
    def esta_dentro(ponto, borda):
        x, y = ponto 
        if borda == "LEFT":
            return x >= XMIN
        elif borda == "RIGHT":
            return x <= XMAX
        elif borda == "BOTTOM":
            return y >= YMIN
        elif borda == "TOP":
            return y <= YMAX
        return False

    def calcular_intersec(p0, p1, borda):
        x0, y0 = p0
        x1, y1 = p1
        if borda == "LEFT":
            x = XMIN
            y = y0 + (y1 - y0) * (XMIN - x0) / (x1 - x0)
        elif borda == "RIGHT":
            x = XMAX
            y = y0 + (y1 - y0) * (XMAX - x0) / (x1 - x0)
        elif borda == "BOTTOM":
            y = YMIN
            x = x0 + (x1 - x0) * (YMIN - y0) / (y1 - y0)
        elif borda == "TOP":
            y = YMAX
            x = x0 + (x1 - x0) * (YMAX - y0) / (y1 - y0)
        return (x, y)

    bordas = ["LEFT", "RIGHT", "BOTTOM", "TOP"]
    lista_clippada = lista_coordenadas_scn

    for borda in bordas:
        lista_entrada = lista_clippada
        lista_clippada = []
        if not lista_entrada:
            break
        s = lista_entrada[-1]  # último vértice
        for p in lista_entrada:
            if esta_dentro(p, borda):
                if esta_dentro(s, borda):
                    # caso 1: ambos dentro
                    lista_clippada.append(p)
                else:
                    # caso 2: s fora, p dentro
                    inter = calcular_intersec(s, p, borda)
                    lista_clippada.append(inter)
                    lista_clippada.append(p)
            else:
                if esta_dentro(s, borda):
                    # caso 3: s dentro, p fora
                    inter = calcular_intersec(s, p, borda)
                    lista_clippada.append(inter)
                # caso 4: ambos fora → não adiciona nada
            s = p
    return lista_clippada