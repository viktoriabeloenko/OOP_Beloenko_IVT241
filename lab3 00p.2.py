"""
ООП-подход БЕЗ соблюдения инкапсуляции.
"""

import json
import datetime as dt
import uuid
from typing import Dict, List, Any


class Person:
    def __init__(self, name: str, born_in: dt.datetime) -> None:
        self._name = name
        self._born_in = born_in
        self._friends: List['Person'] = []
        self._id = str(uuid.uuid4())

    def add_friend(self, friend: 'Person') -> None:
        """Добавляет друга (двусторонняя связь)"""
        if friend not in self._friends:
            self._friends.append(friend)
            friend._friends.append(self)


class DirectSerializer:
    """
    Сериализатор с прямым доступом к приватным полям Person.
    """

    @staticmethod
    def encode(person: Person) -> bytes:
        """
        Кодирует объект Person и все связанные с ним объекты в JSON.
        Обрабатывает циклические ссылки с помощью множества visited.
        """
        objects: List[Dict[str, Any]] = []
        visited_ids = set()

        def collect(p: Person) -> None:
            if p._id in visited_ids:
                return

            visited_ids.add(p._id)

            # Прямой доступ к приватным полям (нарушение инкапсуляции)
            data = {
                "id": p._id,
                "name": p._name,
                "born_in": p._born_in.isoformat(),
                "friends": [f._id for f in p._friends]
            }

            objects.append(data)

            # Рекурсивный обход графа друзей
            for friend in p._friends:
                collect(friend)

        collect(person)
        return json.dumps(objects, indent=2).encode("utf-8")

    @staticmethod
    def decode(data: bytes) -> Person:
        """
        Восстанавливает объекты Person из JSON.
        Используется создание объекта без вызова init.
        """
        raw_objects = json.loads(data.decode("utf-8"))
        cache: Dict[str, Person] = {}

        # Фаза 1: создание объектов без связей
        for obj in raw_objects:
            person = Person.__new__(Person)  # без init
            person._id = obj["id"]
            person._name = obj["name"]
            person._born_in = dt.datetime.fromisoformat(obj["born_in"])
            person._friends = []
            cache[person._id] = person

        # Фаза 2: восстановление связей
        for obj in raw_objects:
            person = cache[obj["id"]]
            person._friends = [cache[fid] for fid in obj["friends"]]

        # Возвращаем корневой объект
        return cache[raw_objects[0]["id"]]


# ================== Пример использования ==================

if name == "__main__":
    print("=== ООП без инкапсуляции ===")

    p1 = Person("Ivan", dt.datetime(2020, 4, 12))
    p2 = Person("Petr", dt.datetime(2021, 9, 27))
    p3 = Person("Anna", dt.datetime(2019, 3, 15))

    p1.add_friend(p2)
    p2.add_friend(p3)
    p3.add_friend(p1)  # создаём цикл

    encoded = DirectSerializer.encode(p1)
    print("Закодированные данные:")
    print(encoded.decode("utf-8"))

    restored = DirectSerializer.decode(encoded)

    # Проверка восстановления
    print("\nПроверка восстановленного объекта:")
    print(f"Имя: {restored._name}")
    print(f"Количество друзей: {len(restored._friends)}")
    print(
        f"Имя друга друга: {restored._friends[0]._friends[0]._name}"
    )
