import config, mikrotik, transmission
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in config.WHITELIST: return
    
    mk = mikrotik.get_system_report()
    tr = transmission.get_client()
    tr_label = "✅ Online" if tr else "❌ Offline"
    
    if mk:
        report = (f"🚀 **SISTEMA RB5009**\n\n💾 **USB:** {mk['disk']}\n🌐 **TR:** {tr_label}\n"
                  f"🌡️ **Temp:** {mk['temp']}°C | 📊 **CPU:** {mk['cpu']}%\n"
                  f"🧠 **RAM:** {mk['ram']} MB\n\n📦 **Containers:**\n{mk['conts']}")
    else:
        report = f"⚠️ MikroTik API Offline\n🌐 **TR:** {tr_label}"
        
    await update.message.reply_text(report, parse_mode='Markdown')

async def fix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id not in config.WHITELIST: return
    success = mikrotik.run_fix_script()
    msg = "✅ Script lanciato!" if success else "❌ Errore API"
    await update.message.reply_text(msg)

# ... Aggiungi qui gli altri handler (list, download, ecc.) seguendo lo stesso stile ...

if __name__ == "__main__":
    app = Application.builder().token(config.TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("fix", fix))
    # Handler per i magnet link automatici
    app.add_handler(MessageHandler(filters.Regex(r'magnet:\?xt=urn:btih:.*'), 
                                   lambda u, c: transmission.add_magnet(u.message.text)))
    
    app.run_polling()