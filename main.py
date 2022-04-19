import telegram.ext
from telegram.ext import *
from telegram import ReplyKeyboardMarkup, Bot, ReplyKeyboardRemove
from data import db_session
from data.mods import Mods
from data.userfols import UserFols
import sqlalchemy
from emoji import emojize
import datetime

EMOJIS = ['🙌', '😃']


def start(update, context):
    smile = emojize(EMOJIS[1])
    reply_keyboard = [['/find', '/add'],
                      ['/help', '/new'],
                      ['/about_user', '/follow_car']]
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)

    update.message.reply_text(
        f"Hello, {update.message.from_user.first_name}! Let's start searching for new mods!{smile}\n"
        f"if you want to get more information about this bot use /about command",
        reply_markup=markup)


def find(update, context):
    update.message.reply_text("What car brand would you like to see?",
                              reply_markup=ReplyKeyboardRemove())
    return 'brand'


def found_brand(update, context):
    if update.message.text == 'back':
        return ConversationHandler.END

    context.user_data['car_brand'] = update.message.text

    update.message.reply_text("What car model would you like to see?\n"
                              'Want to see all models? - print "-"')
    return 'model'


def found_model(update, context):
    if update.message.text == 'back':
        return 'brand'

    context.user_data['model'] = update.message.text

    reply_keyboard = [['by year', 'by date of creation'],
                      ['by model (if all are chosen)']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text("Please choose in what way should we sort found mods",
                              reply_markup=markup)
    return 'sort'


def sort(update, context):
    if update.message.text == 'back':
        return 'model'

    way_to_sort = update.message.text

    db_session.global_init("db/mods.db")
    db_sess = db_session.create_session()
    if context.user_data['model'] == '-':
        context.user_data['model'] = ''
        mods_for_now = db_sess.query(Mods).filter(Mods.brand.like(context.user_data['car_brand'].lower()))
    else:
        mods_for_now = db_sess.query(Mods).filter(Mods.brand.like(context.user_data['car_brand'].lower()),
                                                  Mods.model.like(context.user_data['model']))
    update.message.reply_text(
        f"Here are {context.user_data['car_brand']} {context.user_data['model']} mods which we were able to find:",
        reply_markup=ReplyKeyboardRemove())

    if way_to_sort == 'by year':
        mods_for_now = sorted(mods_for_now, key=lambda x: x.year)
    elif way_to_sort == 'by date of creation':
        mods_for_now = sorted(mods_for_now, key=lambda x: x.created_date)
    elif way_to_sort == 'by model (if all are chosen)':
        mods_for_now = sorted(mods_for_now, key=lambda x: x.model)

    for car in mods_for_now:
        context.bot.sendPhoto(chat_id=update.message.chat_id, photo=open(f'./previews/{car.image}.jpg', 'rb'),
                              caption=f"{car.brand.capitalize()} {car.model.capitalize()} {car.year}\n"
                                      f"{car.description}\n"
                                      f"author: {car.author}\n"
                                      f"download link: {car.link}\n"
                                      f"created on: {car.created_date.date()}")
    context.user_data.clear()
    return ConversationHandler.END


def stop_finding(update, context):
    context.user_data.clear()
    update.message.reply_text("Hope you found something in our bot!", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def add(update, context):
    update.message.reply_text(
        "Please answer some questions about your mod to help other people find it easier!\n"
        "Firstly, please let me know what brand is your car", reply_markup=ReplyKeyboardRemove())
    return 'brand'


def brand(update, context):
    if update.message.text == 'back':
        return ConversationHandler.END
    context.user_data['brand'] = update.message.text.lower()
    update.message.reply_text(
        "What is the model of your car?")
    return 'model'


def car_model(update, context):
    if update.message.text == 'back':
        return 'brand'

    context.user_data['model'] = update.message.text.lower()
    update.message.reply_text(
        "What year your car is?")
    return 'year'


def car_year(update, context):
    if update.message.text == 'back':
        return 'model'

    context.user_data['year'] = int(update.message.text)
    update.message.reply_text(
        "Give a brief description of your mod")
    return 'descript'


def description(update, context):
    if update.message.text == 'back':
        return 'year'

    context.user_data['description'] = update.message.text
    update.message.reply_text(
        "Please send a preview photo of your car")
    return "image"


def image(update, context):
    if update.message.text == 'back':
        return 'descript'

    context.user_data['file'] = context.bot.getFile(update.message.photo[-1].file_id)
    context.user_data['image'] = update.message.photo[-1].file_id
    update.message.reply_text(f"Send a link to author of the mod")
    return 'author'


def author(update, context):
    if update.message.text == 'back':
        return 'image'

    context.user_data['author'] = update.message.text
    update.message.reply_text(f"Final step! Send link to download your mod!")
    return 'link'


def link(update, context):
    context.user_data['link'] = update.message.text

    if update.message.text == 'back':
        return 'author'

    reply_keyboard = [['Yes', 'No']]
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 one_time_keyboard=False,
                                 resize_keyboard=True)
    update.message.reply_text(
        "Are you sure you want to post it?", reply_markup=markup)
    return 'confirm'


def stop_adding(update, context):
    context.user_data.clear()
    return ConversationHandler.END


def confirmation(update, context):
    reply_keyboard = [['/find', '/add'],
                      ['/help', '/new'],
                      ['/about_user', '/follow_to_car']]
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)

    if update.message.text == 'back':
        return 'link'

    if update.message.text.lower() in ['yes', 'sure', 'y', 'yeah']:
        with open('brands.txt', 'r') as file:
            brands_available = file.read().split(', ')

        if context.user_data['brand'] in brands_available:
            checked = True
        else:
            checked = False
        if checked:
            db_session.global_init("db/mods.db")
            mod = Mods()
            context.user_data['file'].download(f'./previews/{context.user_data["image"]}.jpg')
            mod.description = context.user_data['description']
            mod.link = context.user_data['link']
            mod.brand = context.user_data['brand']
            mod.year = context.user_data['year']
            mod.model = context.user_data['model']
            mod.image = context.user_data['image']
            mod.author = context.user_data['author']
            db_sess = db_session.create_session()
            db_sess.add(mod)
            db_sess.commit()

            update.message.reply_text(
                "Thanks for sharing your mod!\n"
                "Looking forward to get new mod from you again!",
                reply_markup=ReplyKeyboardRemove())
        else:
            update.message.reply_text(
                "Try to check if you wrote car brand correctly...",
                reply_markup=markup)

        context.user_data.clear()
        return ConversationHandler.END
    else:
        update.message.reply_text(
            "Hope to get another mod from you)",
            reply_markup=markup)
        context.user_data.clear()

        return ConversationHandler.END


def helpfunc(update, context):
    update.message.reply_text("Commands to control the bot:\n"
                              "\n"
                              "/add - add your own mod by answering some questions\n"
                              "/about - a brief description of this bot"
                              "/find - after choosing a brand and a model of a car you want to find "
                              "you get a list of mods available\n"
                              "/new - shows 10 last added mods\n"
                              "/follow_car - enable notifications when new mod of a subscribed car appears\n"
                              "/unfollow - disable notifications on a car you're subscribed to\n"
                              "/about_user - get info about your subscriptions"
                              'to make a step back just write "back" if you are in commands like /follow_car,'
                              ' /find or /add')


def start_follow(update, context):
    update.message.reply_text(f"Send brand of a car, which you want to follow")
    return 'brand'


def follow_brand(update, context):
    context.user_data['brand'] = update.message.text
    update.message.reply_text(f"Now send model of a car, which you want to follow")
    return 'model'


def follow_model(update, context: telegram.ext.CallbackContext):
    user = UserFols()
    user.user_id = update.message.chat_id
    user.brand = context.user_data['brand'].lower()
    user.model = update.message.text.lower()

    db_session.global_init("db/mods.db")
    db_sess = db_session.create_session()
    db_sess.add(user)
    db_sess.commit()

    if update.message.text == 'back':
        return 'brand'

    reply_keyboard = [['/find', '/add'],
                      ['/help', '/new'],
                      ['/about_user', '/follow_to_car'],
                      ['/unfollow']]
    markup = ReplyKeyboardMarkup(reply_keyboard,
                                 one_time_keyboard=True,
                                 resize_keyboard=True)

    update.message.reply_text(f"Now you follow {context.user_data['brand']} {update.message.text}!",
                              reply_markup=markup)
    context.job_queue.run_once(lambda cont: follow(cont, update.message.chat_id,
                                                   context.user_data['brand'],
                                                   update.message.text.lower()),
                               86400, context=update.message.chat_id,
                               name=str(update.message.chat_id) + context.user_data['brand'].lower() + \
                               update.message.text.lower())

    return ConversationHandler.END


def follow(context: telegram.ext.CallbackContext, cid, branded, modeled):
    db_session.global_init("db/mods.db")
    db_sess = db_session.create_session()
    mods_wanted = db_sess.query(UserFols).filter(UserFols.user_id == cid, UserFols.brand == branded,
                                                 UserFols.model == modeled)

    for followed_car in mods_wanted:
        mods_for_now = list(db_sess.query(Mods).filter(Mods.brand == followed_car.brand.lower(),
                                                       Mods.model == followed_car.model.lower()))
        for car in mods_for_now:
            if (datetime.datetime.now() - car.created_date).seconds // 3600 + \
                    (datetime.datetime.now() - car.created_date).days * 24 < 24:
                context.bot.send_message(text=f"Hello! We've found some new mods of {followed_car.brand.capitalize()} "
                                              f"{followed_car.model.capitalize()}, which you are following:",
                                         chat_id=cid)

                context.bot.sendPhoto(chat_id=cid, photo=open(f'./previews/{car.image}.jpg', 'rb'),
                                      caption=f"{car.brand.capitalize()} {car.model.capitalize()} {car.year}\n"
                                              f"{car.description}\n"
                                              f"author: {car.author if car.author is not None else 'unknown'}\n"
                                              f"download link: {car.link}\n"
                                              f"created on: {car.created_date.date()}",
                                      reply_markup=ReplyKeyboardRemove())

    context.job_queue.run_once(lambda cont: follow(cont, cid, branded, modeled), 86400, context=cid,
                               name=str(cid) + branded + modeled)


def new_mods(update, context):
    db_session.global_init("db/mods.db")
    db_sess = db_session.create_session()
    max_id = db_sess.query(sqlalchemy.func.max(Mods.id)).scalar()
    mods_for_now = sorted(db_sess.query(Mods).filter(Mods.id >= max_id - 10),
                          key=lambda x: x.created_date, reverse=True)

    for car in mods_for_now:
        context.bot.sendPhoto(chat_id=update.message.chat_id, photo=open(f'./previews/{car.image}.jpg', 'rb'),
                              caption=f"{car.brand.capitalize()} {car.model.capitalize()} {car.year}\n"
                                      f"{car.description}\n"
                                      f"author: {car.author if car.author is not None else 'unknown'}\n"
                                      f"download link: {car.link}\n"
                                      f"created on: {car.created_date.date()}"
                              )


def about(update, context):
    smile = emojize(EMOJIS[0])
    update.message.reply_text("Welcome to AssettoModsBot! the bot will be your companion on\n"
                              f"the way to the world of high-quality mods! Hope you'll like it {smile}"
                              f"If you are a mod maker you can post your mods here and get new audience!\n"
                              f"\n"
                              "We highly recommend you to use /help command if you are a new user, "
                              "this will help you to learn more about abilities of this bot\n"
                              "\n"
                              "all mods weren't made by us, so see link to author in cars' description\n")


def start_unfollow(update, context):
    update.message.reply_text("Which car would you like to unfollow?\n"
                              'send message like "brand model"')
    return 'unfollow'


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def unfollow(update, context):
    branded, modeled = update.message.text.lower().split()
    deleted = remove_job_if_exists(str(update.message.chat_id) + branded + modeled, context)

    if deleted:
        db_session.global_init("db/mods.db")
        db_sess = db_session.create_session()
        user = db_sess.query(UserFols).filter(UserFols.user_id == update.message.chat_id,
                                              UserFols.model == modeled, UserFols.brand == branded).first()
        db_sess.delete(user)
        db_sess.commit()
        update.message.reply_text("Deleted successfully")
    else:
        update.message.reply_text("You aren't subscribed to any car")
    context.user_data.clear()
    return ConversationHandler.END


def stop_unfollowing(update, context):
    context.user_data.clear()
    return ConversationHandler.END


def about_user(update, context):
    db_session.global_init("db/mods.db")
    db_sess = db_session.create_session()
    user = db_sess.query(UserFols).filter(UserFols.user_id == update.message.chat_id).all()

    if len(user) != 0:
        update.message.reply_text("You are following these cars for now:")
        for following in user:
            update.message.reply_text(f"{following.brand.capitalize()} {following.model.capitalize()}")
    else:
        update.message.reply_text("You are not subscribed to any car yet")


def main():
    updater = Updater('5147850682:AAEl34eHZfS9epe2lPxQkpHjX5HG_cdcBDc', use_context=True)
    bot = Bot('5147850682:AAEl34eHZfS9epe2lPxQkpHjX5HG_cdcBDc')
    dp = updater.dispatcher

    reply_keyboard = ['/start']
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpfunc))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("new", new_mods))
    dp.add_handler(CommandHandler('about_user', about_user))

    mod_adding = ConversationHandler(
        entry_points=[CommandHandler('add', add)],
        states={
            'brand': [MessageHandler(Filters.text & ~Filters.command, brand)],
            'model': [MessageHandler(Filters.text & ~Filters.command, car_model)],
            'year': [MessageHandler(Filters.text & ~Filters.command, car_year)],
            'descript': [MessageHandler(Filters.text & ~Filters.command, description)],
            'image': [MessageHandler(Filters.photo | Filters.text, image)],
            'author': [MessageHandler(Filters.text & ~Filters.command, author)],
            'link': [MessageHandler(Filters.text & ~Filters.command, link)],
            'confirm': [MessageHandler(Filters.text & ~Filters.command, confirmation)]
        },
        fallbacks=[CommandHandler('stop', stop_adding)]
    )

    mod_finding = ConversationHandler(
        entry_points=[CommandHandler('find', find)],
        states={
            'brand': [MessageHandler(Filters.text & ~Filters.command, found_brand)],
            'model': [MessageHandler(Filters.text & ~Filters.command, found_model)],
            'sort': [MessageHandler(Filters.text & ~Filters.command, sort)]
        },
        fallbacks=[CommandHandler('stop', stop_finding)]
    )

    update_user = ConversationHandler(
        entry_points=[CommandHandler('follow_car', start_follow, pass_args=True,
                                     pass_job_queue=True,
                                     pass_chat_data=True)],
        states={
            'brand': [MessageHandler(Filters.text & ~Filters.command, follow_brand,
                                     pass_job_queue=True,
                                     pass_chat_data=True)],
            'model': [MessageHandler(Filters.text & ~Filters.command, follow_model,
                                     pass_job_queue=True,
                                     pass_chat_data=True)]
        },
        fallbacks=[CommandHandler('stop', stop_unfollowing)]
    )

    unfollow_dialogue = ConversationHandler(
        entry_points=[CommandHandler('unfollow', start_unfollow, pass_chat_data=True)],
        states={
            'unfollow': [MessageHandler(Filters.text & ~Filters.command, unfollow, pass_chat_data=True)]
        },
        fallbacks=[CommandHandler('stop', stop_unfollowing)]
    )

    dp.add_handler(mod_adding)
    dp.add_handler(mod_finding)
    dp.add_handler(update_user)
    dp.add_handler(unfollow_dialogue)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
