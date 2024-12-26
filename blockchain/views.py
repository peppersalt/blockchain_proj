# blockchain/views.py
from django.shortcuts import render
from users.models import UserProfile

from django.shortcuts import render
from .blockchain import BlockChain

import json
from django.shortcuts import render
from .blockchain import BlockChain
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator

def init_blockchain(username, password):
    return BlockChain(username=username, password=password, base_url='https://b1.ahmetshin.com/restapi/')

def home_view(request):
    user_profile = UserProfile.objects.get(id=request.user.id)
    return render(request, 'home.html', {'user': user_profile})

from django.shortcuts import render
from users.models import UserBlock, BlockActiveDataJson, UserProfile

from django.db.models import Q
from django.shortcuts import render
from users.models import UserProfile, UserBlock, BlockActiveDataJson
def messages_view(request):
    user_profile = UserProfile.objects.get(id=request.user.id)
    wallet_credentials = user_profile.wallet_credentials or []
    wallet_hashes = user_profile.wallet_hashes

    # Получение данных с блокчейна
    bc = init_blockchain('', '')
    result = bc.get_chains().json()
    block_active = result.get("chains", {}).get("block_active", [])

    # Фильтрация блоков
    filtered_messages = []
    for block in block_active:
        try:
            for block_data in block.get('data_json', []):
                data = block_data.get('data_json', {})
                if set(wallet_hashes).intersection({
                    data.get('to_hach', ''),
                    data.get('from_hach', ''),
                    data.get('prev_hash', ''),
                }):
                    filtered_messages.append(block)
                    break
        except (TypeError, KeyError):
            continue

    sorted_messages = sorted(filtered_messages, key=lambda x: x['id'], reverse=True)
    # Формируем вкладки кошельков в порядке `wallet_credentials`
    wallet_tabs = {}
    for index, wallet in enumerate(wallet_credentials, start=1):
        wallet_hash = wallet_hashes[index - 1]  # Сопоставление хэшей
        incoming_messages = []
        outgoing_messages = []
        blocks = []
        for block in sorted_messages:
            for data in block.get('data_json', []):
                data_json = data.get('data_json', {})
                if data_json.get('from_hach') == wallet_hash:
                    outgoing_messages.append(data_json)
                    blocks.append(block)
                if data_json.get('to_hach') == wallet_hash:
                    incoming_messages.append(data_json)
                    blocks.append(block)

    
        wallet_tabs[index] = {
            'wallet_hash': wallet_hash,
            'wallet_name': f"Кошелек №{index}",
            'incoming_messages': incoming_messages,
            'outgoing_messages': outgoing_messages,
            'active_tab': 'messages',
            'blocks':blocks
        }

    return render(request, 'messages.html', {

        'wallet_tabs': wallet_tabs,
    })

def tasks_view(request):
    return render(request, 'tasks.html', {'active_tab': 'tasks'})

def all_blocks_view(request):
    bc = init_blockchain('','')
    result = bc.get_chains().json()

    # Получаем список всех блоков
    block_active = result.get("chains", {}).get("block_active", [])

    # Сортируем блоки по id в порядке убывания (последние блоки будут сверху)
    sorted_blocks = sorted(block_active, key=lambda x: x['id'], reverse=True)

    # Настройки пагинации
    paginator = Paginator(sorted_blocks, 5)  # 5 блоков на странице

    # Получаем номер текущей страницы из GET-запроса
    page_number = request.GET.get('page')
    latest_blocks = paginator.get_page(page_number)

    # Передаем данные в шаблон operations.html
    return render(request, 'all_blocks.html', {'active_tab': 'blocks', 'latest_blocks': latest_blocks})


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def decrypt_message_view(request):
    bc = init_blockchain('', '')
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            private_key = data.get('private_key')
            encrypted_object = data.get('encrypted_object')

            if not private_key or not encrypted_object:
                return JsonResponse({'success': False, 'error': 'Отсутствуют данные для расшифровки.'}, status=400)

            # Логика расшифровки
            result = bc.decrypt({
                'private_key': private_key,
                'encrypted_object': encrypted_object,
            })

            return JsonResponse({'success': True, 'result': result.json()})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Недопустимый метод.'}, status=405)

from django.http import JsonResponse
from .blockchain import BlockChain
def encrypt_message_view(request):
    if request.method == 'POST':
        try:
            text  = request.POST.get("message")  # Ключ шифрования (если есть)
            encryption_key = request.POST.get("encryption_key")  # Ключ шифрования (если есть)
            if not encryption_key or not text:
                return JsonResponse({'success': False, 'error': 'Неполные данные'})

            blockchain_client = BlockChain(username='your_username', password='your_password', base_url='https://b1.ahmetshin.com/restapi/')
            result = blockchain_client.encrypt({'private_key': encryption_key, 'text': text}).json()
            return result
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})

from django.shortcuts import render, redirect
from .blockchain import BlockChain
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib import messages
from .blockchain import BlockChain
from .forms import WalletForm
def dashboard_view(request):
    user_profile = request.user  # Текущий пользователь
    wallet_credentials = user_profile.wallet_credentials or []  # Получаем список логинов и паролей
    wallet_hashes = user_profile.wallet_hashes
    selected_wallet = None  # По умолчанию кошелек не выбран

    if request.method == 'POST':
        form = WalletForm(request.POST)
        if form.is_valid():
            if len(wallet_credentials) >= 5:
                messages.error(request, "Вы не можете добавить больше 5 кошельков.")
            else:
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']

                # Инициализация блокчейн клиента и получение данных
                blockchain_client = init_blockchain(username, password)
                try:
                    # Получаем данные о кошельке
                    wallet_data = blockchain_client.get_version_file()
                    user_hash = wallet_data.get('user_hash')
                    if not user_hash:
                        messages.error(request, "Не удалось получить user_hash кошелька.")
                        return redirect('dashboard')

                    
                    # Добавляем логин и пароль в список
                    wallet_credentials.append({
                        'username': username,
                        'password': password
                    })
                    
                    user_profile.wallet_hashes.append(user_hash)
                    user_profile.wallet_credentials = wallet_credentials
                    user_profile.wallet_hashes = wallet_hashes  # Обновляем поле wallet_hashes
                    user_profile.save()

                    messages.success(request, "Кошелек успешно добавлен!")
                except Exception as e:
                    messages.error(request, f"Произошла ошибка при добавлении кошелька: {str(e)}")

                return redirect('dashboard')  # Перезагружаем страницу
    else:
        form = WalletForm()

    # Проверяем, выбран ли кошелек через GET-параметр
    selected_wallet_id = request.GET.get('wallet_id')
    if selected_wallet_id:
        try:
            wallet_index = int(selected_wallet_id) - 1  # Индексация начинается с 0
            wallet = wallet_credentials[wallet_index]  # Получаем данные по индексу
            blockchain_client = init_blockchain(wallet['username'], wallet['password'])
            wallet_balance = blockchain_client.check_coins().json().get('coins', 'Неизвестно')
            wallet_hash = blockchain_client.get_version_file().get('user_hash', 'Неизвестно')

            selected_wallet = {
                'id': selected_wallet_id,
                'name': f'Кошелек №{selected_wallet_id}',
                'balance': wallet_balance,
                'wallet_hash': wallet_hash
            }
        except (IndexError, ValueError, KeyError) as e:
            messages.error(request, f"Ошибка при загрузке данных выбранного кошелька: {str(e)}")

    # Составляем список кошельков для отображения
    wallets = []
    for i, wallet in enumerate(wallet_credentials, start=1):
        blockchain_client = init_blockchain(wallet['username'], wallet['password'])
        balance = blockchain_client.check_coins().json().get('coins', 'Неизвестно')
        
        wallets.append({
            'id': i,
            'name': f'Кошелек №{i}',
            'balance': balance,
            'wallet_username': wallet['username']  # Добавляем логин кошелька для отображения
        })

    # Сохраняем данные о кошельках в сессию
    request.session['wallets'] = wallets

    return render(request, 'dashboard.html', {
        'wallets': wallets,
        'selected_wallet': selected_wallet,  # Передаем выбранный кошелек
        'form': form,
        'active_tab': 'dashboard'
    })



from django.http import JsonResponse

from django import forms

class WalletForm(forms.Form):
    username = forms.CharField(max_length=255, label="Логин")
    password = forms.CharField(max_length=255, label="Пароль", widget=forms.PasswordInput)

from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def send_coins_view(request):
    if request.method == "POST":
        wallet_id = int(request.POST.get("wallet_id"))
        
        # Получаем соответствующие логин и пароль кошелька
        try:
            wallet = request.user.wallet_credentials[wallet_id - 1]  # wallet_id индексация с 1
            blockchain_client = init_blockchain(wallet['username'], wallet['password'])
        except IndexError:
            return HttpResponseBadRequest("Invalid wallet ID")

        from_wallet_hash = request.POST.get("from_wallet_hash")
        to_wallet_hash = request.POST.get("to_wallet_hash")
        coin_amount = int(request.POST.get("coin_amount"))

        data = {
            'type_task': 'send_coins',
            'from_hach': from_wallet_hash,
            'to_hach': to_wallet_hash,
            'count_coins': coin_amount
        }

        # Отправляем задачу в блокчейн клиент
        result = blockchain_client.send_task(data)
        response_data = result.json()

        # Возвращаем сообщение об успехе или ошибке в зависимости от результата
        if response_data.get("success"):
            return JsonResponse({"message": "Монеты успешно отправлены!"})
        else:
            return JsonResponse({"error": "Не удалось отправить монеты."})

    return HttpResponseBadRequest("Invalid request method")

def get_full_json(request):
    # Initialize blockchain and retrieve chain data
    bc = init_blockchain('0','0')
    result = bc.get_chains().json()

    # Get the list of all active blocks
    block_active = result.get("chains", {})

    # Return data as JSON
    return JsonResponse(block_active, safe=False)


# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .blockchain import BlockChain
from .forms import WalletForm
from django.contrib import messages
def add_wallet(request):
    if request.method == "POST":
        username = request.POST.get("wallet_username")
        password = request.POST.get("wallet_password")

        if not request.user.is_authenticated:
            messages.error(request, "Вы должны быть авторизованы для добавления кошелька.")
            return redirect("dashboard")

        user_profile = request.user
        if len(user_profile.wallet_credentials) >= 5:  # Проверяем, не больше ли 5 кошельков
            messages.error(request, "Вы не можете добавить больше 5 кошельков.")
            return redirect("dashboard")

        # Инициализация блокчейн клиента с логином и паролем
        blockchain_client = init_blockchain(username, password)

        try:
            # Получаем данные о кошельке (например, user_hash или другие данные)
            wallet_data = blockchain_client.get_version_file()
            user_hash = wallet_data.get('user_hash')

            if not user_hash:
                messages.error(request, "Не удалось получить user_hash кошелька.")
                return redirect("dashboard")

            # Проверяем, что такой кошелек ещё не добавлен
            for wallet in user_profile.wallet_credentials:
                if wallet['username'] == username:  # Если логин уже есть
                    messages.warning(request, "Этот кошелек уже привязан к вашему аккаунту.")
                    return redirect("dashboard")

            # Добавляем логин и пароль в список кошельков
            user_profile.wallet_credentials.append({
                'username': username,
                'password': password
            })
            wallet_data = blockchain_client.get_version_file()
            user_hash = wallet_data.get('user_hash')
            user_profile.wallet_hashes.append(user_hash)

            user_profile.save()

            messages.success(request, "Кошелек успешно добавлен!")

        except Exception as e:
            messages.error(request, f"Произошла ошибка при добавлении кошелька: {str(e)}")

        return redirect("dashboard")

    return redirect("dashboard")

import pprint
import json
import threading
import time
import datetime
from django.http import JsonResponse
from .blockchain import BlockChain

# Глобальная переменная для хранения вывода консоли
console_output = ""
script_thread = None
stop_thread = False

# Функция для работы с блокчейном
def blockchain_client(username, password):
    global console_output
    init = BlockChain(username=username, password=password, base_url='https://b1.ahmetshin.com/restapi/')
    init.get_version_file()
    while not stop_thread:
        print(f"Client {username} sleeping at {str(datetime.datetime.now())}")
        result = init.get_chains()
        result = init.get_task().json()
        print(f"Client {username} received tasks: {result}")
        
        # Используем pprintpp для красивого форматирования
        formatted_result = pprint.pformat(result, indent=4, width=80)
        console_output += f"Client {username} received tasks:\n{formatted_result}\n\n"

        if result['tasks']:
            for task in result['tasks']:
                task_id = task['id']
                data_json = task['data_json']
                hash = init.get_hash_object(json.dumps(data_json))
                result_hash = init.make_hash(hash)
                data = {
                    'type_task': 'BlockTaskUser_Solution',
                    'id': task_id,
                    'hash': result_hash
                }
                result = init.send_task(data)
                print(f"Client {username} sent solution: {result.json()}")

                # Форматируем вывод и добавляем его в глобальную переменную
                formatted_solution = pprint.pformat(result.json(), indent=4, width=80)
                console_output += f"Client {username} sent solution:\n{formatted_solution}\n\n"

                time.sleep(2)  # Задержка между запросами для имитации работы
# Представление для получения текущего вывода консоли
def get_console_output(request):
    return JsonResponse({"console_output": console_output})

# Представление для запуска скрипта
def start_script(request):
    global script_thread, stop_thread
    if script_thread is None or not script_thread.is_alive():
        stop_thread = False
        client_configs = [
            ('peppersalt3', 'zxc_warrior228'),
            ('peppersalt4', 'zxc_warrior228'),
            ('peppersalt2', 'zxc_warrior228'),
            ('peppersalt1', 'zxc_warrior228'),
            ('peppersalt!', 'zxc_warrior228')
        ]
        threads = []
        for username, password in client_configs:
            thread = threading.Thread(target=blockchain_client, args=(username, password))
            threads.append(thread)
            thread.start()
        script_thread = threading.Thread(target=lambda: [t.join() for t in threads])
        script_thread.start()
        return JsonResponse({'status': 'started'})
    return JsonResponse({'status': 'already running'})

# Представление для остановки скрипта
def stop_script(request):
    global stop_thread
    stop_thread = True
    if script_thread is not None and script_thread.is_alive():
        script_thread.join()  # Ожидаем завершения потока
    return JsonResponse({'status': 'stopped'})

# Страница с кнопками для запуска и остановки скрипта
def index(request):
    return render(request, 'tasks.html')

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def send_message_view(request):
    if request.method == "POST":
        
        wallet_id = int(request.POST.get("wallet_id"))  # ID выбранного кошелька
        to_wallet_hash = request.POST.get("to_wallet_hash")  # Получатель
        message_text = request.POST.get("message")  # Текст сообщения
        encryption_key = request.POST.get("encryption_key")  # Ключ шифрования (если есть)
        encryption_result = ""

        # Получение соответствующего кошелька
        try:
            wallet = request.user.wallet_credentials[wallet_id - 1]  # wallet_id начинается с 1
            blockchain_client = init_blockchain(wallet['username'], wallet['password'])
        except (IndexError, KeyError):
            return HttpResponseBadRequest("Invalid wallet ID")

        from_wallet_hash = blockchain_client.get_version_file().get('user_hash')
        if not from_wallet_hash:
            return HttpResponseBadRequest("Unable to fetch wallet hash.")

        if encryption_key:

            try:
                # Вызываем функцию шифрования
                encryption_result = encrypt_message_view(request)
            except Exception as e:
                return JsonResponse({'error': f"Ошибка при вызове шифрования: {str(e)}"})
        # Подготовка данных для отправки
        if (encryption_key):
            data = {
                'type_task': 'custom',
                'from_hach': from_wallet_hash,
                'to_hach': to_wallet_hash,
                'encrypted_object': encryption_result
        }
        else:
            data = {
                'type_task': 'custom',
                'from_hach': from_wallet_hash,
                'to_hach': to_wallet_hash,
                'message': message_text
            }
        print(data)
        # Отправка сообщения в блокчейн
        try:
            result = blockchain_client.send_task(data)
            response_data = result.json()
            if response_data.get("success"):
                return JsonResponse({"message": "Сообщение успешно отправлено!"})
            else:
                return JsonResponse({"error": "Не удалось отправить сообщение."})
        except Exception as e:
            return JsonResponse({"error": f"Ошибка при отправке сообщения: {str(e)}"})

    return HttpResponseBadRequest("Invalid request method")
from django.shortcuts import render
from django.db import connection
from django.core.paginator import Paginator
from django.db.models import Q
def people(request):
    # Получение пользователей из базы данных
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, username, last_login FROM users_userprofile")
        db_users = cursor.fetchall()  # Список всех пользователей из БД

    # Получение данных из блокчейна
    bc = init_blockchain('', '')
    result = bc.get_chains().json()
    users_block = result.get("chains", {}).get("users_block", [])

    # Обработка фильтрации
    sort_by = request.GET.get('sort', 'coins_desc')  # По умолчанию сортировка по убыванию коинов
    
    # Сортировка по монетам
    if sort_by == 'coins_asc':
        users_block = sorted(users_block, key=lambda x: x['coins'])
    elif sort_by == 'coins_desc':
        users_block = sorted(users_block, key=lambda x: x['coins'], reverse=True)
    # Сортировка по ID (предположительно больший ID = новее)
    elif sort_by == 'time_asc':
        users_block = sorted(users_block, key=lambda x: x['id'])  # Меньшие ID - старее
    elif sort_by == 'time_desc':
        users_block = sorted(users_block, key=lambda x: x['id'], reverse=True)  # Большие ID - новее

    # Пагинация для пользователей из блокчейна
    paginator_blockchain = Paginator(users_block, 10)  # 10 пользователей на странице
    page_number_blockchain = request.GET.get('blockchain_page')
    paginated_blockchain_users = paginator_blockchain.get_page(page_number_blockchain)

    # Расчет дополнительных данных
    blockchain_user_count = len(users_block)
    total_coins = sum(user.get('coins', 0) for user in users_block)
    top_users = sorted(users_block, key=lambda x: x['coins'], reverse=True)[:5]

    # Получаем информацию о кошельках текущего пользователя
    user_profile = request.user
    wallet_credentials = user_profile.wallet_credentials or []  # Получаем список кошельков
    wallets_info = []

    # Словарь для хранения статистики по сообщениям
    wallet_stats = {
    wallet['username']: {
        'sent_messages': 0,
        'received_messages': 0,
        'sent_coins': 0,
        'received_coins': 0,
        'coin_sent_operations': 0,  # Инициализация ключа отправленных операций
        'coin_recieved_operations': 0  # Инициализация ключа полученных операций
    } for wallet in wallet_credentials
}

    # Данные для фильтрации и подсчета сообщений
    wallet_hashes = user_profile.wallet_hashes
    
    # Получение данных блоков для сообщений
    sorted_messages = []
    bc = init_blockchain('', '')
    result = bc.get_chains().json()
    block_active = result.get("chains", {}).get("block_active", [])

    # Фильтрация блоков
    filtered_messages = []
    for block in block_active:
        try:
            for block_data in block.get('data_json', []):
                data = block_data.get('data_json', {})
                if set(wallet_hashes).intersection({
                    data.get('to_hach', ''),
                    data.get('from_hach', ''),
                    data.get('prev_hash', ''),
                }):
                    filtered_messages.append(block)
                    break
        except (TypeError, KeyError):
            continue

    sorted_messages = sorted(filtered_messages, key=lambda x: x['id'], reverse=True)
    
    for block in sorted_messages:
        for block_data in block.get('data_json', []):
            data_json = block_data.get('data_json', {})
            
            # Обработка сообщений, независимо от того, связаны ли они с монетами
            for wallet in wallet_credentials:
                wallet_hash = wallet_hashes[wallet_credentials.index(wallet)]  # Сопоставление хэшей

                # Подсчет исходящих сообщений
                if data_json.get('from_hach') == wallet_hash:
                    wallet_stats[wallet['username']]['sent_messages'] += 1
                    # Если это транзакция с монетами, добавляем монеты
                    if data_json.get('count_coins', 0) != 0:
                        wallet_stats[wallet['username']]['sent_coins'] += data_json.get('count_coins', 0)
                        wallet_stats[wallet['username']]['coin_sent_operations'] += 1

                # Подсчет полученных сообщений
                if data_json.get('to_hach') == wallet_hash:
                    wallet_stats[wallet['username']]['received_messages'] += 1
                    # Если это транзакция с монетами, добавляем монеты
                    if data_json.get('count_coins', 0) != 0:
                        wallet_stats[wallet['username']]['received_coins'] += data_json.get('count_coins', 0)
                        wallet_stats[wallet['username']]['coin_recieved_operations'] += 1


        # Подсчет операций
    operation_stats = {
        'sent_messages': 0,
        'received_messages': 0,
        'sent_coins_operations': 0,  # Счетчик операций по передаче монет
        'received_coins_operations': 0,  # Счетчик операций по получению монет
        'sent_coins_total': 0,  # Суммарное количество отправленных монет
        'received_coins_total': 0,  # Суммарное количество полученных монет
        'coin_recieved_operations': 0,
        'coin_sent_operations':0
    }

    # Подсчет операций и монет
    for block in sorted_messages:
        for block_data in block.get('data_json', []):
            data_json = block_data.get('data_json', {})

            for wallet in wallet_credentials:
                wallet_hash = wallet_hashes[wallet_credentials.index(wallet)]

                # Подсчет исходящих сообщений
                if data_json.get('from_hach') == wallet_hash:
                    if data_json.get('count_coins', 0) != 0:
                        operation_stats['sent_coins_operations'] += 1  # Увеличиваем счетчик операций
                        operation_stats['sent_coins_total'] += data_json.get('count_coins', 0)  # Увеличиваем счетчик переданных монет
                    else:
                        operation_stats['sent_messages'] += 1

                # Подсчет полученных сообщений
                if data_json.get('to_hach') == wallet_hash:
                    if data_json.get('count_coins', 0) != 0:
                        operation_stats['received_coins_operations'] += 1  # Увеличиваем счетчик операций
                        operation_stats['received_coins_total'] += data_json.get('count_coins', 0)  # Увеличиваем счетчик полученных монет
                    else:
                        operation_stats['received_messages'] += 1

    # Получаем информацию о кошельках
    for wallet in wallet_credentials:
        # Создаем структуру данных для кошельков, добавляя к ним информацию, например, баланс
        blockchain_client = init_blockchain(wallet['username'], wallet['password'])
        wallet_balance = blockchain_client.check_coins().json().get('coins', 'Неизвестно')
        wallet_info = {
            'username': wallet['username'],
            'balance': wallet_balance,
            'sent_messages': wallet_stats[wallet['username']]['sent_messages'],
            'received_messages': wallet_stats[wallet['username']]['received_messages'],
            'sent_coins': wallet_stats[wallet['username']]['sent_coins'],
            'received_coins': wallet_stats[wallet['username']]['received_coins'],
            'sent_operations': wallet_stats[wallet['username']]['coin_sent_operations'],
            'received_operations': wallet_stats[wallet['username']]['coin_recieved_operations'],
        }
        wallets_info.append(wallet_info)

    # Настройки пагинации для пользователей из БД
    paginator = Paginator(db_users, 5)  # 5 пользователей на странице
    page_number = request.GET.get('page')
    paginated_users = paginator.get_page(page_number)

    # Добавление статистики в контекст
    context = {
        'db_users': paginated_users,
        'blockchain_users': paginated_blockchain_users,
        'blockchain_user_count': blockchain_user_count,
        'total_coins': total_coins,
        'top_users': top_users,
        'wallets_info': wallets_info,
        'active_tab': 'people',
        'sort_by': sort_by,
        'operation_stats': operation_stats,  # Передаем обновленную статистику по операциям
    }
    return render(request, 'people.html', context)
