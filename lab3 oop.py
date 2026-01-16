"""
ООП-подход С СОБЛЮДЕНИЕМ инкапсуляции.
"""

import json
import datetime as dt
import uuid
from typing import Dict, List, Any, Optional


class Person:
    def __init__(self, name: str, born_in: dt.datetime) -> None:
        self._id = str(uuid.uuid4())
        self._name = name
        self._born_in = born_in
        self._friends: List['Person'] = []

    def add_friend(self, friend: 'Person') -> None:
        """Добавляет друга (двусторонняя связь)"""
        if friend not in self._friends:
            self._friends.append(friend)
            friend._friends.append(self)

    # ---------- Публичные геттеры ----------

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_birth_date(self) -> dt.datetime:
        return self._born_in

    def get_friends(self) -> List['Person']:
        # Возвращаем копию, чтобы защитить внутреннее состояние
        return self._friends.copy()

    # ---------- Методы сериализации ----------

    def to_serializable(self) -> Dict[str, Any]:
        """
        Преобразует объект Person в словарь,
        используя только публичные методы.
        """
        return {
            "id": self.get_id(),
            "name": self.get_name(),
            "born_in": self.get_birth_date().isoformat(),
            "friends": [friend.get_id() for friend in self.get_friends()]
        }

    @classmethod
    def from_serializable(cls, data: Dict[str, Any]) -> 'Person':
        """
        Создаёт объект Person из словаря.
        init не используется, так как данные уже есть.
        """
        obj = cls.__new__(cls)
        obj._id = data["id"]
        obj._name = data["name"]
        obj._born_in = dt.datetime.fromisoformat(data["born_in"])
        obj._friends = []
        return obj


class PersonSerializer:
    """
    Отдельный класс для сериализации Person.
    Использует публичный интерфейс класса.
    """

    @staticmethod
    def encode(person: Person) -> bytes:
        """
        Кодирует объект Person в JSON.
        Корректно обрабатывает циклические ссылки.
        """
        visited_ids = set()
        serialized_objects: List[Dict[str, Any]] = []

        def collect(p: Person) -> None:
            if p.get_id() in visited_ids:
                return

            visited_ids.add(p.get_id())
            serialized_objects.append(p.to_serializable())

            # Рекурсивно обходим друзей
            for friend in p.get_friends():
                collect(friend)

        collect(person)
        return json.dumps(serialized_objects, indent=2).encode("utf-8")

    @staticmethod
    def decode(data: bytes) -> Person:
        """
        Декодирует JSON обратно в объекты Person.
        Используется двухфазное восстановление:
        1. Создание объектов
        2. Восстановление связей
        """
        raw_data = json.loads(data.decode("utf-8"))
        cache: Dict[str, Person] = {}

        # Фаза 1: создание всех объектов
        for item in raw_data:
            person = Person.from_serializable(item)
            cache[person.get_id()] = person

        # Фаза 2: восстановление связей
        for item in raw_data:
            person = cache[item["id"]]
            for friend_id in item["friends"]:
                person._friends.append(cache[friend_id])

        # Возвращаем корневой объект
        return cache[raw_data[0]["id"]]
        # ================== Пример использования ==================

if name == "__main__":
    print("=== ООП с инкапсуляцией ===")

    p1 = Person("Ivan", dt.datetime(2020, 4, 12))
    p2 = Person("Petr", dt.datetime(2021, 9, 27))
    p3 = Person("Anna", dt.datetime(2019, 3, 15))

    p1.add_friend(p2)
    p2.add_friend(p3)
    p3.add_friend(p1)  # цикл

    encoded = PersonSerializer.encode(p1)
    print("Закодированные данные:")
    print(encoded.decode("utf-8"))

    restored = PersonSerializer.decode(encoded)

    print("\nПроверка восстановления:")
    print(f"Имя: {restored.get_name()}")
    print(f"Друзей: {len(restored.get_friends())}")
    print(
        f"Друг друга: {restored.get_friends()[0].get_friends()[0].get_name()}"
    )
