import io
import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from utils.generate import generate_client, is_admin, admin_list, check_client_profile, restart_system
from utils.generate import get_clients_profile_by_id, get_client_profile_by_name, get_user_by_id
from utils.create import create_client, add_user
from utils.qr_gen import generate_qr
from db.mgs_template import REQUEST, REQUEST_SEND, LINKS, LINKS_KEY
from dotenv import load_dotenv


load_dotenv()


bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot, storage=MemoryStorage())


class States(StatesGroup):
    START = State()  # Initial state
    NAME = State()  # State for asking the user's name
    END = State()  # Final state


def profile_keyboard(profiles):
    keyboard = types.InlineKeyboardMarkup()
    for p in profiles:
        keyboard.add(types.InlineKeyboardButton(text=f"{p.name} - {p.tlg}", callback_data=f"profile*{p.name}") )
        
    return keyboard


main_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.row("Запросить VPN профиль")
main_keyboard.row("Показать VPN профили")
main_keyboard.row("Скачать VPN приложение")


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    username = ''
    firstname = ''
    lastname = ''
    if message.chat.username is not None:
        username = message.chat.username

    if message.chat.last_name is not None:
        lastname = message.chat.last_name

    if message.chat.first_name is not None:
        firstname = message.chat.first_name

    name = f"{username} - {firstname} {lastname}"
    try:
        add_user(message.chat.id, name)
    except Exception as e:
        print(e)
    await message.answer("Выберите опцию.", reply_markup=main_keyboard)


@dp.message_handler(commands="id")
async def my_id(message: types.Message):
    await message.answer(message.chat.id)


@dp.message_handler(commands="reload")
async def system_reloader(message: types.Message):
    if is_admin(message.chat.id):
        restart_system()
        await message.answer("System has been restarted.")


# @dp.message_handler(lambda message: message.text == "Скачать VPN приложение")
@dp.message_handler(Text(equals="Скачать VPN приложение"))
async def vpn_app_links(message: types.Message):
    await message.answer(LINKS, reply_markup=LINKS_KEY, parse_mode="HTML")


@dp.message_handler(lambda message: message.text == "Показать VPN профили")
async def show_vpn_profiles(message: types.Message):
    profiles = get_clients_profile_by_id(message.chat.id)
    if len(profiles) < 1:
        await message.answer("У вас нет доступных профилей. Воспользуйтесь запросом профиля.")
    else:
        keyboard = profile_keyboard(profiles)
        await message.answer(f"Ваши VPN профили:", reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith('profile*'))
async def process_callback_profile(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    profile_name = callback_query.data.split('*')[1]
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=f"Скачать файл", callback_data=f"download*{chat_id}*{profile_name}"))
    keyboard.add(types.InlineKeyboardButton(text=f"Показать Qr Код", callback_data=f"qrcode*{chat_id}*{profile_name}"))
    keyboard.add(types.InlineKeyboardButton(text=f"<< Назад <<", callback_data=f"back_profiles"))
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith('download*'))
async def allow_profile(callback_query: types.CallbackQuery):
    tlg_id = callback_query.data.split('*')[1]
    profile_name = callback_query.data.split('*')[2]
    text = generate_client(tlg_id, profile_name)
    document = types.InputFile(io.BytesIO(text.encode()), filename=f"wg-{profile_name}.conf")
    await bot.send_document(callback_query.from_user.id, document)


@dp.callback_query_handler(lambda query: query.data.startswith('qrcode*'))
async def deny_profile(callback_query: types.CallbackQuery):
    tlg_id = callback_query.data.split('*')[1]
    profile_name = callback_query.data.split('*')[2]
    photo = generate_qr(tlg_id, profile_name)
    await bot.send_photo(callback_query.from_user.id, photo)


@dp.callback_query_handler(lambda query: query.data.startswith('back_profiles'))
async def back_to_profiles(callback_query: types.CallbackQuery):
    profiles = get_clients_profile_by_id(callback_query.message.chat.id)
    keyboard = profile_keyboard(profiles)
    await bot.edit_message_reply_markup(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id, reply_markup=keyboard)


@dp.message_handler(Text(equals="Запросить VPN профиль"))
async def process_name(message: types.Message, state: FSMContext):
    await message.answer(REQUEST, parse_mode="HTML")
    await States.NAME.set()
    await state.update_data(state="name")


@dp.message_handler(state=States.NAME)
async def request_profile(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    if check_client_profile(message.chat.id, data['name']):
        await message.answer("Такой профиль уже существует. Введите новое имя.", parse_mode="HTML")
        await States.NAME.set()
        await state.update_data(state="name")
    else:
        await message.answer(REQUEST_SEND, parse_mode="HTML")
        await States.END.set()
        await state.update_data(state="end")
        await state.finish()
        msg = f"Request from {get_user_by_id(message.chat.id).name}, profile: {data['name']}."
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text=f"Allow", callback_data=f"allow*{message.chat.id}*{data['name']}"))
        keyboard.add(types.InlineKeyboardButton(text=f"Deny", callback_data=f"deny*{message.chat.id}*{data['name']}"))
        for uid in admin_list():
            await bot.send_message(uid, msg, reply_markup=keyboard)


@dp.callback_query_handler(lambda query: query.data.startswith('allow*'))
async def allow_profile(callback_query: types.CallbackQuery):
    tlg_id = callback_query.data.split('*')[1]
    profile_name = callback_query.data.split('*')[2]
    create_client(tlg_id, profile_name)
    msg = f"Ваш профиль <{profile_name}> активирован. Нажмите кнопку показать профили."
    await bot.send_message(tlg_id, msg, reply_markup=main_keyboard)
    await bot.send_message(callback_query.message.chat.id, f"You allowed {profile_name} for {tlg_id} user.")


@dp.callback_query_handler(lambda query: query.data.startswith('deny*'))
async def deny_profile(callback_query: types.CallbackQuery):
    tlg_id = callback_query.data.split('*')[1]
    profile_name = callback_query.data.split('*')[2]
    await bot.send_message(tlg_id, f'Ваш профиль "{profile_name}" отклонен.')
    await bot.send_message(callback_query.message.chat.id, f"You denied {profile_name} for {tlg_id} user.")


@dp.message_handler()
async def echo(message: types.Message):
    # old style:
    # await bot.send_message(message.chat.id, message.text)
    await message.answer(message.text)


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
