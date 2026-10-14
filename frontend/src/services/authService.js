/** Login session endpoints. */
export class AuthService {
  constructor(http) {
    this.http = http;
  }

  session() {
    return this.http.get('/api/auth/session');
  }

  login(password) {
    return this.http.post('/api/auth/login', { password });
  }

  logout() {
    return this.http.post('/api/auth/logout');
  }
}
