from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """Проверяем что запрос API ключа возвращает статус 200 и в результате содержится слово key."""

    status, result = pf.get_api_key(email, password)

    assert status == 200
    assert 'key' in result


def test_get_api_key_for_invalid_user_successful(email=invalid_email, password=invalid_password):
    """Проверяем негативный тест-кейс, что запрос API ключа с незарегистрированными на платформе данными пользователя
    (email, password) не возвращает статуса = 200, а ответ (результат) сервера не содержит ключа 'key'."""

    status, result = pf.get_api_key(email, password)

    assert status != 200
    assert 'key' not in result


def test_get_all_pets_with_valid_key(filter=''):
    """Проверяем что запрос всех питомцев возвращает не пустой список. Для этого сначала получаем api ключ и
    сохраняем в переменную auth_key. Далее используя этого ключ запрашиваем список всех питомцев и проверяем,
    что список не пустой. Доступное значение параметра filter - 'my_pets' либо ''"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Гарфилд', animal_type='американская-борзая',
                                     age='40', pet_photo='images/cat2.jpg'):
    """Проверяем, что можно создать карточку питомца с полными (включая фотографию), корректными данными."""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert result['name'] == name


def test_add_new_pet_with_invalid_data(name='', animal_type='', age='', pet_photo='images/cat2.jpg'):
    """Проверяем негативный тест-кейс в случае, когда запрос на добавление питомца содержит некорректные
    параметры (обязательные для заполнения пустые значения). Если система отказывает в запросе - негативный тест-кейс
    пройден. Если система все-таки добавляет карточку питомца с невалидными данными - вызываем исключение и создаем
    баг-репорт."""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    if status == 200 and 'name' in result:
        raise Exception(f'Обнаружена ошибка - возможность создания карточки питомца с пустыми полями.\n'
                        f'Занести баг в баг-трэкинговую систему и создать баг-репорт.')
    else:
        assert status != 200
        assert 'name' not in result


def test_my_pets_filter(filter='my_pets'):
    """ Проверяем работу запроса при переданном параметре фильтра - 'my_pets', который выводит список питомцев(a),
    добавленных(ого) пользователем. Для этого сначала получаем API ключ и сохраняем в переменную auth_key. Далее,
    используя этот ключ, запрашиваем список своих питомцев и проверяем, что список не пустой."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_update_pet_foto_jpg(pet_photo='images/cat2.jpg'):
    """Проверяем, что можно добавить фото питомца в ранее созданную карточку в валидном формате - xxx.jpg."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_foto(auth_key, my_pets['pets'][0]['id'], pet_photo)

        _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

        assert status == 200
        assert result['pet_photo'] == my_pets['pets'][0]['pet_photo']
    else:
        raise Exception("Добавленные вами питомцы в списке отсутствуют.")


def test_update_pet_foto_invalid_bmp(pet_photo='images/cat3.bmp'):
    """Проверяем негативный тест-кейс в случае, когда фото питомца передаётся в невалидном формате
    графического файла - xxx.bmp (в соответствии с требованиями API-документации PetFriends API v1). Если
    система отказывает в запросе - негативный тест-кейс пройден. Если система все-таки добавляет в карточку фото
    питомца с некорректным форматом файла - вызываем исключение и создаем баг-репорт."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    status, result = pf.update_pet_foto(auth_key, my_pets['pets'][0]['id'], pet_photo)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    if status == 200 and result['pet_photo'] == my_pets['pets'][0]['pet_photo']:
        raise Exception('Обнаружена ошибка - возможность добавления фото питомца в невалидном графическом формате '
                        'xxx.bmp.\n'
                        f'Занести баг в баг-трэкинговую систему и создать баг-репорт.')
    else:
        assert status != 200
        assert result['pet_photo'] != my_pets['pets'][0]['pet_photo']


def test_add_new_pet_simple(name='Том', animal_type='американская-борзая', age=4.3):
    """Проверяем возможность добавления базовых данных о питомце без фото."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    assert status == 200
    assert result['name'] == name


def test_add_new_pet_simple_invalid_age_data_type(name='Том', animal_type='американская-борзая', age='2'):
    """Проверяем негативный тест-кейс в случае, когда передаваемое значение переменной age в запросе имеет строковый
    (str) тип данных, тогда как в соответствии с требованиями API-документации PetFriends API v1 значение параметра age
    должно принимать тип данных числа(number). Если система отказывает в запросе - негативный тест-кейс
    пройден. Если система все-таки создает простую карточку питомца с неверным типом переданных данных - вызываем
    исключение и создаем баг-репорт."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    if status == 200 and result['name'] == name:
        raise Exception(f'Обнаружена ошибка - платформа PetFriends принимает параметр age в невалидном'
                        f' строковом (str) формате.\n'
                        f'Занести баг в баг-трэкинговую систему и создать баг-репорт.')
    else:
        assert status != 200
        assert result['name'] != name


def test_add_new_pet_simple_invalid_breed_data_type(name='Том', animal_type=123123123, age='100'):
    """Проверяем негативный тест-кейс в случае, когда передаваемое значение переменной animal_type в запросе имеет
    числовой (number) тип данных, тогда как в соответствии с требованиями API-документации PetFriends API v1 значение
    параметра animal_type должно принимать строчный тип данных (string). Если система отказывает в запросе -
    негативный тест-кейс пройден. Если система все-таки создает простую карточку питомца с неверным типом
    переданных данных - вызываем исключение и создаем баг-репорт."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    if status == 200 and result['name'] == name:
        raise Exception(f'Обнаружена ошибка - платформа PetFriends принимает параметр animal_type в невалидном'
                        f' числовом (number) типе данных.\n'
                        f'Занести баг в баг-трэкинговую систему и создать баг-репорт.')
    else:
        assert status != 200
        assert result['name'] != name

def test_add_new_pet_simple_invalid_age_value(name='Том', animal_type=123123123, age='999999999999999999999999'):
    """Проверяем негативный тест-кейс в случае, когда переменная age в запросе передает системе любое
     значение из цифр, что будет не соответствовать реальной продолжительности жизни любого животного на земле :).
    Если система отказывает в запросе - негативный тест-кейс пройден. Если система все-таки создает простую
    карточку питомца с неверным типом переданных данных - вызываем исключение и создаем баг-репорт."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)

    status, result = pf.create_pet_simple(auth_key, name, animal_type, age)

    if status == 200 and result['name'] == name:
        raise Exception(f'Обнаружена ошибка - платформа PetFriends принимает параметр animal_type в невалидном'
                        f' числовом (number) типе данных.\n'
                        f'Занести баг в баг-трэкинговую систему и создать баг-репорт.')
    else:
        assert status != 200
        assert result['name'] != name


def test_successful_delete_self_pet():
    """Проверяем позитивный тест-кейс на возможность удаления питомца из списка"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Леопольд", "советская-добрая", "40", "images/cat1.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Ninja-cat', animal_type='Japan-NES', age=33.6):
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
