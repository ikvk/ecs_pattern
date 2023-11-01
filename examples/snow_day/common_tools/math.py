from math import cos, sin


def polar2cart(r: float, phi: float) -> (float, float):
    """
    Преобразовать полярные координаты в декартовы
    r - Радиальная координата
    phi - Угловая координата
    вернет (x, y)
    размер итоговой Декартовой плоскости = r*2
    """
    return r * cos(phi), r * sin(phi)
