import time
import pytest
from pytest import fixture


def duration_time_of_test(func):
    """Функция-декоратор для определения длительности авто-теста с момента запуска\до момента его окончания."""

    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"\n\nНачало выполнения теста: {time.asctime()}")

        func(*args, **kwargs)

        end_time = time.time()
        print(f"Окончание выполнения теста: {time.asctime()}")
        result = end_time - start_time
        print(f"Общая продолжительность выполнения теста: {round(result, 3)} сек.")
        return func(*args, **kwargs)

    return wrapper


def time_decorator(func):
    def wrapper(*args, **kwargs):
        print(f'\nТест начат:{time.asctime()}')
        func(*args, **kwargs)
        print(f'Тест окончен:{time.asctime()}\n')
        return func(*args, **kwargs)

    return wrapper
