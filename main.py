import os
import asyncio
import logging
from datetime import datetime
import libtorrent as lt
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import time
import threading
from pathlib import Path
import shutil

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
DOWNLOAD_DIR = './downloads'
MAX_FILE_SIZE = 4 * 1024 * 1024 * 1024  # 4GB in bytes

class TorrentDownloader:
    def __init__(self):
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        self.downloads = {}
        
    def add_torrent(self, magnet_link, download_path):
        """Add a torrent download"""
        try:
            params = {
                'save_path': download_path,
                'storage_mode': lt.storage_mode_t(2),
                "paused": True
                'auto_managed': True,
                'duplicate_is_error': True
            }
            
            handle = lt.add_magnet_uri(self.session, magnet_link, params)
            return handle
        except Exception as e:
            logger.error(f"Error adding torrent: {e}")
            return None
    
    def get_download_info(self, handle):
        """Get download information"""
        try:
            status = handle.status()
            info = {
                'name': status.name,
                'progress': status.progress,
                'download_rate': status.download_rate,
                'upload_rate': status.upload_rate,
                'total_size': status.total_wanted,
                'downloaded': status.total_wanted_done,
                'state': str(status.state),
                'num_peers': status.num_peers,
                'is_finished': status.is_finished
            }
            return info
        except Exception as e:
            logger.error(f"Error getting download info: {e}")
            return None

class TelegramTorrentBot:
    def __init__(self):
        self.downloader = TorrentDownloader()
        self.active_downloads = {}
        
        # Create download directory
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        welcome_message = """
🤖 **Telegram Torrent Bot**

Welcome! Send me a magnet link and I'll download the torrent for you.

**Features:**
• Support for files up to 4GB
• Real-time download progress
• Automatic file upload to Telegram
• File name customization

**Usage:**
Just send me a magnet link starting with `magnet:?xt=`

**Commands:**
/start - Show this message
/status - Show active downloads
/help - Show help information
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
**How to use:**

1. Send me a magnet link
2. I'll start downloading the torrent
3. You'll see real-time progress updates
4. Once complete, I'll upload the file to Telegram
5. You can rename the file before upload

**Supported formats:**
• Any file type up to 4GB
• Multiple files in torrent (uploaded separately)

**Tips:**
• Use /status to check active downloads
• Download speed depends on seeders
• Large files may take time to upload
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Status command handler"""
        if not self.active_downloads:
            await update.message.reply_text("No active downloads.")
            return
        
        status_text = "**Active Downloads:**\n\n"
        for user_id, download_info in self.active_downloads.items():
            handle = download_info['handle']
            info = self.downloader.get_download_info(handle)
            
            if info:
                progress = info['progress'] * 100
                speed = info['download_rate'] / 1024 / 1024  # MB/s
                status_text += f"**{info['name']}**\n"
                status_text += f"Progress: {progress:.1f}%\n"
                status_text += f"Speed: {speed:.2f} MB/s\n"
                status_text += f"Peers: {info['num_peers']}\n\n"
        
        await update.message.reply_text(
            status_text,
            parse_mode='Markdown'
        )
    
    async def handle_magnet_link(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle magnet link messages"""
        magnet_link = update.message.text.strip()
        
        if not magnet_link.startswith('magnet:?xt='):
            await update.message.reply_text(
                "❌ Invalid magnet link. Please send a valid magnet link starting with 'magnet:?xt='"
            )
            return
        
        user_id = update.effective_user.id
        
        # Check if user already has an active download
        if user_id in self.active_downloads:
            await update.message.reply_text(
                "⏳ You already have an active download. Please wait for it to complete."
            )
            return
        
        # Create user-specific download directory
        user_download_dir = os.path.join(DOWNLOAD_DIR, str(user_id))
        os.makedirs(user_download_dir, exist_ok=True)
        
        # Add torrent
        handle = self.downloader.add_torrent(magnet_link, user_download_dir)
        
        if not handle:
            await update.message.reply_text(
                "❌ Failed to add torrent. Please check the magnet link."
            )
            return
        
        # Store download info
        self.active_downloads[user_id] = {
            'handle': handle,
            'chat_id': update.effective_chat.id,
            'message_id': None,
            'start_time': time.time()
        }
        
        # Send initial message
        initial_message = await update.message.reply_text(
            "🔄 **Starting download...**\n\nPlease wait while I fetch torrent information.",
            parse_mode='Markdown'
        )
        
        self.active_downloads[user_id]['message_id'] = initial_message.message_id
        
        # Start progress tracking
        asyncio.create_task(self.track_download_progress(user_id, context))
    
    async def track_download_progress(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Track download progress and update message"""
        download_info = self.active_downloads[user_id]
        handle = download_info['handle']
        chat_id = download_info['chat_id']
        message_id = download_info['message_id']
        
        last_progress = 0
        
        while user_id in self.active_downloads:
            try:
                info = self.downloader.get_download_info(handle)
                
                if not info:
                    break
                
                progress = info['progress'] * 100
                
                # Update every 5% or when finished
                if progress - last_progress >= 5 or info['is_finished']:
                    last_progress = progress
                    
                    # Format file size
                    total_size_mb = info['total_size'] / 1024 / 1024
                    downloaded_mb = info['downloaded'] / 1024 / 1024
                    speed_mb = info['download_rate'] / 1024 / 1024
                    
                    # Calculate ETA
                    if info['download_rate'] > 0:
                        remaining_bytes = info['total_size'] - info['downloaded']
                        eta_seconds = remaining_bytes / info['download_rate']
                        eta_minutes = eta_seconds / 60
                        eta_text = f"{eta_minutes:.1f} min"
                    else:
                        eta_text = "Unknown"
                    
                    progress_text = f"""
🔄 **Downloading Torrent**

**File:** {info['name']}
**Progress:** {progress:.1f}%
**Downloaded:** {downloaded_mb:.1f} MB / {total_size_mb:.1f} MB
**Speed:** {speed_mb:.2f} MB/s
**Peers:** {info['num_peers']}
**ETA:** {eta_text}
**Status:** {info['state']}

{'▓' * int(progress / 5)}{'░' * (20 - int(progress / 5))}
                    """
                    
                    try:
                        await context.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=message_id,
                            text=progress_text,
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        logger.error(f"Error updating progress message: {e}")
                
                # Check if download is complete
                if info['is_finished']:
                    await self.handle_completed_download(user_id, context)
                    break
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in progress tracking: {e}")
                break
    
    async def handle_completed_download(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Handle completed download"""
        download_info = self.active_downloads[user_id]
        handle = download_info['handle']
        chat_id = download_info['chat_id']
        message_id = download_info['message_id']
        
        info = self.downloader.get_download_info(handle)
        
        if not info:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text="❌ Error getting download information.",
                parse_mode='Markdown'
            )
            del self.active_downloads[user_id]
            return
        
        # Update completion message
        completion_text = f"""
✅ **Download Complete!**

**File:** {info['name']}
**Size:** {info['total_size'] / 1024 / 1024:.1f} MB
**Time:** {(time.time() - download_info['start_time']) / 60:.1f} minutes

🔄 **Preparing for upload...**
        """
        
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=completion_text,
            parse_mode='Markdown'
        )
        
        # Find and upload files
        user_download_dir = os.path.join(DOWNLOAD_DIR, str(user_id))
        await self.upload_files(user_id, user_download_dir, context)
        
        # Clean up
        del self.active_downloads[user_id]
        shutil.rmtree(user_download_dir, ignore_errors=True)
    
    async def upload_files(self, user_id: int, download_dir: str, context: ContextTypes.DEFAULT_TYPE):
        """Upload downloaded files to Telegram"""
        chat_id = self.active_downloads[user_id]['chat_id']
        
        try:
            # Find all files in download directory
            files_to_upload = []
            for root, dirs, files in os.walk(download_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    
                    if file_size > MAX_FILE_SIZE:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"❌ File too large: {file} ({file_size / 1024 / 1024:.1f} MB)\n"
                                 f"Maximum supported size: {MAX_FILE_SIZE / 1024 / 1024:.1f} MB"
                        )
                        continue
                    
                    files_to_upload.append((file_path, file, file_size))
            
            if not files_to_upload:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="❌ No files found or all files are too large."
                )
                return
            
            # Upload files
            for file_path, file_name, file_size in files_to_upload:
                upload_message = await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⬆️ Uploading: {file_name} ({file_size / 1024 / 1024:.1f} MB)"
                )
                
                try:
                    with open(file_path, 'rb') as file:
                        await context.bot.send_document(
                            chat_id=chat_id,
                            document=file,
                            filename=file_name,
                            caption=f"📁 {file_name}\n💾 Size: {file_size / 1024 / 1024:.1f} MB"
                        )
                    
                    await context.bot.delete_message(
                        chat_id=chat_id,
                        message_id=upload_message.message_id
                    )
                    
                except Exception as e:
                    logger.error(f"Error uploading file {file_name}: {e}")
                    await context.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=upload_message.message_id,
                        text=f"❌ Failed to upload: {file_name}"
                    )
        
        except Exception as e:
            logger.error(f"Error in upload process: {e}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Error during file upload process."
            )

def main():
    """Main function to run the bot"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set!")
        return
    
    # Initialize bot
    bot = TelegramTorrentBot()
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_magnet_link))
    
    # Run bot
    logger.info("Starting Telegram Torrent Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
