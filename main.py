import telebot
import os
from telebot import types

# Укажите ID администратора
ADMIN_ID = 269717182

# Создаем экземпляр бота с вашим токеном
bot = telebot.TeleBot('7233663080:AAHcxhkcVH0xcdp6iKZg8F9bezVuT3cBrGQ')

# Хранение товаров в формате {ID: {данные товара}}
products = {}

# Хранение категорий
categories1 = {}
categories2 = {}


# Создаём папку, если её нет
if not os.path.exists("photos"):
    os.makedirs("photos")
# Хэндлер для команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_menu(message)


@bot.message_handler(commands=['admin'])
def admin(message):
    if message.from_user.id == ADMIN_ID:
        admin_menu(message)

# Админ меню
def admin_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Додати Товар")
    button2 = types.KeyboardButton("Видалити Товар")
    button3 = types.KeyboardButton("Редагувати Товар")
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, "Вітаю, вам доступні наступні функції:", reply_markup=markup)

# Пользовательское меню
def user_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton("Передивитись актуальні товари")
    markup.add(button)
    bot.send_message(message.chat.id, "Вітаю, скористайтесь нашою послугою!", reply_markup=markup)

# Обработка добавления товара
@bot.message_handler(func=lambda message: message.text == "Додати Товар", content_types=['text'])
def add_product(message):
    bot.send_message(message.chat.id, "Введіть ID товара:")
    bot.register_next_step_handler(message, process_id)

# Обработка ID товара
def process_id(message):
    product_id = message.text
    bot.send_message(message.chat.id, "Введіть назву товара:")
    bot.register_next_step_handler(message, process_name, product_id)

def process_name(message, product_id):
    product_name = message.text
    bot.send_message(message.chat.id, "Введіть ціну товара:")
    bot.register_next_step_handler(message, process_price, product_id, product_name)

def process_price(message, product_id, product_name):
    product_price = message.text
    bot.send_message(message.chat.id, "Введіть опис товара:")
    bot.register_next_step_handler(message, process_description, product_id, product_name, product_price)

def process_description(message, product_id, product_name, product_price):
    product_description = message.text
    bot.send_message(message.chat.id, "Введіть категорію за статтю:")
    bot.register_next_step_handler(message, process_category1, product_id, product_name, product_price, product_description)

def process_category1(message, product_id, product_name, product_price, product_description):
    category1 = message.text
    # Если категория 1 не существует, создаем ее
    if category1 not in categories1:
        categories1[category1] = []
    bot.send_message(message.chat.id, "Введіть категорію за ароматом:")
    bot.register_next_step_handler(message, process_category2, product_id, product_name, product_price, product_description, category1)

def process_category2(message, product_id, product_name, product_price, product_description, category1):
    category2 = message.text
    # Если категория 2 не существует в категории 1, добавляем
    if category2 not in categories2.get(category1, {}):
        if category1 not in categories2:
            categories2[category1] = {}
        categories2[category1][category2] = []
    
    bot.send_message(message.chat.id, "Введіть посилання на платіжну систему:")
    bot.register_next_step_handler(message, process_link, product_id, product_name, product_price, product_description, category1, category2)

def process_link(message, product_id, product_name, product_price, product_description, category1, category2):
    product_link = message.text
    bot.send_message(message.chat.id, "Відправте фото або відео товару:")
    bot.register_next_step_handler(message, process_media, product_id, product_name, product_price, product_description, category1, category2, product_link)

def process_media(message, product_id, product_name, product_price, product_description, category1, category2, product_link):
    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = f"photos/{product_id}.jpg"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        product_media = file_path  # Сохраняем путь к файлу вместо file_id

    elif message.video:
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        file_path = f"photos/{product_id}.mp4"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        product_media = file_path  # Сохраняем путь к файлу

    else:
        product_media = None

    # Сохраняем товар
    products[product_id] = {
        'name': product_name,
        'price': product_price,
        'description': product_description,
        'category1': category1,
        'category2': category2,
        'link': product_link,
        'media': product_media
    }

    categories2[category1][category2].append(product_id)
    bot.send_message(message.chat.id, f"Товар {product_name} успішно додано!")

# Удаление товара
@bot.message_handler(func=lambda message: message.text == "Видалити Товар", content_types=['text'])
def delete_product(message):
    bot.send_message(message.chat.id, "Введіть ID товара для видалення:")
    bot.register_next_step_handler(message, process_delete)

def process_delete(message):
    product_id = message.text
    if product_id in products:
        # Получаем категории товара
        category1 = products[product_id]['category1']
        category2 = products[product_id]['category2']

        # Удаляем товар из основного словаря
        del products[product_id]

        # Удаляем товар из категории
        if category1 in categories2 and category2 in categories2[category1]:
            if product_id in categories2[category1][category2]:
                categories2[category1][category2].remove(product_id)
            
            # Если в подкатегории больше нет товаров, удаляем её
            if not categories2[category1][category2]:
                del categories2[category1][category2]

            # Если в категории больше нет подкатегорий, удаляем её
            if not categories2[category1]:
                del categories2[category1]

        bot.send_message(message.chat.id, "Товар видалено.")
    else:
        bot.send_message(message.chat.id, "Товар з таким ID не знайдено.")
# Редактирование товара
@bot.message_handler(func=lambda message: message.text == "Редагувати Товар", content_types=['text'])
def edit_product(message):
    bot.send_message(message.chat.id, "Введіть ID товару для редагування:")
    bot.register_next_step_handler(message, process_edit)

def process_edit(message):
    product_id = message.text
    if product_id in products:
        product = products[product_id]
        bot.send_message(message.chat.id, f"Товар знайдено: {product['name']}. Что хочете редагувати?? (Назва, Ціна, Опис, Стать, Аромат, Посилання, Фото/Відео)")
        bot.register_next_step_handler(message, process_edit_field, product_id)
    else:
        bot.send_message(message.chat.id, "Товар з таким ID не знайдено.")

def process_edit_field(message, product_id):
    field = message.text.strip().lower()
    valid_fields = {
        'назва': 'name',
        'ціна': 'price',
        'опис': 'description',
        'стать': 'category1',
        'аромат': 'category2',
        'посилання': 'link',
        'фото/відео': 'media'
    }
    
    if field in valid_fields:
        if field == 'фото/відео':
            bot.send_message(message.chat.id, "Відправте нове фото або відео товару:")
            bot.register_next_step_handler(message, process_media_edit, product_id)
        else:
            bot.send_message(message.chat.id, f"Введіть нове значення для {field}:")
            bot.register_next_step_handler(message, process_field_value, product_id, valid_fields[field])
    else:
        bot.send_message(message.chat.id, "Невірно обране поле. Виберіть одне з: Назва, Ціна, Опис, Стать, Аромат, Посилання, Фото/Відео.")

def process_field_value(message, product_id, field_key):
    new_value = message.text.strip()
    products[product_id][field_key] = new_value
    bot.send_message(message.chat.id, "Товар оновлено.")

def process_media_edit(message, product_id):
    if message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = f"photos/{product_id}.jpg"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        products[product_id]['media'] = file_path
    elif message.video:
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_path = f"photos/{product_id}.mp4"
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        products[product_id]['media'] = file_path
    else:
        bot.send_message(message.chat.id, "Файл не розпізнано. Спробуйте ще раз.")
        return
    
    bot.send_message(message.chat.id, "Фото/Відео оновлено.")


# Просмотр товаров пользователем
@bot.message_handler(func=lambda message: message.text == "Передивитись актуальні товари", content_types=['text'])
def show_products(message):
    markup = types.InlineKeyboardMarkup()
    for category in categories1.keys():
        button = types.InlineKeyboardButton(category, callback_data=category)
        markup.add(button)
    bot.send_message(message.chat.id, "Оберіть стать:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data in categories1)
def category_selection(call):
    category1 = call.data
    markup = types.InlineKeyboardMarkup()
    for category2_item in categories2.get(category1, {}).keys():
        button = types.InlineKeyboardButton(category2_item, callback_data=f"{category1}|{category2_item}")
        markup.add(button)
    bot.send_message(call.message.chat.id, "Оберіть аромат:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: '|' in call.data and call.data.split('|')[0] in categories2)
def show_products_by_category(call):
    category1, category2 = call.data.split('|')

    # Добавляем отладочное сообщение
    bot.send_message(call.message.chat.id, f"Оберіть щось з наступного: {category1} -> {category2}")

    product_list = categories2.get(category1, {}).get(category2, [])

    # Ещё одно отладочное сообщение для проверки списка товаров
    bot.send_message(call.message.chat.id, f"Знайдено товарів: {len(product_list)}")

    if not product_list:
        bot.send_message(call.message.chat.id, "В цій категорії покищо немає товарів.")
        return

    for product_id in product_list:
        if product_id not in products:  # Проверка, существует ли товар в словаре
            continue  # Пропускаем несуществующий товар

        product = products[product_id]
        caption = f"Назва: {product['name']}\nЦіна: {product['price']} гривень\nОпис: {product['description']}"
        markupssss = types.InlineKeyboardMarkup()
        buy_button = types.InlineKeyboardButton("💳 Купити", url=product['link'])
        markupssss.add(buy_button)
        

        if product['media']:  
            if product['media'].endswith('.jpg'):
                with open(product['media'], 'rb') as photo:
                    bot.send_photo(call.message.chat.id, photo, caption=caption, reply_markup=markupssss)
            elif product['media'].endswith('.mp4'):
                with open(product['media'], 'rb') as video:
                    bot.send_video(call.message.chat.id, video, caption=caption, reply_markup=markupssss)
        else:
            bot.send_message(call.message.chat.id, caption, reply_markup=markupssss)





# Запуск бота
bot.polling(none_stop=True)

