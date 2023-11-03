from numpy import ndarray, array, vstack, insert, delete, sum as np_sum, ndindex


def m_create(row_cnt: int = None, col_cnt: int = None, *, data=None) -> ndarray:
    """
    Создать матрицу
    (row_cnt, col_cnt) | data
    """
    assert bool(row_cnt and col_cnt) ^ bool(data), 'set matrix Dimension or Data'
    if data:
        return array(data)
    else:
        assert row_cnt and col_cnt, 'row_cnt and col_cnt params expected'
        matrix = ndarray(shape=(row_cnt, col_cnt), dtype=int)
        matrix.fill(0)
        return matrix


def m_intersects(matrix1: ndarray, matrix2: ndarray) -> bool:
    """Пересекаются ли матрицы"""
    return any((i > 1 for i in (matrix1 + matrix2).flatten()))


def m_expand(matrix: ndarray, top=0, bottom=0, left=0, right=0, _filler=0) -> ndarray:
    """Добавить строки и колонки по краям матрицы"""
    assert top >= 0 and bottom >= 0 and left >= 0 and right >= 0
    new_matrix = matrix.copy()
    # rows
    col_cnt = new_matrix.shape[1]
    for i in range(top):
        new_matrix = vstack((tuple(_filler for _ in range(col_cnt)), new_matrix))
    for i in range(bottom):
        new_matrix = vstack((new_matrix, tuple(_filler for _ in range(col_cnt))))
    # cols
    for i in range(left):
        new_matrix = insert(new_matrix, 0, _filler, axis=1)
    col_cnt = new_matrix.shape[1]
    for i in range(right):
        new_matrix = insert(new_matrix, col_cnt, _filler, axis=1)
    return new_matrix


def m_trim(matrix: ndarray, top=0, bottom=0, left=0, right=0) -> ndarray:
    """Удалить строки и колонки по краям матрицы"""
    assert top >= 0 and bottom >= 0 and left >= 0 and right >= 0
    row_cnt, col_cnt = matrix.shape
    return matrix[top:row_cnt - bottom, left:col_cnt - right]


def m_is_sum_equals(matrix1: ndarray, matrix2: ndarray) -> bool:
    """Равны ли суммы элементов матриц"""
    assert matrix1.shape == matrix2.shape, 'Different matrix shapes'
    return np_sum(matrix1) == np_sum(matrix2)


def m_del_rows(matrix: ndarray, rows: tuple or list):
    """Удалить из матрицы строки с указанными индексами"""
    return delete(matrix, rows, axis=0)


def m_indexes(matrix: ndarray) -> iter:
    """
    Итератор элементов матрицы
    Matrix index iterator (An N-dimensional iterator object to index arrays - internal shortcut)
    example:
        for row, col in m_indexes(matrix):
    """
    return ndindex(matrix.shape)  # noqa


def m_2d_move_in_place(matrix: ndarray, row_num: int, col_num: int, x: int = 0, y: int = 0, filler: int = 0) -> None:
    """
    *МЕДЛЕННЫЙ вариант
    Сдвинуть данные заданной матрицы в двухмерной плоскости
    """
    # вправо
    if x > 0:
        for row in range(row_num):
            for col in range(col_num - 1, -1, -1):
                col_src = col - x
                matrix[row, col] = matrix[row, col_src] if col_src >= 0 else filler
    # влево
    if x < 0:
        for row in range(row_num):
            for col in range(col_num):
                col_src = col + abs(x)
                matrix[row, col] = matrix[row, col_src] if col_src < col_num else filler
    # вверх
    if y > 0:
        for col in range(col_num):
            for row in range(row_num):
                row_src = row + y
                matrix[row, col] = matrix[row_src, col] if row_src < row_num else filler
    # вниз
    if y < 0:
        for col in range(col_num):
            for row in range(row_num - 1, -1, -1):
                row_src = row - abs(y)
                matrix[row, col] = matrix[row_src, col] if row_src >= 0 else filler


def m_2d_move(matrix: ndarray, x: int = 0, y: int = 0) -> ndarray:
    """Создать новую матрицу, сдвинутую в двухмерной плоскости"""
    assert x or y
    if x > 0:
        # вправо
        matrix = m_expand(m_trim(matrix, right=x), left=x)
    else:
        # влево
        matrix = m_expand(m_trim(matrix, left=abs(x)), right=abs(x))
    if y > 0:
        # вверх
        matrix = m_expand(m_trim(matrix, top=y), bottom=y)
    else:
        # вниз
        matrix = m_expand(m_trim(matrix, bottom=abs(y)), top=abs(y))
    return matrix
