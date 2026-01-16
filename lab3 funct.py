"""
ФУНКЦИОНАЛЬНЫЙ подход С СОБЛЮДЕНИЕМ инкапсуляции.
"""

import json
import datetime as dt
from typing import Any, Dict, List, Callable


# ---------- Функциональная сериализация ----------

def encode_functional(person: Any) -> bytes:
    """
    Кодирует объект в JSON, используя только публичные методы:
    get_id, get_name, get_birth_date, get_friends.
    """
    visited_ids = set()
    result: List[Dict[str, Any]] = []

    def collect(p: Any) -> None:
        pid = p.get_id()
        if pid in visited_ids:
            return

        visited_ids.add(pid)

        result.append({
            "id": pid,
            "name": p.get_name(),
            "born_in": p.get_birth_date().isoformat(),
            "friends": [f.get_id() for f in p.get_friends()]
        })

        # Рекурсивный обход связей
        for friend in p.get_friends():
            collect(friend)

    collect(person)
    return json.dumps(result, indent=2).encode("utf-8")


def decode_functional(
        data: bytes,
        factory: Callable[[str, dt.datetime], Any]
) -> Any:
    """
    Восстанавливает объекты из JSON.
    Используется фабричная функция, создающая объект Person.
    Связи восстанавливаются через публичный метод add_friend.
    """
    raw_data = json.loads(data.decode("utf-8"))
    cache: Dict[str, Any] = {}

    # Фаза 1: создание объектов без связей
    for item in raw_data:
        obj = factory(
            item["name"],
            dt.datetime.fromisoformat(item["born_in"])
        )
        cache[item["id"]] = obj

    # Фаза 2: восстановление связей
    for item in raw_data:
        person = cache[item["id"]]
        for friend_id in item["friends"]:
            person.add_friend(cache[friend_id])

    return cache[raw_data[0]["id"]]


# ---------- Вспомогательный класс для демонстрации ----------

class FunctionalPerson:
    """
    Упрощённый класс Person для демонстрации
    функционального подхода.
    """

    def __init__(self, name: str, born_in: dt.datetime):
        self._id = f"person_{hash((name, born_in))}"
        self._name = name
        self._born_in = born_in
        self._friends: List['FunctionalPerson'] = []

    def add_friend(self, friend: 'FunctionalPerson') -> None:
        if friend not in self._friends:
            self._friends.append(friend)
            friend._friends.append(self)

    def get_id(self) -> str:
        return self._id

    def get_name(self) -> str:
        return self._name

    def get_birth_date(self) -> dt.datetime:
        return self._born_in

    def get_friends(self) -> List['FunctionalPerson']:
        return self._friends.copy()


# ================== Пример использования ==================

if name == "__main__":
    print("=== Функциональный подход с инкапсуляцией ===")

    p1 = FunctionalPerson("Ivan", dt.datetime(2020, 4, 12))
    p2 = FunctionalPerson("Petr", dt.datetime(2021, 9, 27))
    p3 = FunctionalPerson("Anna", dt.datetime(2019, 3, 15))

    p1.add_friend(p2)
    p2.add_friend(p3)
    p3.add_friend(p1)  # цикл

    encoded = encode_functional(p1)
    print("Закодированные данные:")
    print(encoded.decode("utf-8"))

    def factory(name: str, born: dt.datetime) -> FunctionalPerson:
        return FunctionalPerson(name, born)

    restored = decode_functional(encoded, factory)

    print("\nПроверка восстановления:")
    print(f"Имя: {restored.get_name()}")
    print(f"Друзей: {len(restored.get_friends())}")
    print(f"Друг друга: {restored.get_friends()[0].get_friends()[0].get_name()}"
    )
