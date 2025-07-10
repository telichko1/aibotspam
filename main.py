import asyncio
import random
import time
import aiohttp
import uvicorn
import os
import logging
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ChannelPosterBot")

BOT_TOKEN = "7783817301:AAFxS4fXUTe9Q34NrP8110yvzZeBNIMmui4"
CHANNELS = [
    "@deepseek_openai_claude",
    "@gpt_deepseek_claude",
    "@gptdalle3",
    "@gptchatdalle",
    "@gpt_deepseek_openai",
    "@gemini_stable_diffusion"
]

# Расширенные библиотеки хештегов
NEURAL_TAGS = [
    # Глобальные AI теги
    "#AI", "#ArtificialIntelligence", "#MachineLearning", "#DeepLearning", 
    "#NeuralNetwork", "#AIGenerated", "#AIArt", "#AIVision", "#AIMusic", 
    "#AIText", "#AIChat", "#AIModel", "#AIFuture", "#DeepFake", "#GANArt", 
    "#LLM", "#AIVideo", "#AIVoice", "#GenerativeAI", "#AIDesign",
    
    # Популярные модели
    "#ChatGPT", "#GPT4", "#GPT5", "#Midjourney", "#DALLE3", "#StableDiffusion", 
    "#Gemini", "#Claude", "#OpenAI", "#DeepSeek", "#GeminiPro", "#Anthropic",
    
    # Русскоязычные теги
    "#ИИ", "#ИскусственныйИнтеллект", "#Нейросети", "#Нейросеть", "#ЧатГПТ", 
    "#Миджорни", "#ГенеративныйИИ", "#НейроХудожник", "#НейроГрафика", 
    "#НейроТекст", "#НейроМедиа", "#ИИБудущее", "#ГПТ", "#ИИПомощник",
    "#ГлубокоеОбучение", "#НейроДизайн", "#НейроКреатив", "#ИИАрт"
]

F4F_TAGS = [
    # Глобальные теги
    "#F4F", "#FollowForFollow", "#FollowBack", "#LikeForLike", "#Sub4Sub",
    "#FollowTrain", "#FollowMe", "#FollowHer", "#FollowHim", "#FollowAll",
    "#Followers", "#FollowUs", "#Follower", "#F4FInstagram", "#F4FLike",
    "#F4FAlways", "#F4FCommunity", "#Follow4Follow", "#FollowForFollowBack",
    "#Like4Like", "#Like4Likes", "#Sub4Subs", "#Follow4Follows",
    
    # Русскоязычные теги
    "#ВзаимныйФолловинг", "#ПодпискаЗаПодписку", "#ЛайкЗаЛайк", "#Ф4Ф", 
    "#Взаимоподписка", "#ПодпишисьИяПодпишусь", "#ВзаимныеПодписки", 
    "#ПодпискаНаПодписку", "#Подпишемся", "#Фолловинг", "#ПодпишисьОтмечай", 
    "#ПодпишисьНеПожалеешь", "#ПодпискаВзамен", "#ПодпишимсяВзаимно", 
    "#ПодпишисьИяВерну", "#ПодпишисьАктивный", "#ПодпишисьБудьДругом",
    "#Взаимно", "#Подписка", "#Лайки", "#Подписчики"
]

ENTERTAINMENT_TAGS = [
    # Глобальные теги
    "#Fun", "#Memes", "#Humor", "#Entertainment", "#Laugh", "#Joke", 
    "#Comedy", "#Viral", "#Trending", "#Daily", "#LOL", "#Hilarious", 
    "#FunnyVideos", "#FunnyPics", "#FunnyPosts", "#Jokes", "#DankMemes",
    "#MemesDaily", "#Entertaining", "#Entertain", "#Trend", "#Trends",
    "#ViralPost", "#ViralMemes", "#ViralVideo", "#ViralContent",
    "#DailyMemes", "#DailyFun", "#DailyJokes", "#LaughOutLoud", "#LMAO",
    
    # Русскоязычные теги
    "#Развлечения", "#Юмор", "#Мемы", "#Смешно", "#Приколы", "#Ржака", 
    "#Веселье", "#Смех", "#Угар", "#МемыДня", "#Тренды", "#Вирус", 
    "#Вайнеры", "#СмешныеВидео", "#СмешныеКартинки", "#Прикол", 
    "#Анекдоты", "#Залипательно", "#Угарно", "#Юморок", "#Отдохни", 
    "#Посмеемся", "#Улыбнись", "#Позитив", "#СмешныеИстории",
    "#ТикТок", "#Реакции", "#Пранки", "#КВН", "#Стендап"
]

# Создаем экземпляр бота
bot = Bot(token=BOT_TOKEN)

def generate_hashtags():
    """Генерирует уникальный набор из 10 хештегов с максимальным разбросом"""
    # Отбираем хештеги с разной популярностью
    neural_tags = (
        random.sample(NEURAL_TAGS[:15], 2) +  # Самые популярные
        random.sample(NEURAL_TAGS[15:30], 2) +  # Средняя популярность
        random.sample(NEURAL_TAGS[30:], 1)  # Менее популярные
    )
    
    f4f_tags = (
        random.sample(F4F_TAGS[:10], 1) +  # Самые популярные
        random.sample(F4F_TAGS[10:20], 1) +  # Средняя популярность
        random.sample(F4F_TAGS[20:], 1)  # Менее популярные
    )
    
    entertainment_tags = (
        random.sample(ENTERTAINMENT_TAGS[:15], 2) +  # Самые популярные
        random.sample(ENTERTAINMENT_TAGS[15:30], 1) +  # Средняя популярность
        random.sample(ENTERTAINMENT_TAGS[30:], 1)  # Менее популярные
    )
    
    # Перемешиваем все теги
    all_tags = neural_tags + f4f_tags + entertainment_tags
    random.shuffle(all_tags)
    
    return ' '.join(all_tags[:10])  # Возвращаем 10 случайных тегов

def create_keyboard():
    """Создает кнопку под постом"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🚀 Перейти к боту ➡️", url="https://t.me/NeuroAlliance_bot")
    return keyboard.as_markup()

def generate_post():
    """Генерирует пост с улучшенным дизайном"""
    bot_link = "https://t.me/NeuroAlliance_bot"
    
    return (
        f"<b>✨ БЕСПЛАТНЫЙ ДОСТУП К МОЩНЫМ НЕЙРОСЕТЯМ!</b>\n\n"
        f"⚡️ <b>ChatGPT</b> для текста и <b>Midjourney</b> для изображений\n"
        f"уже доступны прямо в Telegram!\n\n"
        f"🔥 <b>Преимущества:</b>\n"
        f"• <b>100% бесплатно</b> - никаких скрытых платежей\n"
        f"• <b>Без регистрации</b> - начинайте сразу\n"
        f"• <b>Работает в Telegram</b> - не нужно скачивать приложения\n"
        f"• <b>Максимально просто</b> - интуитивно понятный интерфейс\n\n"
        f"🎨 Создавайте тексты, изображения, идеи - всё в одном месте!\n\n"
        f"🚀 <b>Начните прямо сейчас:</b>\n"
        f"• <a href='{bot_link}'>ChatGPT</a> - генерация текстов\n"
        f"• <a href='{bot_link}'>Midjourney</a> - создание изображений\n\n"
        f"⚡️⚡️⚡️ <b><a href='{bot_link}'>ДОСТУП КО ВСЕМ НЕЙРОСЕТЯМ</a></b> ⚡️⚡️⚡️\n\n"
        f"<i>#{random.choice(['актуально', 'новинка', 'тренд', 'горячее'])} "
        f"{generate_hashtags()}</i>\n\n"
        f"<i>Нажмите кнопку ниже, чтобы начать 👇</i>"
    )

async def post_to_channels():
    """Отправляет посты во все каналы"""
    keyboard = create_keyboard()
    
    for channel in CHANNELS:
        try:
            post_text = generate_post()
            await bot.send_message(
                chat_id=channel,
                text=post_text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
                parse_mode="HTML"
            )
            logger.info(f"✅ Пост успешно отправлен в {channel}")
            await asyncio.sleep(1)  # Задержка между отправками
        except Exception as e:
            logger.error(f"❌ Ошибка при отправке в {channel}: {str(e)}")

async def scheduler():
    """Планировщик отправки постов каждые 3 минуты"""
    while True:
        try:
            await post_to_channels()
        except Exception as e:
            logger.error(f"❌ Ошибка в планировщике: {str(e)}")
        
        await asyncio.sleep(60)  # 3 минуты = 180 секунд

async def self_pinger():
    """Регулярные ping-запросы для предотвращения сна сервиса"""
    RENDER_APP_URL = os.getenv("RENDER_APP_URL", "https://aibotspam.onrender.com/")
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(RENDER_APP_URL, timeout=10) as response:
                    logger.info(f"🔄 Self-ping status: {response.status}")
        except Exception as e:
            logger.error(f"❌ Self-ping failed: {str(e)}")
        await asyncio.sleep(300)  # 5 минут

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Запускаем фоновые задачи при старте
    asyncio.create_task(scheduler())
    asyncio.create_task(self_pinger())
    
    logger.info("🚀 Приложение запущено")
    yield
    
    # Очистка при завершении
    logger.info("🛑 Приложение останавливается...")
    await bot.session.close()
    logger.info("✅ Сессия бота закрыта")

# Создаем FastAPI приложение
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def health_check():
    """Эндпоинт для проверки работоспособности"""
    return {
        "status": "active",
        "service": "Telegram Channel Poster",
        "version": "1.0",
        "channels": CHANNELS,
        "interval": "3 minutes"
    }

@app.get("/ping")
async def ping():
    """Эндпоинт для пинга"""
    return {"status": "pong"}

if __name__ == "__main__":
    # Настройки для запуска на Render.com
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Запуск сервера на {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=1,
        loop="asyncio",
        timeout_keep_alive=60
    )
