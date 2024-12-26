import time
import datetime
import threading
from blockchain import BlockChain
from multiprocessing import Pool, cpu_count
import json

link_client = 'https://b1.ahmetshin.com/static/blockchain.py'
username = 'TestValid1'
password = '1'
init = BlockChain(username=username, password=password, base_url='https://b1.ahmetshin.com/restapi/')

# Функция для обработки задачи
def process_task(task, proc_id):
    id = task['id']
    data_json = task['data_json']
    hash = init.get_hash_object(json.dumps(data_json))
    result_hash = init.make_hash(hash)
    data = {
        'type_task': 'BlockTaskUser _Solution',
        'id': id,
        'hash': result_hash
    }
    thread_id = threading.get_ident()  # Получаем идентификатор текущего потока
    print(f"Ядро №{proc_id}, Поток №{thread_id}: Обрабатывается задача {id}")
    result = init.send_task(data)
    return result.json()

def worker(tasks, proc_id):
    results = []
    for task in tasks:
        result = process_task(task, proc_id)
        results.append(result)
    return results

if __name__ == "__main__":

    init.get_version_file()

    while True:
        time.sleep(2)
        print(f'sleep {str(datetime.datetime.now())}')

        # Получаем цепочки какие есть, и сохраняем у себя локально
        result = init.get_chains()

        # получаем задачи, которые надо решить
        result = init.get_task().json()
        print(result)

        # проверяем какие задачи поступили на решение
        if result['tasks']:
            tasks = result['tasks']
            n_proc = cpu_count()  # Количество доступных ядер
            # Разделяем задачи между процессами
            chunk_size = len(tasks) // n_proc + (len(tasks) % n_proc > 0)
            task_chunks = [tasks[i:i + chunk_size] for i in range(0, len(tasks), chunk_size)]

            with Pool(processes=n_proc) as pool:
                # Передаем номер процесса в качестве аргумента
                results = pool.starmap(worker, [(task_chunks[i], i) for i in range(len(task_chunks))])

            # Обработка результатов, если необходимо
            for result in results:
                for res in result:
                    print(res)
