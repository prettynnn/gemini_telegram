import asyncio
import logging
import aiosqlite

# IMPORTANT : To record your chat history,
# you need to create a file called example data.db (or whatever name you like) 

from google import genai
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
logging.basicConfig(level=logging.INFO, format="%(message)s")


# register the important data
log = logging.info
api_key = 'token'
gemini_api_key = 'api token'
client = genai.Client(api_key=gemini_api_key)

log(f'Database is connected!')
log(f'Cursor created!')

dp = Dispatcher()
bot = Bot(token=api_key)
model = "gemini-2.0-flash"
chat = client.chats.create(model='gemini-2.0-flash')


class Data():
    def __init__(self, connect='', cursor=''):
        self.connect = connect
        self.cursor = cursor
        
    async def db(self):
        self.connect = await aiosqlite.connect('data.db')
        self.cursor = await self.connect.cursor()
        
    async def create_table(self):
        await self.db()
        await self.cursor.execute('CREATE TABLE IF NOT EXISTS DATA (user TEXT, requests TEXT, response TEXT)')
        await self.connect.commit()
        
    # save all messages to database
    async def save_message(self, user_id, requests, response):
        await self.cursor.execute('INSERT INTO DATA (user, requests, response) VALUES (?, ?, ?)', (user_id, requests, response))
        return await self.connect.commit()

    # function
    async def require_message_data(self, user_id):
        await self.db()
        await self.cursor.execute('SELECT * FROM DATA WHERE user = ?', (user_id,))
        return await self.cursor.fetchone()
        
# started bot command
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer('Hey! My name is Laura! You ready learning English?')
    
# create chat command with history (chats)
@dp.message(Command("create_chat"))
async def create_handler(message: types.Message):
        try:
            user_id = message.from_user.id

        except aiosqlite.Error as e:
            log(f'{e}')
    
        search = await dat.require_message_data(user_id)
        
        try:
            if search is None:
                await dat.cursor.execute('INSERT OR IGNORE INTO DATA (user, requests, response) VALUES (?, ?, ?)', (user_id, 'requests', 'response'))
                await message.reply("Succesfully chat created!")
            
                await dat.save_message(user_id, 'requests', 'response')
                return
        
            else:
                await message.reply("You have chat, cannot create new!")
                
        except aiosqlite.Error as e:
            log(f'error  - {e}')
        

# here we speaking to bot, and he responds to any of our commands
@dp.message()
async def gemini_handler(message: types.Message):
        user_id = message.from_user.id
        
        try:
            search = await dat.require_message_data(user_id)
        
            if search is None:
                await message.reply('You must create chat: /create_chat')
                return
            
            user_message = message.text
            requests = chat.send_message(user_message)
            response = requests.text
            response = response.replace('**', '')
            
            await dat.save_message(user_id, 'requests', 'response')
            
            if len(response) > 4096:
                for x in range(0, len(response), 4096):
                    await message.answer(
                    response[x:x+4096],
                    ),
            
            else:
                await message.reply(response)
                
        except aiosqlite.Error as e:
            log(f'error - {e}')

# bot listening to all requests
async def main():
    await dat.create_table()
    await dp.start_polling(bot)
    
dat = Data()

if __name__ == "__main__":
    asyncio.run(main())
