#Учебный проект YaMDb

#Описание Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории (Category) Список категорий может быть расширен администратором. Сами произведения в YaMDb не хранятся. Произведению может быть присвоен жанр (Genre) из списка предустановленных. Новые жанры может создавать только администратор. Пользователи могут оставить к произведениям текстовые отзывы (Review) и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг(Rating) (целое число). На одно произведение пользователь может оставить только один отзыв.

## _Запуск_:
 - Клонируйте репозиторий на свою локальную машину:
```sh
git clone git@github.com:Thx-Phila/infra_sp2.git
cd infra
```
 - Cоздайте в папке /infra файл .env и заполните его переменными окружения:
```sh
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем c postgresql

DB_NAME=postgres # имя базы данных

POSTGRES_USER=postgres # логин для подключения к базе данных

POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)

DB_HOST=db # название сервиса (контейнера)

DB_PORT=5432 # порт для подключения к БД

SECRET_KEY=ваш секретный ключ
```
- Находясь в папке /infra, запустите сборку образа Docker:
```sh
docker-compose up -d
```
- Выполните миграции:
```sh
docker-compose exec web python manage.py migrate
```

- Создайте суперпользователя:
```sh
docker-compose exec web python manage.py createsuperuser
```
- Выполните команду collectstatic:
```sh
docker-compose exec web python manage.py collectstatic --no-input
```
- Заполните базу тестовыми данными:
```sh
docker-compose exec web python manage.py loaddata fixtures.json
```
- Перейдите по адресу:
```sh
http://localhost/api/v1
```
Автор проекта: Ворончихин Яков email: Wade333@list.ru