from dotenv import load_dotenv
import os
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Update,
    ReplyKeyboardRemove,
    message,
    replymarkup)
from typing import Dict
import logging

# logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# dotenv
load_dotenv()

# constants
TOKEN = os.environ.get("TOKEN")
CHANNEL = os.environ.get("CHANNEL")
AD, MENU = range(2)

# keyboards
menu_keyboard = ReplyKeyboardMarkup(
    [
        ['🦉 Senioridade'],
        ['🤝 Contrato'],
        ['💱 Moeda'],
        ['💵 Salário'],
        ['👥 Soft skills'],
        ['⚙️ Hard skills'],
        ['📞 Contato'],
        ['✅ Pronto'],
    ], one_time_keyboard=True
)

expertise_keyboard = ReplyKeyboardMarkup(
    [
        ['Estágio'],
        ['Trainee'],
        ['Júnior'],
        ['Pleno'],
        ['Sênior'],
    ], one_time_keyboard=True
)

work_type_keyboard = ReplyKeyboardMarkup(
    [
        ['CLT'],
        ['PJ'],
        ['CLT ou PJ'],
    ], one_time_keyboard=True
)

coin_keyboard = ReplyKeyboardMarkup(
    [
        ['BRL'],
        ['USD'],
        ['EUR'],
    ], one_time_keyboard=True
)

# variables
info_from = seniority = contract = currency = soft_skills = tech_skills = contact = ''
salary = 0


def reset():
    global info_from, seniority, contract, salary, currency, soft_skills, tech_skills, contact

    info_from = seniority = contract = currency = soft_skills = tech_skills = contact = ''
    salary = 0


def home_screen(update: Update, context: CallbackContext) -> int:
    global chat_id
    reset()

    user = update.message.chat.first_name
    chat_id = update.message.chat_id

    update.message.reply_text(f"Saudações, {user}!\nSou o responsável pelo @ProgrameirosJobs.\n\nPara divulgar seu job, navegue usando os botões abaixo.\n\nQuando finalizar clique em \"✅ Pronto\".",
                              reply_markup=menu_keyboard
                              )

    return AD


def data_session():

    return f"\n🦉 {seniority}\n🤝 {contract}\n💱 {currency}\n💵 {salary}\n👥 {soft_skills}\n⚙️ {tech_skills}\n📞 {contact}"


def received_information(update: Update, context: CallbackContext) -> int:
    global info_from, seniority, contract, currency, salary, soft_skills, tech_skills, contact

    if(info_from == 'expertise'):
        seniority = update.message.text

    elif(info_from == 'work_type'):
        contract = update.message.text

    elif(info_from == 'wage'):
        salary = update.message.text

    elif(info_from == 'coin'):
        currency = update.message.text

    elif(info_from == 'interpersonal_skills'):
        soft_skills = update.message.text

    elif(info_from == 'hard_skills'):
        tech_skills = update.message.text

    elif(info_from == 'meet'):
        contact = update.message.text

    update.message.reply_text(
        f"Seu job até agora:\n{data_session()}",
        reply_markup=menu_keyboard,
    )

    return AD


def expertise(update: Update, _: CallbackContext) -> int:
    global info_from

    info_from = 'expertise'

    update.message.reply_text(
        "Qual o nível de senioridade exigido na vaga?", reply_markup=expertise_keyboard)

    return MENU


def work_type(update: Update, _: CallbackContext) -> int:
    global info_from

    info_from = 'work_type'

    update.message.reply_text(
        "Qual a forma de contrato?", reply_markup=work_type_keyboard)

    return MENU


def coin(update: Update, _: CallbackContext) -> int:
    global info_from

    info_from = 'coin'

    update.message.reply_text(
        "Em qual moeda será realizado o pagamento?", reply_markup=coin_keyboard)

    return MENU


def wage(update: Update, _: CallbackContext) -> int:
    global info_from

    info_from = 'wage'

    update.message.reply_text(
        "Envie o valor do salário da vaga (somente números).")

    return MENU


def interpersonal_skills(update: Update, _: CallbackContext) -> int:
    global info_from

    info_from = 'interpersonal_skills'

    update.message.reply_text(
        "Envie a lista de soft skills requisitadas neste job.")

    return MENU


def hard_skills(update: Update, _: CallbackContext) -> int:
    global info_from

    info_from = 'hard_skills'

    update.message.reply_text(
        "Envie a lista de hard skills requisitadas neste job.")

    return MENU


def meet(update: Update, _: CallbackContext) -> int:
    global info_from

    info_from = 'meet'

    update.message.reply_text(
        "Informe as formas que o candidato poderá entrar em contato.")

    return MENU


def done(update: Update, context: CallbackContext) -> int:

    context.bot.send_message(chat_id=CHANNEL,
                             text=f"{data_session()}",
                             reply_markup=InlineKeyboardMarkup([
                                 [InlineKeyboardButton(
                                     text='Divulgue seu job', url='https://t.me/ProgrameirosJobsRobot')],
                             ])
                             )

    update.message.reply_text(
        'Seu job foi publicado!\n\nPara reiniciar, envie /start',
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(
            ['start', 'restart'], home_screen)],
        states={
            MENU: [
                MessageHandler(
                    Filters.text & ~(Filters.command |
                                     Filters.regex('^Pronto$')),
                    received_information,
                )
            ],
            AD: [
                MessageHandler(
                    Filters.regex(
                        '^(✅ Pronto)$'), done,
                ),
                MessageHandler(
                    Filters.regex(
                        '^(🦉 Senioridade)$'), expertise,
                ),
                MessageHandler(
                    Filters.regex('^(🤝 Contrato)$'), work_type
                ),
                MessageHandler(
                    Filters.regex('^(💱 Moeda)$'), coin
                ),
                MessageHandler(
                    Filters.regex('^(💵 Salário)$'), wage
                ),
                MessageHandler(
                    Filters.regex('^(👥 Soft skills)$'), interpersonal_skills
                ),
                MessageHandler(
                    Filters.regex('^(⚙️ Hard skills)$'), hard_skills
                ),
                MessageHandler(
                    Filters.regex('^(📞 Contato)$'), meet
                )
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('/start'), home_screen)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
