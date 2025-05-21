# College Telegram Bot

Telegram bot for college/university students with features for requests, grades tracking, surveys, and room booking.

## Features

1. **Заявки и обращения (Requests and Appeals)**
   - Request certificates
   - Absence requests
   - Document requests
   - Other appeals

2. **Отслеживание успеваемости (Grades Tracking)**
   - Current grades
   - Debts tracking
   - Attendance statistics
   - Group ranking

3. **Опросы и анкеты (Surveys)**
   - Teacher evaluations
   - Event feedback
   - Process improvement suggestions
   - New student questionnaires

4. **Бронирование помещений (Room Booking)**
   - Classroom booking
   - Computer lab booking
   - Conference room booking
   - Sports hall booking

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with your bot token:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
4. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

1. Start the bot by sending `/start` command
2. Use the interactive menu to navigate through features
3. Follow the bot's prompts to complete actions

## Development

The bot is built using:
- python-telegram-bot library
- SQLAlchemy for database operations
- Python-dotenv for environment variables

## Contributing

Feel free to submit issues and enhancement requests. 