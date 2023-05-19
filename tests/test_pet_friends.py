from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос API ключа возвращает статус 200 и в результате содержится слово key"""

    status, result = pf.get_api_key(email, password)

    assert status == 200
    assert 'key' in result


def test_get_api_key_for_invalid_user_successful(email=invalid_email, password=invalid_password):
    """ Проверяем негативный тест-кейс, что запрос API ключа с незарегистрированными на платформе данными пользователя
    (email, password) не возвращает статуса = 200, а ответ (результат) сервера не содержит ключа 'key'."""

    status, result = pf.get_api_key(email, password)

    assert status != 200
    assert 'key' not in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем, что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Чубайс', animal_type='древняя', age='99', pet_photo='images/cat2.jpg'):
    """Проверяем, что можно создать карточку питомца с полными, включая фотографию, корректными данными."""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert result['name'] == name


def test_add_new_pet_with_invalid_data_successful(name='', animal_type='', age='', pet_photo='images/cat2.jpg'):
    """Проверяем успешность негативного тест-кейса в случае, если запрос на добавление питомца содержит некорректные
    параметры (обязательные для заполнения пустые значения). Если система отказывает в запросе - негативный тест-кейс
    пройден. Если система все-таки добавляет карточку питомца с невалидными данными - вызываем исключение и создаем
    баг-репорт."""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    if status != 200 and 'name' not in result:
        assert status != 200
        assert 'name' not in result
    else:
        raise Exception(f'Обнаружена ошибка - возможность создания карточки питомца с пустыми полями.\n'
                        f'Занести баг в баг-трэкинговую систему и создать баг-репорт.')


def test_my_pets_filter(filter='my_pets'):
    """ Проверяем работу запроса при переданном параметре фильтра - 'my_pets', который выводит список питомцев(a),
    добавленных(ого) пользователем. Для этого сначала получаем API ключ и сохраняем в переменную auth_key. Далее,
    используя этот ключ, запрашиваем список своих питомцев и проверяем, что список не пустой."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_successful_update_pet_foto(pet_photo='images/cat1.jpg'):
    """Проверяем, что можно добавить фото в ранее созданную карточку питомца."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_foto(auth_key, my_pets['pets'][0]['id'], pet_photo)

        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

        assert status == 200
        assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']
    else:
        raise Exception("There is no my pets")


def test_successful_add_new_pet_without_foto(name='Том', animal_type='сиамский', age='4'):
    """Проверяем возможность добавления базовых данных о питомце без фото."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")
