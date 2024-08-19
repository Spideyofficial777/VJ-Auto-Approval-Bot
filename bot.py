from pyrogram import Client, filters, enums, errors
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserNotParticipant
from pyrogram.errors.exceptions.flood_420 import FloodWait
from database import add_user, add_group, all_users, all_groups, users, remove_user
from configs import cfg
import asyncio

app = Client(
    "approver",
    api_id=cfg.API_ID,
    api_hash=cfg.API_HASH,
    bot_token=cfg.BOT_TOKEN
)

# Updated image for welcome message
WELCOME_IMAGE_URL = "https://i.ibb.co/CPxdkHR/IMG-20240818-192201-633.jpg"

# Approve all pending requests when bot starts
@app.on_chat_join_request(filters.group | filters.channel & ~filters.private)
async def approve_all_requests(_, m: Message):
    try:
        add_group(m.chat.id)
        await app.approve_chat_join_request(m.chat.id, m.from_user.id)
        await app.send_photo(m.from_user.id, WELCOME_IMAGE_URL, 
                             caption=f"**Hello {m.from_user.mention}!\nWelcome to {m.chat.title}\n\n__Powered by: @Spidey_official_777__**")
        add_user(m.from_user.id)
    except errors.PeerIdInvalid:
        print("User hasn't started the bot (PeerIdInvalid)")
    except Exception as err:
        print(str(err))

@app.on_message(filters.command("start"))
async def start(_, m: Message):
    try:
        await app.get_chat_member(cfg.CHID, m.from_user.id)
        if m.chat.type == enums.ChatType.PRIVATE:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🗯 Channel", url="https://t.me/+wqqdiBLf6mI5MmU1"),
                        InlineKeyboardButton("💬 Support", url="https://t.me/+wqqdiBLf6mI5MmU1")
                    ],
                    [
                        InlineKeyboardButton("➕ Add me to your Chat ➕", url="https://t.me/+wqqdiBLf6mI5MmU1")
                    ]
                ]
            )
            add_user(m.from_user.id)
            await m.reply_photo(
                WELCOME_IMAGE_URL,
                caption=f"**🦊 Hello {m.from_user.mention}!\nI'm an auto-approve [Admin Join Requests](https://t.me/telegram/153) bot.\nI can approve users in Groups/Channels. Add me to your chat and promote me to admin with add members permission.\n\n__Powered by: @Spidey_official_777__**",
                reply_markup=keyboard
            )
        elif m.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("💁‍♂️ Start me private 💁‍♂️", url="https://t.me/+wqqdiBLf6mI5MmU1")
                    ]
                ]
            )
            add_group(m.chat.id)
            await m.reply_text(f"**🦊 Hello {m.from_user.first_name}!\nWrite me privately for more details**", reply_markup=keyboard)
        print(f"{m.from_user.first_name} has started your bot!")
    except UserNotParticipant:
        key = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("🍀 Check Again 🍀", "chk")]
            ]
        )
        await m.reply_text(f"**⚠️ Access Denied! ⚠️\n\nPlease join @{cfg.FSUB} to use me. If you've already joined, click 'Check Again' to confirm.**", reply_markup=key)

@app.on_callback_query(filters.regex("chk"))
async def check_subscription(_, cb: CallbackQuery):
    try:
        await app.get_chat_member(cfg.CHID, cb.from_user.id)
        if cb.message.chat.type == enums.ChatType.PRIVATE:
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🗯 Channel", url="https://t.me/+wqqdiBLf6mI5MmU1"),
                        InlineKeyboardButton("💬 Support", url="https://t.me/+wqqdiBLf6mI5MmU1")
                    ],
                    [
                        InlineKeyboardButton("➕ Add me to your Chat ➕", url="https://t.me/+wqqdiBLf6mI5MmU1")
                    ]
                ]
            )
            add_user(cb.from_user.id)
            await cb.message.edit(
                f"**🦊 Hello {cb.from_user.mention}!\nI'm an auto-approve [Admin Join Requests](https://t.me/telegram/153) bot.\nI can approve users in Groups/Channels. Add me to your chat and promote me to admin with add members permission.\n\n__Powered by: @Spidey_official_777__**",
                reply_markup=keyboard,
                disable_web_page_preview=True
            )
        print(f"{cb.from_user.first_name} has started your bot!")
    except UserNotParticipant:
        await cb.answer("🙅‍♂️ You are not joined to the channel. Join and try again. 🙅‍♂️")

@app.on_message(filters.command("users") & filters.user(cfg.SUDO))
async def dbtool(_, m: Message):
    total_users = all_users()
    total_groups = all_groups()
    total = total_users + total_groups
    await m.reply_text(f"""
🍀 Chats Stats 🍀
🙋‍♂️ Users : `{total_users}`
👥 Groups : `{total_groups}`
🚧 Total users & groups : `{total}`""")

@app.on_message(filters.command("bcast") & filters.user(cfg.SUDO))
async def broadcast(_, m: Message):
    all_users = users
    processing_msg = await m.reply_text("⚡️ Processing...")
    success, failed, deactivated, blocked = 0, 0, 0, 0
    
    for user in all_users.find():
        try:
            user_id = user["user_id"]
            await m.reply_to_message.copy(user_id)
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await m.reply_to_message.copy(user_id)
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(user_id)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(e)
            failed += 1

    await processing_msg.edit(f"✅ Successfully broadcasted to `{success}` users.\n❌ Failed to reach `{failed}` users.\n👾 Found `{blocked}` blocked users.\n👻 Found `{deactivated}` deactivated users.")

@app.on_message(filters.command("fcast") & filters.user(cfg.SUDO))
async def forward_broadcast(_, m: Message):
    all_users = users
    processing_msg = await m.reply_text("⚡️ Processing...")
    success, failed, deactivated, blocked = 0, 0, 0, 0
    
    for user in all_users.find():
        try:
            user_id = user["user_id"]
            await m.reply_to_message.forward(user_id)
            success += 1
        except FloodWait as ex:
            await asyncio.sleep(ex.value)
            await m.reply_to_message.forward(user_id)
        except errors.InputUserDeactivated:
            deactivated += 1
            remove_user(user_id)
        except errors.UserIsBlocked:
            blocked += 1
        except Exception as e:
            print(e)
            failed += 1

    await processing_msg.edit(f"✅ Successfully forwarded to `{success}` users.\n❌ Failed to reach `{failed}` users.\n👾 Found `{blocked}` blocked users.\n👻 Found `{deactivated}` deactivated users.")

# Automatically accept all previous pending requests
async def accept_all_pending_requests():
    try:
        group_list = all_groups()
        for group in group_list:
            members = await app.get_chat_members(group['chat_id'], filter="restricted")
            for member in members:
                if member.user.is_bot or member.user.is_deleted:
                    continue
                try:
                    await app.approve_chat_join_request(group['chat_id'], member.user.id)
                    await app.send_photo(member.user.id, WELCOME_IMAGE_URL,
                                         caption=f"**Hello {member.user.mention}!\nWelcome to {group['title']}\n\n__Powered by: @Spidey_official_777__**")
                except Exception as e:
                    print(f"Failed to approve {member.user.id} in {group['chat_id']}: {e}")
    except Exception as e:
        print(f"Error in accepting pending requests: {e}")

# Run the bot and accept pending requests when it starts
async def main():
    await app.start()
    await accept_all_pending_requests()
    print("Bot is now running!")
    await app.stop()

if __name__ == "__main__":
    app.run(main)
