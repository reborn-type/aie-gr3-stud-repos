# cli-eda-project

## Доступные cli-команды

`overview` - с помощью этой команды можно напечатать краткий обзор датасета:
    - размеры;
    - типы;
    - простая табличка по колонкам.

`report` - c помощью этой команды можно сгенерировать полный EDA-отчёт:
    - текстовый overview и summary по колонкам (CSV/Markdown);
    - статистика пропусков;
    - корреляционная матрица;
    - top-k категорий по категориальным признакам;
    - картинки: гистограммы, матрица пропусков, heatmap корреляции.

## Новые параметры добавленые к report 

`--title` - Изменят загаловок отчета, принимает значение строки.

`--min-missing-share` - Минимально допустимая доля пропусков в датасете (влияет на выставление флага и изменение оценки качества), принимает float значения (по дефолту значение 0.5).

## Пример вызова CLI-report

`uv run eda-cli --title "Отчет для csv датасета из HW02" --min-missing-share 0.3 ./data/S02-hw-dataset.csv`

# eda-project by FastAPI

## Нужные команды для использования: 

Для синхронизации библиотек и пакетов с виртуальным окружением
`uv sync`

Для запуска тестов 
`uv run pytest -q`

Запуск сервера на localhost
`uv run uvicorn eda_cli.api:app --port 8000`

Запуск скрипта
`uv run eda-cli report ./data/example.csv`


## Доступные эндпоинты 

`/healt` - Простейший health-check сервиса.

`/quality` - Эндпоинт, который принимает агрегированные признаки датасета и возвращает эвристическую оценку качества. 

`/quality-from-csv` - Эндпоинт, который принимает CSV-файл, запускает EDA-ядро (summarize_dataset, missing_table, compute_quality_flags, is_unique_identificators, zeros_table) и возвращает оценку качества данных.

`/quality-flags-from-csv` - Эндпоинт, который принимает CSV-файл, запускает EDA-ядро(summarize_dataset, missing_table, compute_quality_flags, is_unique_identificators, zeros_table), и возвращает `буллевый словарь флагов в формате JSON`.
