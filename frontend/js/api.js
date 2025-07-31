// API client for QuickLedger backend
class APIClient {
  constructor() {
    // Try to detect if we're running locally or in production
    this.baseURL = this.detectBaseURL();
  }

  detectBaseURL() {
    // Check if we're running locally
    if (
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1"
    ) {
      return "http://localhost:8000";
    }

    // For production, you might want to set this to your actual API URL
    // For now, assume the API is running on the same host
    return window.location.origin.replace(":3000", ":8000"); // Common dev setup
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    const defaultOptions = {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    };

    const config = {
      ...defaultOptions,
      ...options,
    };

    // Set default method to GET only if no method is specified
    if (!config.method) {
      config.method = 'GET';
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Expense endpoints
  async getExpenses(params = {}) {
    const queryString = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryString.append(key, value.toString());
      }
    });

    const endpoint = `/expenses${
      queryString.toString() ? "?" + queryString.toString() : ""
    }`;
    return await this.request(endpoint);
  }

  async addExpense(expenseData) {
    return await this.request("/expenses", {
      method: "POST",
      body: JSON.stringify(expenseData),
    });
  }

  async updateExpense(date, index, updateData) {
    return await this.request(`/expenses/${date}/${index}`, {
      method: "PUT",
      body: JSON.stringify(updateData),
    });
  }

  async deleteExpense(date, index) {
    return await this.request(`/expenses/${date}/${index}`, {
      method: "DELETE",
    });
  }

  // Analytics endpoints
  async getSummary(params = {}) {
    const queryString = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        queryString.append(key, value.toString());
      }
    });

    const endpoint = `/summary${
      queryString.toString() ? "?" + queryString.toString() : ""
    }`;
    return await this.request(endpoint);
  }

  async getStats() {
    return await this.request("/stats");
  }

  // NLP endpoints
  async parseNaturalLanguage(text) {
    return await this.request("/nlp/parse", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  }

  async processNaturalLanguage(text) {
    return await this.request("/nlp/say", {
      method: "POST",
      body: JSON.stringify({ text }),
    });
  }

  // Health check
  async healthCheck() {
    try {
      // Try to get stats as a simple health check
      await this.getStats();
      return true;
    } catch (error) {
      console.warn("API health check failed:", error);
      return false;
    }
  }
}

// Create global API instance
const api = new APIClient();

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = APIClient;
}
