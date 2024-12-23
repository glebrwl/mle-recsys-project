# Подготовка виртуальной машины

## Склонируйте репозиторий

Склонируйте репозиторий проекта:

```
git clone https://github.com/yandex-praktikum/mle-project-sprint-4-v001.git
```

## Активируйте виртуальное окружение

Используйте то же самое виртуальное окружение, что и созданное для работы с уроками. Если его не существует, то его следует создать.

Создать новое виртуальное окружение можно командой:

```
python3 -m venv env_recsys_start
```

После его инициализации следующей командой

```
. env_recsys_start/bin/activate
```

установите в него необходимые Python-пакеты следующей командой

```
pip install -r requirements.txt
```

### Скачайте файлы с данными

Для начала работы понадобится три файла с данными:
- [tracks.parquet](https://storage.yandexcloud.net/mle-data/ym/tracks.parquet)
- [catalog_names.parquet](https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet)
- [interactions.parquet](https://storage.yandexcloud.net/mle-data/ym/interactions.parquet)
 
Скачайте их в директорию локального репозитория. Для удобства вы можете воспользоваться командой wget:

```
wget https://storage.yandexcloud.net/mle-data/ym/tracks.parquet

wget https://storage.yandexcloud.net/mle-data/ym/catalog_names.parquet

wget https://storage.yandexcloud.net/mle-data/ym/interactions.parquet
```

## Запустите Jupyter Lab

Запустите Jupyter Lab в командной строке

```
jupyter lab --ip=0.0.0.0 --no-browser
```

# Расчёт рекомендаций

Код для выполнения первой части проекта находится в файле `recommendations.ipynb`. Изначально, это шаблон. Используйте его для выполнения первой части проекта.

# Сервис рекомендаций

Код сервиса рекомендаций находится в файле `recommendations_service.py`.

Из папки проекта нужно запустить три сервиса из разных терминалов: 
1. uvicorn recommendations_service:app
2. uvicorn features_service:app --port 8010 
3. uvicorn events_service:app --port 8020

Для финальной версии рекоммендаций, оффлайн и онлайн рекоммендации чередуются. Когда один из списков рекоммендаций заканчивается, мы просто добавляем в конец финального списка реккоммендаций все оставшие рекоммендации из более длинного списка.


# Инструкции для тестирования сервиса

Код для тестирования сервиса находится в файле `test_service.py`.

1. Из папки проекта запустим три сервиса из разных терминалов: 
    * uvicorn recommendations_service:app
    * uvicorn features_service:app --port 8010 
    * uvicorn events_service:app --port 8020
2. Из четвертого терминала перейдем в папку test_scripts и для начала запускаем python3 test_put_events_service.py для того, чтобы добавить в хранилище ивентов взаимодействие юзера с id 1337055.
3. После можем протестировать python3 test_get_events_service.py и основной сервис: python3 test_service.py
4. Файлы test_service.log, test_feature_service.log, test_get_events_service.log и test_put_events_service.log находятся в папке test_scripts