# Сервис YaCut

Сервис позволяет генерировать короткие ссылки.

## Установка

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:MrProfessorCat/yacut.git
```

```
cd yacut
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

```
flask run
```