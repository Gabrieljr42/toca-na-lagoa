/** Labels and suggestions shared by the pages. */
export class OptionsService {
  constructor(http) {
    this.http = http;
  }

  get() {
    return this.http.get('/api/options');
  }
}
