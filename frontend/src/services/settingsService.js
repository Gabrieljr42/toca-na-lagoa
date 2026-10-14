/** Search and schedule settings endpoints. */
export class SettingsService {
  constructor(http) {
    this.http = http;
  }

  get() {
    return this.http.get('/api/settings');
  }

  save(settings) {
    return this.http.put('/api/settings', settings);
  }
}
