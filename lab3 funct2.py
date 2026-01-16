"""
ФУНКЦИОНАЛЬНЫЙ подход БЕЗ инкапсуляции.
"""

import json
import datetime as dt
import uuid
from typing import Dict, List, Tuple, Any


# ---------- Функции создания и изменения данных ----------

def create_person(name: str, born_in: dt.datetime) -> Dict[str, Any]:
    """
    Создаёт структуру данных, описывающую человека.
    Это не объект, а обычный словарь.
    """
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "born_in": born_in,
        "friends": []  # храним индексы друзей
    }


def add_friend(
        persons: List[Dict[str, Any]],
        index1: int,
        index2: int
) -> None:
    """
    Добавляет взаимную дружбу между двумя людьми
    по их индексам в списке.
    """
    if index2 not in persons[index1]["friends"]:
        persons[index1]["friends"].append(index2)

    if index1 not in persons[index2]["friends"]:
        persons[index2]["friends"].append(index1)


# ---------- Сериализация ----------

def encode_functional(
        persons: List[Dict[str, Any]],
        root_index: int
) -> bytes:
    """
    Кодирует список людей в JSON.
    Все ссылки преобразуются в идентификаторы.
    """
    serializable_persons = []

    for person in persons:
        serializable_persons.append({
            "id": person["id"],
            "name": person["name"],
            "born_in": person["born_in"].isoformat(),
            "friends": [persons[i]["id"] for i in person["friends"]]
        })

    result = {
        "root_id": persons[root_index]["id"],
        "persons": serializable_persons
    }

    return json.dumps(result, indent=2).encode("utf-8")


# ---------- Десериализация ----------

def decode_functional(data: bytes) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Восстанавливает структуры данных из JSON.
    Возвращает список всех людей и корневого человека.
    """
    parsed = json.loads(data.decode("utf-8"))
    persons: List[Dict[str, Any]] = []
    id_to_index: Dict[str, int] = {}

    # Фаза 1: создание людей
    for item in parsed["persons"]:
        person = {
            "id": item["id"],
            "name": item["name"],
            "born_in": dt.datetime.fromisoformat(item["born_in"]),
            "friends": []
        }
        id_to_index[person["id"]] = len(persons)
        persons.append(person)

    # Фаза 2: восстановление связей
    for i, item in enumerate(parsed["persons"]):
        persons[i]["friends"] = [
            id_to_index[fid] for fid in item["friends"]
        ]

    root_person = persons[id_to_index[parsed["root_id"]]]
    return persons, root_person


# ---------- Вспомогательная функция ----------

def find_by_name(persons: List[Dict[str, Any]], name: str) -> Dict[str, Any]:
    """Поиск человека по имени"""
    return next(p for p in persons if p["name"] == name)


# ================== Пример использования ==================

if name == "__main__":
    print("=== Функциональный подход без инкапсуляции ===")

    persons = [
        create_person("Ivan", dt.datetime(2020, 4, 12)),
        create_person("Petr", dt.datetime(2021, 9, 27)),
        create_person("Anna", dt.datetime(2019, 3, 15))
    ]

    add_friend(persons, 0, 1)
    add_friend(persons, 1, 2)
    add_friend(persons, 2, 0)  # создаём цикл

    encoded = encode_functional(persons, 0)
    print("Закодированные данные:")
    print(encoded.decode("utf-8"))

    decoded_persons, root = decode_functional(encoded)

    print("\nПроверка восстановления:")
    print(f"Корневой: {root['name']}")
    print(f"Друзей у корневого: {len(root['friends'])}")

    anna = find_by_name(decoded_persons, "Anna")
    print(
        f"У Анны друзей: {len(anna['friends'])}, "
        f"первый друг: {decoded_persons[anna['friends'][0]]['name']}"
    )
  
