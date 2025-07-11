# Telegram Torrent Bot

A powerful Telegram bot that downloads torrents from magnet links and uploads them directly to Telegram. Supports files up to 4GB with real-time progress tracking.

## Features

- 📥 Download torrents from magnet links
- 📤 Upload files directly to Telegram (up to 4GB)
- 📊 Real-time download progress tracking
- 🔄 Multiple file support
- 🎯 File name preservation
- 🚀 Easy deployment on Render
- 🔒 User-specific download isolation
- 📱 Mobile-friendly interface

## Quick Start

### Prerequisites

- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Render account (for deployment)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/telegram-torrent-bot.git
   cd telegram-torrent-bot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export BOT_TOKEN="your_telegram_bot_token_here"
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

### Deploy on Render

1. **Fork this repository**

2. **Create a new Web Service on Render:**
   - Connect your GitHub repository
   - Use the following settings:
     - **Environment**: Docker
     - **Build Command**: (leave empty)
     - **Start Command**: `python main.py`

3. **Set environment variables in Render:**
   - `BOT_TOKEN`: Your Telegram bot token

4. **Deploy**: Click "Create Web Service"

## Usage

### Bot Commands

- `/start` - Welcome message and instructions
- `/help` - Detailed help information
- `/status` - Check active downloads

### How to Use

1. **Start the bot** by sending `/start`
2. **Send a magnet link** (starting with `magnet:?xt=`)
3. **Wait for download** - You'll see real-time progress
4. **Receive files** - Files will be uploaded to Telegram automatically

### Example Magnet Link Format
```
magnet:?xt=urn:btih:HASH&dn=filename&tr=tracker_url
```

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BOT_TOKEN` | Telegram Bot Token | Yes | - |
| `LOG_LEVEL` | Logging level | No | INFO |

### File Limits

- **Maximum file size**: 4GB
- **Supported formats**: All file types
- **Multiple files**: Supported (uploaded separately)

## Project Structure

```
telegram-torrent-bot/
├── main.py              # Main bot application
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── Dockerfile          # Docker configuration
├── render.yaml         # Render deployment config
├── README.md           # This file
└── downloads/          # Temporary download directory
```

## Technical Details

### Dependencies

- **python-telegram-bot**: Telegram Bot API wrapper
- **libtorrent**: BitTorrent library for downloads
- **asyncio**: Asynchronous programming support

### Architecture

1. **Torrent Handling**: Uses libtorrent for efficient downloading
2. **Progress Tracking**: Real-time updates every 5 seconds
3. **File Upload**: Chunked upload for large files
4. **Memory Management**: Automatic cleanup after uploads
5. **Error Handling**: Comprehensive error handling and logging

### Security Features

- User-specific download directories
- File size validation
- Magnet link validation
- Automatic cleanup of temporary files

## Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if BOT_TOKEN is set correctly
   - Verify the bot is running without errors

2. **Download fails**
   - Ensure the magnet link is valid
   - Check if there are enough seeders
   - Verify network connectivity

3. **Upload fails**
   - Check if file size is under 4GB
   - Ensure stable internet connection
   - Verify Telegram API limits

### Logs

The bot provides detailed logging. Check the console output for:
- Download progress
- Error messages
- Upload status
- System information

## Development

### Adding Features

1. **Fork the repository**
2. **Create a feature branch**
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

### Testing

```bash
# Run the bot in development mode
python main.py

# Check logs for any errors
tail -f logs/bot.log
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/telegram-torrent-bot/issues) page
2. Create a new issue with detailed information
3. Include logs and error messages

## Disclaimer

This bot is for educational purposes only. Users are responsible for ensuring they have the right to download and share any content. The developers are not responsible for any misuse of this software.

## Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot API wrapper
- [libtorrent](https://www.libtorrent.org/) - BitTorrent library
- [Render](https://render.com/) - Deployment platform

---

**⭐ Star this repository if you find it useful!**
