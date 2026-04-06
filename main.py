import config
import mikrotik
import transmission
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Configurazione Logging minima per vedere cosa succede nel terminale
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Stato notifiche (in memoria, si resetta al riavvio del bot)
ALREADY_NOTIFIED = set()

# --- UTILS ---
def escape_md(text: str) -> str:
    """Escapa i caratteri speciali del Markdown per evitare errori di parsing."""
    return text.replace("_", "\\_").replace("*", "\\*").replace("`", "\\`").replace("[", "\\[")

# --- MIDDLEWARE DI SICUREZZA ---
def is_authorized(update: Update) -> bool:
    return update.effective_chat.id in config.WHITELIST

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    await update.message.reply_text(
        "🤖 **Bot RB5009 Pronto**\n\n"
        "/status - Stato MikroTik & Container\n"
        "/list - Download attivi su Transmission\n"
        "/dl [link] - Aggiungi magnet link\n"
        "/del [ID] - Rimuovi torrent (mantiene file)\n"
        "/deldata [ID] - Elimina torrent e file\n"
        "/fix - Tenta ripristino disco e container",
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    
    mk = mikrotik.get_system_report()
    tr = transmission.get_client()
    tr_label = "✅ Online" if tr else "❌ Offline"
    
    if mk:
        report = (
            "🚀 **SISTEMA RB5009**\n\n"
            f"🌐 **Transmission:** {tr_label}\n"
            f"💾 **USB:** {mk['disk']}\n"
            f"🌡️ **Temp:** {mk['temp']}°C | 📊 **CPU:** {mk['cpu']}%\n"
            f"🧠 **RAM Libera:** {mk['ram']} MB\n\n"
            f"📦 **Container Status:**\n{mk['conts']}"
        )
    else:
        report = (
            "🚀 **SISTEMA RB5009**\n\n"
            f"🌐 **Transmission:** {tr_label}\n"
            "⚠️ **MikroTik API:** Non raggiungibile"
        )
        
    await update.effective_message.reply_text(report, parse_mode='Markdown')

async def fix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    success = mikrotik.run_fix_script()
    msg = "✅ Monitoraggio (Disk & Containers) avviato!" if success else "❌ Errore API MikroTik"
    await update.effective_message.reply_text(msg)

async def new_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    
    keyboard = [
        [
            InlineKeyboardButton("📊 Status Sistema", callback_data='status'),
            InlineKeyboardButton("📥 Lista Torrent", callback_data='list')
        ],
        [
            InlineKeyboardButton("🛠️ Esegui Fix/Monitor", callback_data='fix')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎮 **Pannello di Controllo RB5009**\nSeleziona un'operazione:", reply_markup=reply_markup, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # Importante per togliere l'icona di caricamento sul pulsante
    
    if query.data == 'status':
        await status(update, context)
    elif query.data == 'list':
        await list_torrents(update, context)
    elif query.data == 'fix':
        await fix(update, context)

async def download_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    if not context.args:
        await update.effective_message.reply_text("Uso: /dl [magnet_link]")
        return
    
    success = transmission.add_magnet(context.args[0])
    if success:
        await update.effective_message.reply_text("✅ Torrent aggiunto con successo!")
    else:
        await update.effective_message.reply_text("❌ Errore: Transmission offline o link non valido.")

async def list_torrents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    torrents = transmission.get_torrents()
    if torrents is None:
        await update.effective_message.reply_text("❌ Transmission offline.")
        return
    if not torrents:
        await update.effective_message.reply_text("Nessun download attivo.")
        return
        
    report = "📊 **Download in corso:**\n"
    for t in torrents:
        clean_name = escape_md(t.name[:25] + "..." if len(t.name) > 25 else t.name)
        # Mostra lo stato: scaricamento o seeding (finito)
        status = "✅ Finito" if t.progress >= 100 else "⏳ DL"
        report += f"- ID: `{t.id}` | {status} | {clean_name} | {round(t.progress, 1)}%\n"
    await update.effective_message.reply_text(report, parse_mode='Markdown')

async def delete_torrent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    if not context.args:
        await list_torrents(update, context)
        return
        
    try:
        t_id = int(context.args[0])
        if transmission.remove_torrent(t_id, delete_data=False):
            await update.effective_message.reply_text(f"🧹 Torrent {t_id} rimosso (file conservati).")
        else:
            await update.effective_message.reply_text("❌ ID non trovato o errore Transmission.")
    except ValueError:
        await update.effective_message.reply_text("❌ Inserisci un ID numerico valido.")

async def delete_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update): return
    if not context.args:
        await list_torrents(update, context)
        return
        
    try:
        t_id = int(context.args[0])
        if transmission.remove_torrent(t_id, delete_data=True):
            await update.effective_message.reply_text(f"🗑️ Torrent {t_id} e dati eliminati definitivamente.")
        else:
            await update.effective_message.reply_text("❌ ID non trovato o errore Transmission.")
    except ValueError:
        await update.effective_message.reply_text("❌ Inserisci un ID numerico valido.")

# --- BACKGROUND JOB ---
async def check_downloads(context: ContextTypes.DEFAULT_TYPE):
    torrents = transmission.get_torrents()
    if not torrents: return

    for t in torrents:
        if t.progress == 100.0 and t.id not in ALREADY_NOTIFIED:
            for user_id in config.WHITELIST:
                try:
                    await context.bot.send_message(
                        chat_id=user_id, 
                        text=f"✅ **Download Completato!**\n📦 {escape_md(t.name)}",
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logging.error(f"Errore invio notifica a {user_id}: {e}")
            ALREADY_NOTIFIED.add(t.id)

# --- MAIN ---

if __name__ == "__main__":
    print("--- Avvio Bot Telegram in corso... ---")
    
    # Creazione App
    app = Application.builder().token(config.TOKEN).build()
    
    # Background Job (controlla ogni 30 secondi)
    if app.job_queue:
        app.job_queue.run_repeating(check_downloads, interval=30, first=10)

    # Aggiunta Handler
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("new", new_menu))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("fix", fix))
    app.add_handler(CommandHandler("list", list_torrents))
    app.add_handler(CommandHandler("dl", download_cmd))
    app.add_handler(CommandHandler("del", delete_torrent))
    app.add_handler(CommandHandler("deldata", delete_all))
    
    # Gestore dei click sui bottoni
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("--- Bot in ascolto. Premi Ctrl+C per fermare. ---")
    app.run_polling()