"""
Telegram-бот для мода HoI4 «штымпы» (aiogram 3.x)

Запуск:
    pip install "aiogram>=3.7"
    export BOT_TOKEN="123456:ABC..."     # Windows: set BOT_TOKEN=...
    python shtympy_bot.py

В BotFather отключи Privacy Mode (/setprivacy -> Disable), иначе бот не будет
видеть команды в группах при обращении без @имени.
"""

import asyncio
import html
import json
import logging
import os
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatMemberStatus, ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    User,
)

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DATA_FILE = os.getenv("DATA_FILE", "divisions.json")

router = Router()
GROUP_ONLY = F.chat.type.in_({"group", "supergroup"})


# ============================================================================
# ДАННЫЕ
# ============================================================================

WHO_LIST: List[str] = [
    "Антон Китлеренко (Украинская Соборная Держава) — бедный австрийский беженец которого приютила волынь",
    "Тарас Шевченко (Вольный город Петроград) — мне жаль что ты ещё дышишь",
    "Елена Отт-Скоропадская (Украинский Нуклеархический Гетьманат) — «Еби всех ядеркой,выебаный не будешь»",
    "Мао (Нац Китай) — ебать коммунисты пидоры",
    "Муссолини (Четвертый рим) — За что мут суки",
    "Махно (Вольная территория) — Ебучий папуас",
    "Власов (Белая Россия) — У тебя нихуя нет и по жизни ты нихуя не добился",
    "Берия (Красная Россия) — Кто насрал мне в штаны?",
    "Маннергейм (Финляндия) — вроде старый а вроде и похуй",
    "Владислав Сикорський (Польща) — wypierdalaj na Ukrainę",
    "Анте Павелич (Хорватия) — главный читатель сказок сербам",
    "Генерал Олександр Натієв (Гетьман-Штадт Єрусалим) — Генерал-губернатор, колония Украины, окруженный арабами, которые мечтают его повесить",
    "Ідріс I (Королівство Лівія) — Под протекторатом и наместничеством Украины",
    "Ібн Сауд (Великий Арабський Халіфат) — Сидит на нефти и люто ненавидит каждого украинца на пушечный выстрел",
    "Султан Омер Фарук (Османський Султанат) — Флаг похож на флаг педиков",
    "Наслідний Емір Шахмурад (Бухарський Емірат) — маленькая хуйня на карте",
    "Саїд Абдулла-хан (Хівинське Ханство) — еще меньше",
    "Мохаммед Захір-шах (Афганський Емірат) — Гордый горец",
    "Мохаммед Реза Пехлеві (Персія) — Шах с большими амбициями",
    "Фейсал II (Ірак) — Король в песочнице",
    "Відкун Квіслінг (Норвегия) — Профессиональный предатель на окладе",
    "Король Леопольд III (Бельгия) — Марионетка Франции",
    "Королева Юліана (Нідерланди) — Марионетка Франции",
    "Ма Буфан (Уйгурське Царство) — Уй... что?",
    "Сукарно (Індонезія) — Крутит интриги со всеми подряд",
    "Плек Пібунсонграм (Таїланд) — Бля мужики нет тут хуястых тян",
    "Джавахарлал Неру (Індія) — Что ты тут нахуй делаешь? США в моде нет",
    "Кім Ку (Реформований Уряд Кореї) — Единый вождь реформированной Кореи, реформировал до нуля",
    "Імператор Хірохіто (Японська Острівна Держава) — Зажат на островах",
    "Ельпідіо Кіріно (Філіппіни) — Ловит пальмовые листья",
    "Роберт Мензіс (Австралія) — Пьет пиво в кенгурушатнике",
    "Сідні Голланд (Нова Зеландія) — Овцы главнее политики",
    "Атауальпа Сuasmal (Імперія Інків) — Возрожденный трон Солнца",
    "Монтесума VI (Імперія Ацтеків) — Я ж не лох",
    "Вождь Хакав-Чан (Міста-держави Мая) — Жертвоприношения и расизм белых — твой конёк",
    "Сагаморе Деканівіда (Ліга Ірокезів) — Курит трубку мира",
    "Вождь Едінсо (Конфедерація Гайда) — Нацепил перья вместо бронежилета и искренне верит, что пули отскочат",
    "Вождь Пійпот (Залізна Спілка Крі) — Закутался в шкуры",
    "Аг Мохаммед (Держава Туарегів) — Атаман пустыни",
    "Аскія Мухаммад V (Імперія Сонгаї) — Старый дед на троне",
    "Султан Алі Мірах Ханіфаре (Ефіопський Султанат) — Гордый горец",
    "Король П'єр I (Держава Конго) — Правит тремя пальмами",
    "Вільям Табмен (Ліберія) — Что ты тут нахуй делаешь? США не существует",
    "Сільванус Олімпіо (Того) — Нулевой вес",
    "Ннамді Азіківе (Нігерія) — Сам не понял, куда попал",
    "Рубен Ум Ньобе (Камерун) — Бунтарь с палкой",
    "Симеон II (Болгарія) — типа 13 лет",
    "Зеленский / Наполеон III (Франция) — я ж не лох",
    "Гарри Поллитт (Британські Комунны) — Ну комунизм это короче когда денег нет и есть где жить и у тебя пломбир тоже есть и квас с одного стаканчика пили и не болели",
    "Даг Хаммаршельд (ООН) — ты профиссионально всё фиксируешь",
    "Второе Пришествие — считай тебе нет равных",
    "Орда (Восстание мертвых в Ухани) — 67 покойо гаргамель оуджи оппы украли геньг",
]

QUOTES: List[str] = [
    "«Кто владеет малой Токмачкой, тот владеет миром» — Отто фон Бисмарк",
    "«Тот, кто ни разу не заблудился в трех соснах на окраине Житомира, не познал истинной горечи бытия» — Фридрих Ницше",
    "«Не поверишь — это Волчанск» — Аристид Бриан (о Вердене)",
    "«Какие ещё рубцы? Ты думаешь, возьмешь их и война закончится?» — Адольф Гитлер",
    "«А что мы будем делать, когда СВО закончится?» — Хайле Селассие I (о войне с Италией)",
    "«Не могу дождаться, когда наши идеологические потомки ебнут кринжовый мем с моим фото, уебут туда VHS-фильтр, прилепят черное солнце и все это в вырвиглазной цветовой гамме и зальют это на канал Пендосия» — Павел Скоропадский",
    "«Хрюкни, фанат ТСС» — Александр Македонский",
    "«Ебаная русня» — Некий мистер «П»",
    "«Римского во мне дохуя. Король Эфиопии передо мной стоит и претензии дрочит свои. Я говорю: \"bastardo, съеби нахуй\", забираю просто колонии у него и всё. Говорю: \"Viva la Italia\"» — Бенито Муссолини",
]

IDEOLOGIES: List[tuple] = [
    ("Нуклеархия", "Когда на землю придёт желтый дым — прославь Атом и Гетьмана, ведь пришла на землю нуклеархия."),
    ("Анархо-ТЦКизм", "Государства нет, законов нет, войны нет, но бусик у тебя во дворе всё равно есть, и план по мобилизации выполнять надо."),
    ("Национал-большевизм", "Национализация заводов под портретами Сталина и Лимонова, крест-накрест с партийными билетами и колючей проволокой. Летом — в комиссары, зимой — в окоп с красным флагом."),
    ("Национал-социализм", "Светлая арийская кровь сотрёт с лица земли этих ублюдков. Расовая чистота, тотальный геноцид и индустриальное уничтожение неугодных под марши из репродукторов."),
    ("Фашизм", "Всё для государства, ничего вне государства, ничего против государства. Дубинка штурмовика бьет быстрее, чем думает либерал."),
    ("Ультракапитализм (Либертарианство)", "Тотальное дерегулирование, отмена любых социальных обязательств и свободный рынок вооружений, где выживает сильнейший корпоративный картель."),
    ("Сталинизм (Марксизм-ленинизм-сталинизм)", "Железная рука, индустриализация за три года, лагеря для вредителей и расстрельные тройки как высшая мера социальной справедливости."),
    ("Монархизм (Абсолютизм)", "О добрыи молодец, да припади же ты к надеже-государю челомъ! Воля царя — законъ божий, а бунтовщиковъ вешать на сукахъ до скончания вѣка."),
    ("Троцкизм", "Перманентная революция везде, перманентный срач в ЦК и вечное изгнание с ледорубом наперевес."),
    ("Маоизм", "Тотальная мобилизация крестьянских масс, культурная чистка городского элемента и беспощадная борьба с ревизионистами всех мастей."),
    ("Анархо-коммунизм", "Свободные советы рабочих и крестьян, отсутствие тюрем и денег, немедленный расстрел любого, кто попытается надеть галстук."),
    ("Клерикальный фашизм", "Крест в одной руке, автомат в другой. Священная война против еретиков, безбожников и либералов во имя чистоты веры."),
    ("Милитаристская хунта", "Парламент разогнан, конституция отменена, комендантский час с девяти вечера. Страной управляет генералитет с контузией и сигарой в зубах."),
    ("Поздний Брежневский Застой", "Продукты по талонам, геронтократия в Политбюро, бесконечное перекладывание бумаг в министерствах и гниение великой державы под аккомпанемент похоронного марша."),
    ("Либеральный интернационализм", "Свобода рынков, права человека по методичке Госдепа, бомбардировки во имя демократии и ковровые инвестиции в сырьевые колонии."),
    ("Популистский авторитаризм", "Вождь говорит с народом с экрана телевизора, обещает колбасу по две копейки, а неугодных журналистов тихо закапывает в лесополосе."),
    ("Джихадизм / Радикальный исламизм", "Шариат на кончиках мечей, уничтожение всех неверных, разрушение светских границ и установление халифата огнем и железом."),
    ("Эко-фашизм", "Человечество — раковая опухоль планеты. Вырубить города, сократить население на 90% ради спасения биосферы и матушки-природы."),
    ("Постсоветский олигархический компрадор", "Что плохого, что я поддерживаю, поддерживал этих страусов?"),
    ("Радикальный Сионистский Этнократизм", "Избранный народ должен железной рукой утвердить свое абсолютное превосходство на Земле Обетованной, стерши любые чужеродные анклавы в пыль."),
]

# (шаблон, вес)
ROLL_PLUS = [
    ("{u} ТЦК Десна Токмачка мобает +{n} на фронт!", 35),
    ("{u} рабовладельческий строй, неофеодализм с элементами киберпанка, отсутствие налогов, женская военная повинность — +{n} дивизий!", 35),
    ("{u} тільки наші так можуть)))) шкода, що далеко не всі зрозуміють хто тримає цей район))) дійсно бавовна)))))) не так багато в наш час, хто знає як збити дрон банкою помідорів — +{n} дивизий!", 30),
]
ROLL_MINUS = [
    ("{u} ГОЙ ДЕТЕКТЕД! Минус {n} дивизий.", 35),
    ("{u} о НЕТ, ваши дивизии поймал окулист! Минус {n} дивизий.", 35),
    ("{u} МИНДИЧ УЕБАЛ по распологе ваших бедолаг! Минус {n} дивизий.", 30),
]


# ============================================================================
# ХЕЛПЕРЫ
# ============================================================================

def mention(user: User) -> str:
    """@username, если он есть, иначе кликабельное имя."""
    if user.username:
        return f"@{html.escape(user.username)}"
    return f'<a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a>'


def plain_name(user: User) -> str:
    return f"@{user.username}" if user.username else user.full_name


def weighted_choice(options):
    templates = [o[0] for o in options]
    weights = [o[1] for o in options]
    return random.choices(templates, weights=weights, k=1)[0]


# ============================================================================
# ХРАНИЛИЩЕ БАЛАНСОВ
# ============================================================================

_data_lock = asyncio.Lock()
_data: Dict[str, Dict[str, dict]] = {}


def _load() -> None:
    global _data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                _data = json.load(f)
        except Exception:
            logging.exception("Не удалось прочитать %s, начинаю с пустой базы", DATA_FILE)
            _data = {}


def _save() -> None:
    tmp = DATA_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(_data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


async def change_balance(chat_id: int, user: User, delta: int) -> int:
    async with _data_lock:
        chat = _data.setdefault(str(chat_id), {})
        rec = chat.setdefault(str(user.id), {"name": plain_name(user), "balance": 0})
        rec["name"] = plain_name(user)
        rec["balance"] += delta
        _save()
        return rec["balance"]


# ============================================================================
# /who /quote /ideology
# ============================================================================

@router.message(Command("who"))
async def cmd_who(message: Message):
    await message.reply("Ты — " + html.escape(random.choice(WHO_LIST)))


@router.message(Command("quote"))
async def cmd_quote(message: Message):
    await message.reply(html.escape(random.choice(QUOTES)))


@router.message(Command("ideology"))
async def cmd_ideology(message: Message):
    name, desc = random.choice(IDEOLOGIES)
    await message.reply(f"<b>{html.escape(name)}</b>: {html.escape(desc)}")


# ============================================================================
# /roll /toproll
# ============================================================================

@router.message(Command("roll"), GROUP_ONLY)
async def cmd_roll(message: Message):
    user = message.from_user
    amount = random.randint(1, 15)
    if random.random() < 0.5:
        template = weighted_choice(ROLL_PLUS)
        delta = amount
    else:
        template = weighted_choice(ROLL_MINUS)
        delta = -amount
    await change_balance(message.chat.id, user, delta)
    # шаблоны содержат '<'/'>' нигде, но экранируем на всякий случай до подстановки упоминания
    text = html.escape(template).replace("{u}", mention(user)).replace("{n}", str(amount))
    await message.answer(text)


@router.message(Command("toproll"), GROUP_ONLY)
async def cmd_toproll(message: Message):
    async with _data_lock:
        chat = _data.get(str(message.chat.id), {})
        rows = sorted(chat.values(), key=lambda r: r["balance"], reverse=True)[:10]
    if not rows:
        await message.reply("Пока никто не ролил.")
        return
    lines = ["<b>Таблица лидеров по дивизиям:</b>"]
    for i, r in enumerate(rows, 1):
        lines.append(f"{i}. {html.escape(r['name'])} — {r['balance']}")
    await message.answer("\n".join(lines))


# ============================================================================
# /duel (крестики-нолики 3x3)
# ============================================================================

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]
SYMBOLS = {"X": "❌", "O": "⭕", "": "▫️"}

# game_id -> состояние
GAMES: Dict[str, dict] = {}


def check_winner(board: List[str]) -> Optional[str]:
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


def board_kb(gid: str, board: List[str], finished: bool = False) -> InlineKeyboardMarkup:
    rows = []
    for r in range(3):
        row = []
        for c in range(3):
            i = r * 3 + c
            cb = "duel:noop" if finished else f"duel:mv:{gid}:{i}"
            row.append(InlineKeyboardButton(text=SYMBOLS[board[i]], callback_data=cb))
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)


def turn_text(game: dict) -> str:
    p = game["p1"] if game["turn"] == "X" else game["p2"]
    return f"Дуэль: {game['p1']['m']} ❌ vs {game['p2']['m']} ⭕\nХод: {p['m']} {SYMBOLS[game['turn']]}"


@router.message(Command("duel"), GROUP_ONLY)
async def cmd_duel(message: Message):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply("Ответь командой /duel на сообщение того, кого вызываешь.")
        return
    challenger = message.from_user
    opponent = message.reply_to_message.from_user
    if opponent.is_bot:
        await message.reply("С ботами не дуэлимся.")
        return
    if opponent.id == challenger.id:
        await message.reply("Сам с собой не дуэлимся.")
        return

    gid = uuid.uuid4().hex[:8]
    GAMES[gid] = {
        "chat_id": message.chat.id,
        "p1": {"id": challenger.id, "m": mention(challenger)},
        "p2": {"id": opponent.id, "m": mention(opponent)},
        "board": [""] * 9,
        "turn": "X",
        "accepted": False,
    }
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Принять вызов", callback_data=f"duel:acc:{gid}")
    ]])
    await message.answer(
        f"{mention(challenger)} вызывает {mention(opponent)} на дуэль!",
        reply_markup=kb,
    )


@router.callback_query(F.data == "duel:noop")
async def cb_noop(call: CallbackQuery):
    await call.answer()


@router.callback_query(F.data.startswith("duel:acc:"))
async def cb_accept(call: CallbackQuery):
    gid = call.data.split(":")[2]
    game = GAMES.get(gid)
    if not game:
        await call.answer("Эта дуэль уже неактуальна.", show_alert=True)
        return
    if call.from_user.id != game["p2"]["id"]:
        await call.answer("Этот вызов адресован не тебе.", show_alert=True)
        return
    if game["accepted"]:
        await call.answer()
        return
    game["accepted"] = True
    await call.message.edit_text(turn_text(game), reply_markup=board_kb(gid, game["board"]))
    await call.answer()


@router.callback_query(F.data.startswith("duel:mv:"))
async def cb_move(call: CallbackQuery):
    _, _, gid, idx_s = call.data.split(":")
    idx = int(idx_s)
    game = GAMES.get(gid)
    if not game or not game["accepted"]:
        await call.answer("Эта дуэль уже неактуальна.", show_alert=True)
        return

    uid = call.from_user.id
    if uid not in (game["p1"]["id"], game["p2"]["id"]):
        await call.answer("Это не твоя дуэль.", show_alert=True)
        return

    mark = game["turn"]
    current = game["p1"] if mark == "X" else game["p2"]
    if uid != current["id"]:
        await call.answer("Сейчас не твой ход.", show_alert=True)
        return
    if game["board"][idx]:
        await call.answer("Клетка занята.", show_alert=True)
        return

    game["board"][idx] = mark
    winner = check_winner(game["board"])

    if winner:
        win_p = game["p1"] if winner == "X" else game["p2"]
        lose_p = game["p2"] if winner == "X" else game["p1"]
        GAMES.pop(gid, None)
        await call.message.edit_text(
            f"{win_p['m']} выебал {lose_p['m']}",
            reply_markup=board_kb(gid, game["board"], finished=True),
        )
    elif all(game["board"]):
        GAMES.pop(gid, None)
        await call.message.edit_text(
            "отсосите,ничья",
            reply_markup=board_kb(gid, game["board"], finished=True),
        )
    else:
        game["turn"] = "O" if mark == "X" else "X"
        await call.message.edit_text(turn_text(game), reply_markup=board_kb(gid, game["board"]))
    await call.answer()


# ============================================================================
# /mute (только админы)
# ============================================================================

MAX_MUTE_MINUTES = 366 * 24 * 60  # больше — Telegram считает мут вечным


@router.message(Command("mute"), GROUP_ONLY)
async def cmd_mute(message: Message, command: CommandObject, bot: Bot):
    member = await bot.get_chat_member(message.chat.id, message.from_user.id)
    if member.status not in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR):
        await message.reply("Команда только для админов.")
        return

    if not message.reply_to_message or not message.reply_to_message.from_user:
        await message.reply("Используй реплаем: /mute [минуты], например /mute 180")
        return

    arg = (command.args or "").strip().split()
    if not arg or not arg[0].isdigit() or int(arg[0]) <= 0:
        await message.reply("Укажи время в минутах: /mute 180")
        return
    minutes = min(int(arg[0]), MAX_MUTE_MINUTES)

    target = message.reply_to_message.from_user
    until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    try:
        await bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target.id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_audios=False,
                can_send_documents=False,
                can_send_photos=False,
                can_send_videos=False,
                can_send_video_notes=False,
                can_send_voice_notes=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
            ),
            until_date=until,
        )
    except Exception as e:
        logging.warning("mute failed: %s", e)
        await message.reply("Не удалось замутить (у бота нет прав или цель — админ).")
        return

    await message.answer(f"{mention(target)} получает мут на {minutes}")


# ============================================================================
# ЗАПУСК
# ============================================================================

async def main():
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN:
        raise SystemExit("Задай переменную окружения BOT_TOKEN")
    _load()
    bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
