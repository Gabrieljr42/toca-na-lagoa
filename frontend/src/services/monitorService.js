/** Monitor status and manual checks. */
export class MonitorService {
  constructor(http) {
    this.http = http;
  }

  status() {
    return this.http.get('/api/status');
  }

  checkNow() {
    return this.http.post('/api/check');
  }
}
