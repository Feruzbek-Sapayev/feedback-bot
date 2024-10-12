import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from aiogram.types.keyboard_button import KeyboardButton
from db import DataBase as db
from aiogram.enums.chat_type import ChatType


TOKEN = "7716250999:AAGVucoUyH03cc0WQHKI8LiJa_0ymBH_XTg"
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

#db
db.create_table_users()
db.create_table_applications()
db.create_table_answers()

class UserState(StatesGroup):
    main = State()
    enterprise = State()
    passport = State()
    problem = State()
    media = State()
    suggestions = State()
    reply = State()
    send_reply = State()
    select_app = State()
    view_app = State()

def get_reply_btn(id, message_id, app_id):
    reply_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Жавоб ёзиш', callback_data=f'reply_{id}_{message_id}_{app_id}')]
    ])
    return reply_btn

def get_apps_btn(applications):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[])
    markup.keyboard.append([KeyboardButton(text="⬅️ Оркага")])
    for i in range(0, len(applications)//2, 2):
        text1 = applications[i][0]
        text2 = applications[i+1][0]
        markup.keyboard.append([KeyboardButton(text=str(text1)), KeyboardButton(text=str(text2))])
    if len(applications)%2 == 1:
        text = applications[-1][0]
        markup.keyboard.append([KeyboardButton(text=str(text))])
    return markup

def get_answer_btn(msg_id):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Жавоб ёзиш", url=f"https://t.me/c/4500975902/{msg_id}")],
    ])
    return markup

cancel_btn = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='✅ Тугатиш')]
])
main_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="✍🏻 Претензия юбориш")],
    [KeyboardButton(text="📬 Мурожаатларни текшириш")]
])
next_btn = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="✅ Юбориш")],
    [KeyboardButton(text="❌ Бекор килиш")]
])
go_to_back_btn = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="⬅️ Оркага")]
])
exit_btn = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="❌ Бекор килиш")]
])

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    print(message.chat.id)
    user = db.select_user(message.from_user.id)
    if user is None:
        db.add_user(message.from_user.id)
    await message.answer(f"Assalomu aleykum, {message.from_user.full_name}", reply_markup=main_markup)
    await state.set_state(UserState.main)

@dp.message(UserState.main)
async def main_handler(message: types.Message, state: FSMContext):
    if message.text == "✍🏻 Претензия юбориш":
        await message.answer("Корхонангиз номини ёзинг:", reply_markup=exit_btn)
        await state.set_state(UserState.enterprise)
    elif message.text == "📬 Мурожаатларни текшириш":
        applications = db.select_user_applications(message.from_user.id)
        if applications:
            markup = get_apps_btn(applications)
            await message.answer("Мурожаат ракамини танланг:", reply_markup=markup)
            await state.set_state(UserState.select_app)
        else:
            await message.answer('📭')
            await message.answer('Сиз хали мурожаат юбормагансиз!')

@dp.message(UserState.select_app)
async def select_app_handler(message: Message, state: FSMContext):
    if message.text:
        if message.text == '⬅️ Оркага':
            await message.answer('Асосий меню!', reply_markup=main_markup)
            await state.set_state(UserState.main)
        else:
            app = db.select_application_by_id(message.from_user.id, message.text)
            if app:
                answers = db.select_application_answers(app[0])
                if answers:
                    await state.set_state(UserState.view_app)
                    await message.answer(f"<b>№{app[0]} сонли мурожаат учун жавоб:</b>", parse_mode='html', reply_markup=go_to_back_btn)
                    for msg in answers:
                        author = msg[-1]
                        markup = get_reply_btn(author, app[2], app[0])
                        await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id, message_id=msg[2], reply_markup=markup)
                else:
                    await message.answer("Ушбу мурожаатингиз учун жавоб келмаган!")
            else:
                await message.answer("Мурожаат ракамини танланг:")
    else:
        await message.answer("Мурожаат ракамини танланг:")

@dp.message(UserState.view_app)
async def view_app_handler(message: Message, state: FSMContext):
    if message.text and message.text == "⬅️ Оркага":
        applications = db.select_user_applications(message.from_user.id)
        if applications:
            markup = get_apps_btn(applications)
            await message.answer("Мурожаат ракамини танланг:", reply_markup=markup)
            await state.set_state(UserState.select_app)
        else:
            await message.answer('📭')
            await message.answer('Сиз хали мурожаат юбормагансиз!')
    else:
        await message.answer("Хато буйрук! Янги морожаат юбориш учун <b>Асосий менюга</b> кайтинг!", reply_markup=go_to_back_btn)
        

@dp.message(UserState.enterprise)
async def enterprise_handler(message: Message, state: FSMContext):
    if message.text:
        if message.text == "❌ Бекор килиш":
            await message.answer("Мурожаат юбориш бекор килинди!", reply_markup=main_markup)
            await state.set_state(UserState.main)
        else:
            await state.set_data({'enterprise': message.text})
            await message.answer("Маҳсулот паспорти расмини юборинг:", reply_markup=exit_btn)
            await state.set_state(UserState.passport)
    else:
        await message.answer("Корхонангиз номини ёзинг:")

@dp.message(UserState.passport)
async def passport_handler(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data({'passport': message.photo[-1].file_id})
        await message.answer("Претензияни тўлиқ таърифлаб, барча деталларни ёзинг ёки овозли хабар юборинг:", reply_markup=exit_btn)
        await state.set_state(UserState.problem)
    elif message.text and message.text == "❌ Бекор килиш":
        await message.answer("Мурожаат юбориш бекор килинди!", reply_markup=main_markup)
        await state.set_state(UserState.main)
    else:
        await message.answer("Маҳсулот паспорти расмини юборинг(1 та):")

@dp.message(UserState.problem)
async def problem_handler(message: Message, state: FSMContext):
    if message.text:
        if message.text == "❌ Бекор килиш":
            await message.answer("Мурожаат юбориш бекор килинди!", reply_markup=main_markup)
            await state.set_state(UserState.main)
        else:
            await state.update_data({'problem_text': message.text})
            await message.answer("Претензия бўйича фото ёки видео материалларни алохида юборинг ва <b>'✅ Юбориш'</b> тугмасини босинг.", reply_markup=next_btn)
            await state.set_state(UserState.media)
            await state.update_data({'media': []})
    elif message.voice:
        await state.update_data({'problem_voice': message.voice.file_id})
        await message.answer("Претензия бўйича фото ёки видео материалларни алохида юборинг ва <b>'✅ Юбориш'</b> тугмасини босинг.", reply_markup=next_btn)
        await state.set_state(UserState.media)
        await state.update_data({'media': []})
    else:
        await message.answer("Претензияни тўлиқ таърифлаб, барча деталларни ёзинг ёки овозли хабар юборинг:")

@dp.message(UserState.media)
async def media_handler(message: Message, state: FSMContext):
    if message.text and message.text == "✅ Юбориш":
        media = (await state.get_data()).get('media')
        if media:
            await message.answer("Ушбу ҳолат бўйича ўз тахминларингиз (нега бундай бўлганлиги) ва қанақа ечим қилишимиз бўйича таклифларингизни ёзинг:", reply_markup=exit_btn)
            await state.set_state(UserState.suggestions)
        else:
            await message.answer("Медиафайл юбормадингиз!", reply_markup=next_btn)
    elif message.text and message.text == "❌ Бекор килиш":
            await message.answer("Мурожаат юбориш бекор килинди!", reply_markup=main_markup)
            await state.set_state(UserState.main)
    elif message.media_group_id:
            await message.answer("Илтимос, медиафайлларни алохида юборинг!", reply_markup=next_btn)
    elif message.photo:
        media = (await state.get_data()).get('media')
        media.append({'photo': message.photo[-1].file_id})
        await state.update_data({'media': media})
    elif message.video:
        media = (await state.get_data()).get('media')
        media.append({'video': message.video.file_id})
        await state.update_data({'media': media})
    else:
        await message.answer("Претензия бўйича фото ёки видео материалларни алохида юборинг ва <b>'✅Юбориш'</b> тугмасини босинг.", reply_markup=next_btn)

@dp.message(UserState.suggestions)
async def suggestions_handler(message: Message, state: FSMContext):
    if message.text:
        if message.text == "❌ Бекор килиш":
            await message.answer("Мурожаат юбориш бекор килинди!", reply_markup=main_markup)
            await state.set_state(UserState.main)
        else:
            await state.update_data(suggestions=message.text)
            user_data = await state.get_data()
            enterprise = user_data['enterprise']
            passport = user_data['passport']
            try:
                problem_text = user_data['problem_text']
                problem_voice = None
            except:
                problem_voice = user_data['problem_voice']
                problem_text = None
            media = user_data['media']
            suggestions = user_data['suggestions']

            group_chat_id = '-4500975902'
            db.add_application(message.from_user.id, 0)  #application yaratamiz
            app = db.select_application_by_user(message.from_user.id, 0)
            feedback_message = (
                f"📌 Murojaat №{app[0]}\n"
                f"📋 Korxona nomi: {enterprise}\n"
                f"💡 Takliflar: {suggestions}"
            )
            msg = None
            if problem_text:
                feedback_message = (
                    f"📌 Murojaat №{app[0]}\n"
                    f"📋 Korxona nomi: {enterprise}\n"
                    f"🚨 Muammo: {problem_text}\n"
                    f"💡 Takliflar: {suggestions}"
                )
                msg = await bot.send_message(chat_id=group_chat_id, text=feedback_message)
            else:
                msg = await bot.send_message(chat_id=group_chat_id, text=feedback_message)
                await bot.send_voice(chat_id=group_chat_id, voice=problem_voice, caption='🚨 Muammo')
            db.update_application(app[0], msg.message_id) # application message_id yangilaymiz
            await bot.send_photo(chat_id=group_chat_id, photo=passport, caption='🔖 Passport')
            media_group = MediaGroupBuilder(caption=f'❗️ Muammo')
            for med in media:
                if med.get('photo'):
                    media_group.add(type='photo', media=med.get('photo'), parse_mode='html')
                else:
                    media_group.add(type='video', media=med.get('video'), parse_mode='html')
            await bot.send_media_group(chat_id=group_chat_id, media=media_group.build())
            await message.answer(f"Сизнинг №{app[0]} сонли мурожаатингиз қабул қилинди. Мурожаат 3 кун ичида ўрганиб чиқилиб, натижаси бўйича хулосага келинади. Вақт талаб қилинадиган ҳолатларда қўшимча яна 3 кунга чўзилиши мумкин. Шошилинч ва осон ҳал этиладиган ҳолатларда узоғи 12 соатгача ўрганиб, жавоб берилади.", reply_markup=main_markup)
            await state.set_state(UserState.main)
    else:
        await message.answer("Ушбу ҳолат бўйича ўз тахминларингиз (нега бундай бўлганлиги) ва қанақа ечим қилишимиз бўйича таклифларингизни ёзинг:", reply_markup=ReplyKeyboardRemove())
        
        
# Guruhdan kelgan javobni qayta ishlash
@dp.message(lambda message: message.reply_to_message)
async def handle_group_reply(message: types.Message):
    if ChatType.GROUP: 
        reply_message = message.reply_to_message
        application = db.select_application(reply_message.message_id)
        if application:
            user_id = application[1]
            await message.answer(f"<b>Сизнинг №{application[0]} сонли мурожаатингиз учун жавоб келди:</b>", parse_mode='html')
            msg = await message.send_copy(chat_id=user_id, reply_markup=get_reply_btn(message.from_user.id, application[2], application[0]))
            db.add_app_message(application[0], msg.message_id, message.from_user.id)
        else:
            await message.reply("Bu xabar uchun foydalanuvchini topa olmadim.")
        
@dp.message(UserState.send_reply)
async def repl_msg(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('user_id')
    message_id = data.get('message_id')
    app_id = data.get('app_id')
    if message.text == '✅ Тугатиш':
        await message.answer('Чат тугатилди!', reply_markup=main_markup)
        await state.clear()
        await state.set_state(UserState.main)
    else:
        await bot.send_message(text=f"<b>№{app_id} сонли мурожаатга кушимча савол:</b>", chat_id=user_id, reply_markup=get_answer_btn(message_id))
        await message.send_copy(chat_id=user_id)
        await message.answer("Жавоб админга юборилди!")

@dp.message()
async def all_msgs(message: types.Message, state: FSMContext):
    if ChatType.GROUP:
        await message.answer("Ботни ишлатиш учун /start босинг!")
        
@dp.callback_query()
async def callbacks_hndler(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('reply'):
        _, user_id, message_id, app_id = call.data.split('_')
        await state.update_data(user_id=user_id, message_id=message_id, app_id=app_id)
        await call.message.answer('Жавобни юборишингиз мумкин:', reply_markup=cancel_btn)
        await state.set_state(UserState.send_reply)

    await call.answer()

async def main() -> None:
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())