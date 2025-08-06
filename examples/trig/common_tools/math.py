from math import cos, exp, sin


def polar2cart(r: float, phi: float) -> (float, float):
    """
    Преобразовать полярные координаты в декартовы
    r - Радиальная координата
    phi - Угловая координата
    вернет (x, y)
    размер итоговой Декартовой плоскости = r*2
    """
    return r * cos(phi), r * sin(phi)


def normal_distribution(data: list, mu: float, sigma: float):
    """
    Нормализованное распределение Гаусса
    :param data: Входные данные (список)
    :param mu: Среднее значение распределения
    :param sigma: Стандартное отклонение
    :return: Нормализованный список данных

    Чем меньше значение sigma, тем сильнее сгруппированы данные вокруг среднего.
    Чем больше sigma, тем шире разброс значений и меньшие отличия между соседними элементами.
    """
    if sigma <= 0:
        raise ValueError("sigma must be > 0")
    result = []
    total_weight = sum(exp(-((x - mu) ** 2) / (2 * sigma ** 2)) for x in data)
    if total_weight == 0:
        return [1.0 / len(data)] * len(data)  # Равномерное распределение
    for x in data:
        weight = exp(-((x - mu) ** 2) / (2 * sigma ** 2)) / total_weight
        result.append(weight)
    return result
