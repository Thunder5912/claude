#!/bin/bash

# Telegram Torrent Bot Deployment Script
# This script helps deploy the bot to Render

set -e

echo "🚀 Telegram Torrent Bot Deployment Script"
echo "=========================================="

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if user is in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Not in a git repository. Please run this script from the project root."
    exit 1
fi

# Function to check if BOT_TOKEN is set
check_bot_token() {
    if [ -z "$BOT_TOKEN" ]; then
        echo "⚠️  BOT_TOKEN environment variable is not set."
        echo "Please set it before deployment:"
        echo "export BOT_TOKEN='your_telegram_bot_token_here'"
        echo ""
        echo "To get a bot token:"
        echo "1. Message @BotFather on Telegram"
        echo "2. Send /newbot"
        echo "3. Follow the instructions"
        echo "4. Copy the token provided"
        return 1
    else
        echo "✅ BOT_TOKEN is set"
        return 0
    fi
}

# Function to validate requirements
validate_requirements() {
    echo "🔍 Validating requirements..."
    
    if [ ! -f "requirements.txt" ]; then
        echo "❌ requirements.txt not found"
        exit 1
    fi
    
    if [ ! -f "main.py" ]; then
        echo "❌ main.py not found"
        exit 1
    fi
    
    if [ ! -f "Dockerfile" ]; then
        echo "❌ Dockerfile not found"
        exit 1
    fi
    
    echo "✅ All required files found"
}

# Function to create GitHub repository
create_github_repo() {
    echo "📁 Setting up GitHub repository..."
    
    # Check if origin remote exists
    if git remote get-url origin &> /dev/null; then
        echo "✅ Git remote origin already exists"
        REPO_URL=$(git remote get-url origin)
        echo "Repository URL: $REPO_URL"
    else
        echo "⚠️  No git remote origin found."
        echo "Please create a GitHub repository and add it as origin:"
        echo "git remote add origin https://github.com/yourusername/telegram-torrent-bot.git"
        echo "Then run this script again."
        exit 1
    fi
}

# Function to commit and push changes
commit_and_push() {
    echo "📤 Committing and pushing changes..."
    
    # Add all files
    git add .
    
    # Check if there are changes to commit
    if git diff --staged --quiet; then
        echo "✅ No changes to commit"
    else
        # Commit changes
        git commit -m "Deploy: Update bot configuration for Render deployment"
        echo "✅ Changes committed"
    fi
    
    # Push to GitHub
    git push origin main
    echo "✅ Changes pushed to GitHub"
}

# Function to show deployment instructions
show_deployment_instructions() {
    echo ""
    echo "🎉 Ready for Render deployment!"
    echo "================================"
    echo ""
    echo "Next steps:"
    echo "1. Go to https://render.com and sign up/login"
    echo "2. Click 'New +' and select 'Web Service'"
    echo "3. Connect your GitHub repository"
    echo "4. Configure the service:"
    echo "   - Name: telegram-torrent-bot"
    echo "   - Environment: Docker"
    echo "   - Build Command: (leave empty)"
    echo "   - Start Command: python main.py"
    echo "5. Add environment variables:"
    echo "   - BOT_TOKEN: $BOT_TOKEN"
    echo "6. Click 'Create Web Service'"
    echo ""
    echo "📋 Render Configuration:"
    echo "- Region: Choose closest to your users"
    echo "- Plan: Free tier is sufficient for testing"
    echo "- Health Check: Disabled (not needed for bot)"
    echo ""
    echo "🔗 Your repository: $(git remote get-url origin)"
    echo ""
    echo "📖 For detailed instructions, see README.md"
}

# Main deployment process
main() {
    echo "Starting deployment process..."
    echo ""
    
    # Validate requirements
    validate_requirements
    
    # Check bot token
    if ! check_bot_token; then
        echo ""
        echo "Please set your BOT_TOKEN and run the script again."
        exit 1
    fi
    
    # Setup GitHub repository
    create_github_repo
    
    # Commit and push changes
    commit_and_push
    
    # Show deployment instructions
    show_deployment_instructions
    
    echo ""
    echo "✅ Deployment preparation complete!"
    echo "You can now deploy to Render using the instructions above."
}

# Run main function
main
