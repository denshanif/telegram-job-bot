import os
import logging
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler
import requests
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# URL of the website
url = "https://daesang.id/in/career/en"

# Telegram Bot API details
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

def get_fresh_graduate_content():
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        fresh_graduate_div = soup.find('div', {'id': 'tab_sec2', 'class': 'tab-pane fade in'})
        
        if fresh_graduate_div:
            accordion_div = fresh_graduate_div.find('div', {'id': 'accordion-3', 'class': 'panel-group accordion-style3'})
            
            if accordion_div:
                job_panels = accordion_div.find_all('div', class_='panel panel-default')
                
                if job_panels:
                    content = []
                    for panel in job_panels:
                        job_title = panel.find('span', class_='text-white')
                        job_description = panel.find('div', class_='panel-body')
                        
                        if job_title and job_description:
                            title = job_title.text.strip()
                            description = job_description.get_text(separator='\n', strip=True)
                            
                            job_info = f"Job Title: {title}\n\nDescription:\n{description}\n\n{'='*50}\n"
                            content.append(job_info)
                    
                    return content if content else ["No job listings found in the Fresh Graduate section."]
                else:
                    return ["No job panels found in the Fresh Graduate section."]
            else:
                return ["Accordion not found in Fresh Graduate section."]
        else:
            return ["Fresh Graduate section not found."]
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return [f"An error occurred: {str(e)}"]

def start(update: Update, context):
    update.message.reply_text("Welcome! Use /check to check for current job listings.")

def check(update: Update, context):
    logger.info("Manual check requested via /check command")
    content = get_fresh_graduate_content()
    if content and isinstance(content[0], str) and not content[0].startswith("No job"):
        update.message.reply_text("Here are the current Fresh Graduate job listings:")
        for job in content:
            update.message.reply_text(job, parse_mode='HTML')
    else:
        update.message.reply_text("No job listings found in the Fresh Graduate section.")

def setup_dispatcher(dispatcher):
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("check", check))
    return dispatcher

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dispatcher = setup_dispatcher(Dispatcher(bot, None, use_context=True))

def telegram_bot(request):
    if request.method != "POST":
        return "OK"
    
    update = Update.de_json(request.get_json(force=True), bot)
    
    dispatcher.process_update(update)
    
    return "OK"
