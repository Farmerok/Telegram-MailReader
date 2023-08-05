#TEST
import requests, time, imaplib, email, telebot, os, ctypes, urllib.parse

from telebot import types

tgram = "insiderkeeps"
def primary():
    primarys = types.ReplyKeyboardMarkup(True, False, input_field_placeholder='Checking post')
    buttons = [
        types.KeyboardButton('/Read'),
        types.KeyboardButton('/FAQ'),
    ]
    for i in range(0, len(buttons), 3):
        primarys.row(*buttons[i:i+3])
    return primarys

# создать файл если не существует и заполнить его
if not os.path.exists("config.txt"):
    with open("config.txt", "w") as file:
        file.write("IMAP Host = \n")
        file.write("IMAP User = \n")
        file.write("IMAP Pass = \n")
        file.write("Bot Token = \n")
        file.write("Chat ID = \n")

#читаем
with open("config.txt", "r") as file:
    lines = file.readlines()
    imap_host = lines[0].split("= ")[1].strip()
    imap_user = lines[1].split("= ")[1].strip()
    imap_pass = lines[2].split("= ")[1].strip()
    bot_token = lines[3].split("= ")[1].strip()
    chat_id = lines[4].split("= ")[1].strip()


#Token
bot = telebot.TeleBot(bot_token, threaded=True)

def Admin():  return ctypes.windll.shell32.IsUserAnAdmin() != 0 #Load scritps Admin

#Primary func
def read_mail():
    try:
        # Пробуем коннектится к почте
        mail = imaplib.IMAP4_SSL(imap_host)
        mail.login(imap_user, imap_pass)
        mail.select('inbox')

        # поиск всех смс
        status, messages = mail.search(None, 'UNSEEN')

        #Если нет смс
        if not messages[0]:
            return 'На почте писем больше не обнаружено 😕'

        # Проверяем каждое непрочитанное сообщение и извлекаем текст из почты.

        for message_id in messages[0].split():
            status, msg = mail.fetch(message_id, '(RFC822)')
            for response in msg:
                if isinstance(response, tuple):
                    msg = email.message_from_bytes(response[1])
                    email_text = None
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            if content_type == 'text/plain':
                                email_text = part.get_payload(decode=True).decode()
                                break
                    else:
                        email_text = msg.get_payload(decode=True).decode()
                    
                    # Если текст почты не найден, скипаем сообщение
                    if email_text is None:
                        continue

                    sender = email.utils.parseaddr(msg['From'].encode('utf-8').decode())[0]
                    timestamp = email.utils.parsedate_to_datetime(msg['Date']).strftime('%Y-%m-%d %H:%M:%S')
                    email_info = f"From: {sender}\nTime: {timestamp}\nText: {email_text}"
                    
                    # Trim the email text to a maximum of 1000 characters and URL encode it
                    trimmed_email_info = email_info[:1000]
                    encoded_email_info = urllib.parse.quote(trimmed_email_info)
                    url = f'https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&text={encoded_email_info}'
                    response = requests.get(url)
                    if response.status_code != 200:
                        print(f"Ошибка отправки СМС: {response.text}")
    except Exception as e:
        print(f"Ошибка чтения почты: {e}")
        message_error = f'{e}'
        bot.send_message(chat_id, message_error)
        ctypes.windll.user32.MessageBoxW(0, f'Упс.. ошибка: {e}', u'Информация об ошибке', 0x10) 
        return
def main():
    
    if not bot_token or not chat_id:
        ctypes.windll.user32.MessageBoxW(0, f'Заполните оба поля (Bot Token и Chat ID) в файле config.txt', u'Ошибка чтения', 0x10)
        return

    if not imap_host:
        ctypes.windll.user32.MessageBoxW(0, f'Заполните поле (imap_host) с каким E-mail мне взаимодействовать.\nПримечание: Бот будет работать но не полностью, пока не укажешь значение в config.txt. Рекомендую к прочтению FAQ', u'Предупреждение', 0x00000030)

    PC = 'С АДМИН ПРАВАМИ' if Admin() else 'БЕЗ АДМИН ПРАВ'
    try:
        ctypes.windll.user32.MessageBoxW(0, f'Введённые данные считаны успешно, скрипт  был запущен {PC}', u'Информация', 0x00000040)
    except Exception as err:
        print('[-] › Retrying connect to api.telegram.org\n' + err)
    else:
        print('[+] › Connected to api.telegram.org\n')
    

    @bot.message_handler(commands=['Start','Read', 'FAQ'])
    def handle_commands(message):
        
        inf = {
        'FirstName -' : message.from_user.first_name,
        'Last - ' : message.from_user.last_name,
        }
        if str(message.chat.id) not in chat_id:
            bot.send_message(message.chat.id, f'🔴 - *{inf["FirstName -"]} {inf["Last - "]}*, у тебя нет прав. Если проблема возникла ошибочно - пиши разработчику - {tgram}', parse_mode="Markdown", reply_markup=types.ReplyKeyboardRemove())
            return      

        if message.text == '/Start':    
            bot.send_message(message.chat.id, f'Привет. Если ты видишь это сообщение, то токен и и ID введено верно \n\nDeveloper - {tgram} ', reply_markup=primary())
            
        if message.text == '/FAQ':
            faq_message = '''
    ℹ️ Какими функциями обладает бот?

        - `Читать сообщения с почты( бывает такое письмо, что он не сможет прочитать из за его содержимого )`

        - `Бот в ваших руках, изменяете, настраиваеет только ВЫ через конфиг config.txt, который создаётся автоматически при первом запуске скрипта`

    ℹ️ Как правильно указать данные для полной корректной работы программы?

            -  `IMAP Host= КАКОЙ ТИП ПОЧТЫ`:

            ( `imap.gmail.com` \ `imap.mail.ru` ) ...
            
            - `IMAP User= Логин от почты`
            
            - `IMAP Pass= Пароль от почты(Не основной пароль) `
            ( МОЖНО ПОЛУЧИТЬ ЗДЕСЬ - https://myaccount.google.com/security )
            
            - `Bot Token= Токен можно взять у бота` ( @BotFather )
             
            - `Chat ID= ИД МОЖНО Взять у бота` ( @userinfobot ) '''

            bot.send_message(message.chat.id, faq_message, reply_markup=primary(), parse_mode="Markdown")
        elif message.text == '/Read':
            if imap_user == "":
                bot.send_message(message.chat.id, "⚠️ *Поле с имя почты пустое. Заполните файл таким образом:*\n`IMAP User: ваша почта`", parse_mode="Markdown")
                return
            if imap_pass == "":
                bot.send_message(message.chat.id, "⚠️ *Поле с паролем пустое. Заполните файл таким образом:* \n`IMAP Pass: ваш пароль`", parse_mode="Markdown")
                return

            try:
                bot.send_message(message.chat.id, 'Проверяю почту 😇', reply_markup=primary())
                read_mail()
                bot.send_message(message.chat.id, read_mail())
            except: pass

    while True:
        try:
            response = requests.get('https://www.google.com')
            if response.status_code == 200:
                bot.polling(none_stop=True, interval=1, timeout=123, skip_pending=True)
                print('Bot (ok)')
                break
        except Exception as err:
            print(f'Bot (error)\n {err}')
            
        time.sleep(30)

if __name__ == "__main__":
    main()