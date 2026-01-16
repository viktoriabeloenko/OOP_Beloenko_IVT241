from typing import List, Union

Number = Union[int, float]


class Matrix:
    """Матричный класс (ООП стиль)"""

    def __init__(self, data: List[List[Number]]):
        self.data = data
        self.rows = len(data)
        self.cols = len(data[0])

    # ===== СЛОЖЕНИЕ МАТРИЦ =====
    def __add__(self, other: "Matrix") -> "Matrix":
        if self.rows != other.rows or self.cols != other.cols:
            raise ValueError("ОШИБКА: размеры матриц не совпадают")

        result = []
        for i in range(self.rows):
            row = []
            for j in range(self.cols):
                row.append(self.data[i][j] + other.data[i][j])
            result.append(row)
        return Matrix(result)

    # ===== УМНОЖЕНИЕ (МАТРИЦА ИЛИ СКАЛЯР) =====
    def __mul__(self, other: Union["Matrix", Number]) -> "Matrix":
        # Умножение на число
        if isinstance(other, (int, float)):
            result = []
            for i in range(self.rows):
                row = []
                for j in range(self.cols):
                    row.append(self.data[i][j] * other)
                result.append(row)
            return Matrix(result)

        # Умножение на матрицу
        if self.cols != other.rows:
            raise ValueError("ОШИБКА: нельзя умножить матрицы с такими размерами")

        result = []
        for i in range(self.rows):
            row = []
            for j in range(other.cols):
                sum_val = 0
                for k in range(self.cols):
                    sum_val += self.data[i][k] * other.data[k][j]
                row.append(sum_val)
            result.append(row)
        return Matrix(result)

    # ===== ТРАНСПОНИРОВАНИЕ =====
    def transpose(self) -> "Matrix":
        result = []
        for j in range(self.cols):
            row = []
            for i in range(self.rows):
                row.append(self.data[i][j])
            result.append(row)
        return Matrix(result)

    # ===== ВЫВОД =====
    def __str__(self) -> str:
        lines = []
        for row in self.data:
            line = " ".join(f"{x:6}" for x in row)
            lines.append(line)
        return "\n".join(lines)
