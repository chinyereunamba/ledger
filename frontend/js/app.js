// Main application logic
class QuickLedger {
  constructor() {
    this.currentSection = "dashboard";
    this.expenses = [];
    this.stats = {};
    this.init();
  }

  async init() {
    // Set today's date as default
    const today = new Date().toISOString().split("T")[0];
    const dateInput = document.getElementById("expense-date");
    if (dateInput) {
      dateInput.value = today;
    }

    // Load initial data
    await this.loadDashboard();

    // Set up event listeners
    this.setupEventListeners();

    // Show dashboard by default
    this.showSection("dashboard");
  }

  setupEventListeners() {
    // Form submission
    const expenseForm = document.getElementById("expense-form");
    if (expenseForm) {
      expenseForm.addEventListener("submit", (e) => {
        e.preventDefault();
        this.addExpense();
      });
    }

    // Filter change
    const expenseFilter = document.getElementById("expense-filter");
    if (expenseFilter) {
      expenseFilter.addEventListener("change", () => {
        this.loadExpenses();
      });
    }

    // Enter key handlers for quick inputs
    const quickExpense = document.getElementById("quick-expense");
    const quickAmount = document.getElementById("quick-amount");

    if (quickExpense && quickAmount) {
      quickExpense.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
          quickAmount.focus();
        }
      });

      quickAmount.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
          this.quickAddExpense();
        }
      });
    }

    // NLP input enter key
    const nlpInput = document.getElementById("nlp-input");
    if (nlpInput) {
      nlpInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          this.processNaturalLanguage();
        }
      });
    }
  }

  showSection(sectionName) {
    // Hide all sections
    const sections = document.querySelectorAll(".section");
    sections.forEach((section) => {
      section.classList.add("hidden");
    });

    // Show selected section
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
      targetSection.classList.remove("hidden");
      targetSection.classList.add("slide-in");
    }

    // Update navigation
    const navButtons = document.querySelectorAll(".nav-btn");
    navButtons.forEach((btn) => {
      btn.classList.remove("bg-white", "bg-opacity-30");
    });

    this.currentSection = sectionName;

    // Load section-specific data
    switch (sectionName) {
      case "dashboard":
        this.loadDashboard();
        break;
      case "expenses":
        this.loadExpenses();
        break;
      case "analytics":
        this.loadAnalytics();
        break;
    }

    // Close mobile menu
    this.closeMobileMenu();
  }

  toggleMobileMenu() {
    const mobileMenu = document.getElementById("mobile-menu");
    if (mobileMenu) {
      mobileMenu.classList.toggle("hidden");
    }
  }

  closeMobileMenu() {
    const mobileMenu = document.getElementById("mobile-menu");
    if (mobileMenu) {
      mobileMenu.classList.add("hidden");
    }
  }

  async loadDashboard() {
    try {
      this.showLoading();

      // Load stats and recent expenses
      const [stats, expenses] = await Promise.all([
        api.getStats(),
        api.getExpenses({ limit: 5 }),
      ]);

      this.updateDashboardStats(stats);
      this.updateRecentExpenses(expenses.expenses);
    } catch (error) {
      console.error("Error loading dashboard:", error);
      this.showToast("Error loading dashboard data", "error");
    } finally {
      this.hideLoading();
    }
  }

  updateDashboardStats(stats) {
    document.getElementById("total-spent").textContent = `₦${this.formatNumber(
      stats.total_spent
    )}`;
    document.getElementById(
      "daily-average"
    ).textContent = `₦${this.formatNumber(stats.daily_average)}`;
    document.getElementById("transaction-count").textContent =
      stats.transaction_count.toLocaleString();
    document.getElementById("days-tracked").textContent =
      stats.days_tracked.toLocaleString();
  }

  updateRecentExpenses(expenses) {
    const container = document.getElementById("recent-expenses");
    if (!container) return;

    if (expenses.length === 0) {
      container.innerHTML =
        '<p class="text-gray-500 text-center py-4">No expenses yet. Add your first expense!</p>';
      return;
    }

    container.innerHTML = expenses
      .map(
        (expense) => `
            <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                <div>
                    <p class="font-medium text-gray-900">${expense.expense}</p>
                    <p class="text-sm text-gray-500">${this.formatDate(
                      expense.date
                    )}</p>
                </div>
                <span class="font-semibold text-gray-900">₦${this.formatNumber(
                  expense.amount
                )}</span>
            </div>
        `
      )
      .join("");
  }

  async addExpense() {
    const name = document.getElementById("expense-name").value.trim();
    const amount = parseFloat(document.getElementById("expense-amount").value);
    const date = document.getElementById("expense-date").value;

    if (!name || !amount || amount <= 0) {
      this.showToast("Please fill in all fields correctly", "error");
      return;
    }

    try {
      this.showLoading();

      await api.addExpense({
        expense: name,
        amount: amount,
        date: date || undefined,
      });

      this.showToast("Expense added successfully!", "success");

      // Clear form
      document.getElementById("expense-form").reset();
      const today = new Date().toISOString().split("T")[0];
      document.getElementById("expense-date").value = today;

      // Refresh dashboard if we're on it
      if (this.currentSection === "dashboard") {
        await this.loadDashboard();
      }
    } catch (error) {
      console.error("Error adding expense:", error);
      this.showToast("Error adding expense", "error");
    } finally {
      this.hideLoading();
    }
  }

  async quickAddExpense() {
    const expense = document.getElementById("quick-expense").value.trim();
    const amount = parseFloat(document.getElementById("quick-amount").value);

    if (!expense || !amount || amount <= 0) {
      this.showToast("Please fill in both fields", "error");
      return;
    }

    try {
      await api.addExpense({
        expense: expense,
        amount: amount,
      });

      this.showToast("Expense added successfully!", "success");

      // Clear inputs
      document.getElementById("quick-expense").value = "";
      document.getElementById("quick-amount").value = "";

      // Refresh dashboard
      await this.loadDashboard();
    } catch (error) {
      console.error("Error adding expense:", error);
      this.showToast("Error adding expense", "error");
    }
  }

  async processNaturalLanguage() {
    const text = document.getElementById("nlp-input").value.trim();

    if (!text) {
      this.showToast("Please enter some text", "error");
      return;
    }

    try {
      this.showLoading();

      const result = await api.processNaturalLanguage(text);

      this.showToast(
        `Added ${result.parsed_expenses.length} expense(s) successfully!`,
        "success"
      );

      // Clear input
      document.getElementById("nlp-input").value = "";

      // Refresh dashboard
      await this.loadDashboard();
    } catch (error) {
      console.error("Error processing natural language:", error);
      this.showToast(
        "Error processing text. Please try a different format.",
        "error"
      );
    } finally {
      this.hideLoading();
    }
  }

  async processNaturalLanguageAdd() {
    const text = document.getElementById("nlp-text").value.trim();

    if (!text) {
      this.showToast("Please enter some text", "error");
      return;
    }

    try {
      this.showLoading();

      const result = await api.processNaturalLanguage(text);

      this.showToast(
        `Added ${result.parsed_expenses.length} expense(s) successfully!`,
        "success"
      );

      // Clear input
      document.getElementById("nlp-text").value = "";
    } catch (error) {
      console.error("Error processing natural language:", error);
      this.showToast(
        "Error processing text. Please try a different format.",
        "error"
      );
    } finally {
      this.hideLoading();
    }
  }

  async loadExpenses() {
    try {
      this.showLoading();

      const filter = document.getElementById("expense-filter").value;
      let params = { limit: 100 };

      // Apply filters
      switch (filter) {
        case "today":
          params.date = new Date().toISOString().split("T")[0];
          break;
        case "week":
          params.week = true;
          break;
        case "month":
          const now = new Date();
          const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
          const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
          params.range = `${firstDay.toISOString().split("T")[0]},${
            lastDay.toISOString().split("T")[0]
          }`;
          break;
      }

      const result = await api.getExpenses(params);
      this.displayExpenses(result.expenses);

      // Update count
      document.getElementById("expense-count").textContent = `${
        result.total
      } expense${result.total !== 1 ? "s" : ""}`;
    } catch (error) {
      console.error("Error loading expenses:", error);
      this.showToast("Error loading expenses", "error");
    } finally {
      this.hideLoading();
    }
  }

  displayExpenses(expenses) {
    const container = document.getElementById("expenses-list");
    if (!container) return;

    if (expenses.length === 0) {
      container.innerHTML =
        '<div class="p-6 text-center text-gray-500">No expenses found</div>';
      return;
    }

    container.innerHTML = expenses
      .map(
        (expense, index) => `
            <div class="p-4 hover:bg-gray-50 transition-colors">
                <div class="flex justify-between items-center">
                    <div class="flex-1">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                                <span class="text-blue-600 font-semibold">${expense.expense
                                  .charAt(0)
                                  .toUpperCase()}</span>
                            </div>
                            <div>
                                <p class="font-medium text-gray-900">${
                                  expense.expense
                                }</p>
                                <p class="text-sm text-gray-500">${this.formatDate(
                                  expense.date
                                )}</p>
                            </div>
                        </div>
                    </div>
                    <div class="flex items-center space-x-3">
                        <span class="font-semibold text-lg text-gray-900">₦${this.formatNumber(
                          expense.amount
                        )}</span>
                        <div class="flex space-x-1">
                            <button onclick="app.editExpense('${
                              expense.date
                            }', ${index})" class="text-blue-600 hover:text-blue-800 p-1">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                                </svg>
                            </button>
                            <button onclick="app.deleteExpense('${
                              expense.date
                            }', ${index})" class="text-red-600 hover:text-red-800 p-1">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                </svg>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `
      )
      .join("");
  }

  async loadAnalytics() {
    try {
      this.showLoading();

      const stats = await api.getStats();
      this.displayAnalytics(stats);
    } catch (error) {
      console.error("Error loading analytics:", error);
      this.showToast("Error loading analytics", "error");
    } finally {
      this.hideLoading();
    }
  }

  displayAnalytics(stats) {
    // Update detailed stats
    const detailedStats = document.getElementById("detailed-stats");
    if (detailedStats) {
      detailedStats.innerHTML = `
                <div class="text-center">
                    <p class="text-2xl font-bold text-blue-600">₦${this.formatNumber(
                      stats.total_spent
                    )}</p>
                    <p class="text-sm text-gray-500">Total Spent</p>
                </div>
                <div class="text-center">
                    <p class="text-2xl font-bold text-green-600">₦${this.formatNumber(
                      stats.daily_average
                    )}</p>
                    <p class="text-sm text-gray-500">Daily Average</p>
                </div>
                <div class="text-center">
                    <p class="text-2xl font-bold text-purple-600">${
                      stats.transaction_count
                    }</p>
                    <p class="text-sm text-gray-500">Total Transactions</p>
                </div>
                <div class="text-center">
                    <p class="text-2xl font-bold text-orange-600">${
                      stats.most_spent_category?.name || "N/A"
                    }</p>
                    <p class="text-sm text-gray-500">Top Category</p>
                </div>
                <div class="text-center">
                    <p class="text-2xl font-bold text-red-600">${
                      stats.most_frequent_expense?.name || "N/A"
                    }</p>
                    <p class="text-sm text-gray-500">Most Frequent</p>
                </div>
                <div class="text-center">
                    <p class="text-2xl font-bold text-indigo-600">${
                      stats.most_expensive_day?.date || "N/A"
                    }</p>
                    <p class="text-sm text-gray-500">Highest Spending Day</p>
                </div>
            `;
    }

    // Update charts
    this.updateCharts(stats);
  }

  updateCharts(stats) {
    // Category chart
    if (stats.top_categories && stats.top_categories.length > 0) {
      charts.updateCategoryChart(stats.top_categories);
    }

    // Expenses chart
    if (stats.top_expenses && stats.top_expenses.length > 0) {
      charts.updateExpensesChart(stats.top_expenses);
    }
  }

  async editExpense(date, index) {
    const newExpense = prompt("Enter new expense name:");
    const newAmount = prompt("Enter new amount:");

    if (!newExpense && !newAmount) return;

    try {
      await api.updateExpense(date, index, {
        expense: newExpense || undefined,
        amount: newAmount ? parseFloat(newAmount) : undefined,
      });

      this.showToast("Expense updated successfully!", "success");
      await this.loadExpenses();
    } catch (error) {
      console.error("Error updating expense:", error);
      this.showToast("Error updating expense", "error");
    }
  }

  async deleteExpense(date, index) {
    if (!confirm("Are you sure you want to delete this expense?")) return;

    try {
      await api.deleteExpense(date, index);
      this.showToast("Expense deleted successfully!", "success");
      await this.loadExpenses();
    } catch (error) {
      console.error("Error deleting expense:", error);
      this.showToast("Error deleting expense", "error");
    }
  }

  // Utility methods
  formatNumber(num) {
    return new Intl.NumberFormat("en-NG").format(num);
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-NG", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  showLoading() {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
      overlay.classList.remove("hidden");
    }
  }

  hideLoading() {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
      overlay.classList.add("hidden");
    }
  }

  showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) return;

    const toast = document.createElement("div");
    const bgColor =
      type === "success"
        ? "bg-green-500"
        : type === "error"
        ? "bg-red-500"
        : "bg-blue-500";

    toast.className = `${bgColor} text-white px-6 py-3 rounded-lg shadow-lg transform transition-all duration-300 translate-x-full`;
    toast.textContent = message;

    container.appendChild(toast);

    // Animate in
    setTimeout(() => {
      toast.classList.remove("translate-x-full");
    }, 100);

    // Remove after 3 seconds
    setTimeout(() => {
      toast.classList.add("translate-x-full");
      setTimeout(() => {
        if (container.contains(toast)) {
          container.removeChild(toast);
        }
      }, 300);
    }, 3000);
  }
}

// Global functions for HTML onclick handlers
function showSection(section) {
  app.showSection(section);
}

function toggleMobileMenu() {
  app.toggleMobileMenu();
}

function quickAddExpense() {
  app.quickAddExpense();
}

function processNaturalLanguage() {
  app.processNaturalLanguage();
}

function processNaturalLanguageAdd() {
  app.processNaturalLanguageAdd();
}

// Initialize app when DOM is loaded
let app;
document.addEventListener("DOMContentLoaded", () => {
  app = new QuickLedger();
});
