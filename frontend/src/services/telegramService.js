/** Telegram setup endpoints. */
export class TelegramService {
  constructor(http) {
    this.http = http;
  }

  save({ botToken, chatId }) {
    return this.http.put('/api/telegram', { bot_token: botToken, chat_id: chatId });
  }

  detectChat() {
    return this.http.post('/api/telegram/detect');
  }

  sendTest() {
    return this.http.post('/api/telegram/test');
  }
}
