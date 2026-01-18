// Main application logic
class QuickLedger {
  constructor() {
    this.currentSection = "dashboard";
    this.expenses = [];
    this.stats = {};
    this.currentPage = 1;
    this.itemsPerPage = 10;
    this.totalExpenses = 0;
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
        this.currentPage = 1; // Reset to first page
        this.loadExpenses(1);
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

      // Load comprehensive dashboard data
      const [stats, recentExpenses, weekExpenses, allExpenses] =
        await Promise.all([
          api.getStats(),
          api.getExpenses({ limit: 10 }), // For recent expenses display
          api.getExpenses({ week: true }),
          api.getExpenses({ limit: 1000 }), // For monthly calculations
        ]);

      this.updateEnhancedDashboardStats(
        stats,
        allExpenses.expenses || [],
        weekExpenses.expenses,
      );
      this.updateRecentExpenses(recentExpenses.expenses);
      this.updateDashboardCharts(stats, recentExpenses.expenses);
      this.updateDashboardInsights(stats, recentExpenses.expenses);
      this.updateBudgetTracker(stats);
      this.updateSpendingGoals(stats);
      this.updateRemoveBudgetButton();
    } catch (error) {
      console.error("Error loading dashboard:", error);
      this.showToast("Error loading dashboard data", "error");
    } finally {
      this.hideLoading();
    }
  }

  updateEnhancedDashboardStats(stats, allExpenses, weekExpenses) {
    // Use the backend-calculated monthly spending
    const currentMonth = new Date().toISOString().slice(0, 7);
    const monthlyTotal = stats.current_month_spent || 0;

    document.getElementById("monthly-spent").textContent =
      `₦${this.formatNumber(monthlyTotal)}`;

    // Calculate monthly change using backend monthly_spending data
    const changeElement = document.getElementById("monthly-change");
    const previousMonth = this.getPreviousMonth(currentMonth);
    const monthlySpending = stats.monthly_spending || {};
    const previousMonthTotal = monthlySpending[previousMonth] || 0;

    if (previousMonthTotal > 0) {
      const change =
        ((monthlyTotal - previousMonthTotal) / previousMonthTotal) * 100;
      changeElement.textContent =
        change > 0
          ? `+${change.toFixed(1)}% vs last month`
          : `${change.toFixed(1)}% vs last month`;
      changeElement.className =
        change > 0
          ? "text-xs text-red-200 mt-1"
          : "text-xs text-green-200 mt-1";
    } else {
      changeElement.textContent = "First month tracked";
    }

    // Enhanced daily average with trend
    document.getElementById("daily-average").textContent =
      `₦${this.formatNumber(stats.daily_average)}`;

    const trendElement = document.getElementById("daily-trend");
    const trend = this.calculateSpendingTrend(allExpenses);
    trendElement.textContent = trend;

    // Top category
    const topCategory = stats.most_spent_category;
    document.getElementById("top-category").textContent =
      this.formatCategoryName(topCategory?.name) || "N/A";
    document.getElementById("top-category-amount").textContent =
      `₦${this.formatNumber(topCategory?.amount || 0)} spent`;

    // Week stats
    const weekExpensesArray = Array.isArray(weekExpenses) ? weekExpenses : [];
    const weekTotal = weekExpensesArray.reduce(
      (sum, exp) => sum + parseFloat(exp.amount || 0),
      0,
    );
    document.getElementById("week-spent").textContent = `₦${this.formatNumber(
      weekTotal,
    )}`;
    document.getElementById("week-transactions").textContent =
      `${weekExpensesArray.length} transactions`;
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
      .slice(0, 5)
      .map(
        (expense, index) => `
            <div class="flex justify-between items-center p-3 hover:bg-gray-50 rounded-lg transition-colors">
                <div class="flex items-center space-x-3">
                    <div class="w-10 h-10 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full flex items-center justify-center">
                        <span class="text-white font-semibold text-sm">${expense.expense
                          .charAt(0)
                          .toUpperCase()}</span>
                    </div>
                    <div>
                        <p class="font-medium text-gray-900">${this.formatExpenseName(
                          expense.expense,
                        )}</p>
                        <p class="text-sm text-gray-500">${this.formatDate(
                          expense.date,
                        )} • ${this.getCategoryDisplay(expense.expense)}</p>
                    </div>
                </div>
                <div class="text-right">
                    <span class="font-semibold text-gray-900">₦${this.formatNumber(
                      expense.amount,
                    )}</span>
                    <p class="text-xs text-gray-500">${this.getTimeAgo(
                      expense.date,
                    )}</p>
                </div>
            </div>
        `,
      )
      .join("");
  }

  updateDashboardCharts(stats, expenses) {
    // Create mini trend chart for last 7 days
    this.createDashboardTrendChart(expenses);

    // Update categories display
    this.updateDashboardCategories(stats.top_categories || []);
  }

  createDashboardTrendChart(expenses) {
    const ctx = document.getElementById("dashboard-trend-chart");
    if (!ctx) return;

    // Get last 7 days of data
    const last7Days = this.getLast7DaysData(expenses);

    // Destroy existing chart
    if (this.dashboardTrendChart) {
      this.dashboardTrendChart.destroy();
    }

    const data = {
      labels: last7Days.map((d) => d.label),
      datasets: [
        {
          data: last7Days.map((d) => d.amount),
          borderColor: "#3B82F6",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          borderWidth: 2,
          fill: true,
          tension: 0.4,
          pointRadius: 0,
          pointHoverRadius: 4,
        },
      ],
    };

    this.dashboardTrendChart = new Chart(ctx, {
      type: "line",
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (context) => `₦${this.formatNumber(context.parsed.y)}`,
            },
          },
        },
        scales: {
          x: { display: false },
          y: { display: false },
        },
        elements: {
          point: { radius: 0 },
        },
      },
    });

    // Update trend indicator
    const trendIndicator = document.getElementById("trend-indicator");
    const trend = this.calculateTrendDirection(last7Days);
    trendIndicator.textContent = trend.label;
    trendIndicator.className = `text-sm px-2 py-1 rounded-full ${trend.class}`;
  }

  updateDashboardCategories(categories) {
    const container = document.getElementById("dashboard-categories");
    if (!container) return;

    if (categories.length === 0) {
      container.innerHTML =
        '<p class="text-gray-500 text-sm">No category data yet</p>';
      return;
    }

    const topCategories = categories.slice(0, 4);
    const total = categories.reduce(
      (sum, cat) => sum + (cat.amount || cat.total_amount),
      0,
    );

    container.innerHTML = topCategories
      .map((category) => {
        const amount = category.amount || category.total_amount;
        const percentage = ((amount / total) * 100).toFixed(1);

        return `
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <div class="w-3 h-3 rounded-full bg-blue-500"></div>
            <span class="text-sm font-medium text-gray-700">${this.formatCategoryName(
              category.name,
            )}</span>
          </div>
          <div class="text-right">
            <span class="text-sm font-semibold text-gray-900">₦${this.formatNumber(
              amount,
            )}</span>
            <p class="text-xs text-gray-500">${percentage}%</p>
          </div>
        </div>
      `;
      })
      .join("");
  }

  updateDashboardInsights(stats, expenses) {
    const container = document.getElementById("dashboard-insights");
    if (!container) return;

    const insights = this.generateSmartInsights(stats, expenses);

    container.innerHTML = insights
      .map(
        (insight) => `
      <div class="flex items-start space-x-2 p-2 bg-gray-50 rounded-lg">
        <span class="text-lg">${insight.icon}</span>
        <p class="text-sm text-gray-700">${insight.text}</p>
      </div>
    `,
      )
      .join("");
  }

  async updateBudgetTracker(stats) {
    try {
      const response = await fetch(`${api.baseURL}/budget`);
      const budgetData = await response.json();

      if (budgetData.budget_amount > 0) {
        const percentage = Math.min(budgetData.percentage, 100);
        const remaining = budgetData.remaining;

        document.getElementById("budget-percentage").textContent =
          `${percentage.toFixed(1)}%`;
        document.getElementById("budget-progress").style.width =
          `${percentage}%`;
        document.getElementById("budget-spent").textContent =
          `₦${this.formatNumber(budgetData.spent)}`;
        document.getElementById("budget-limit").textContent =
          `₦${this.formatNumber(budgetData.budget_amount)}`;

        const progressBar = document.getElementById("budget-progress");
        if (percentage > 90) {
          progressBar.className =
            "bg-red-500 h-2 rounded-full transition-all duration-300";
        } else if (percentage > 75) {
          progressBar.className =
            "bg-yellow-500 h-2 rounded-full transition-all duration-300";
        } else {
          progressBar.className =
            "bg-blue-500 h-2 rounded-full transition-all duration-300";
        }

        const statusElement = document.getElementById("budget-status");
        if (budgetData.over_budget) {
          statusElement.textContent = `₦${this.formatNumber(
            Math.abs(remaining),
          )} over budget`;
          statusElement.className = "text-sm text-red-600";
        } else {
          statusElement.textContent = `₦${this.formatNumber(
            remaining,
          )} remaining this month`;
          statusElement.className = "text-sm text-green-600";
        }

        // Show auto-reset indicator if budget was reset
        if (budgetData.reset_from_previous) {
          const resetIndicator = document.createElement("span");
          resetIndicator.className = "text-xs text-blue-600 ml-2";
          resetIndicator.textContent = "(Auto-reset)";
          statusElement.appendChild(resetIndicator);
        }
      } else {
        // No budget set - show current month spending
        const monthlySpent = stats.current_month_spent || 0;
        document.getElementById("budget-percentage").textContent = "0%";
        document.getElementById("budget-progress").style.width = "0%";
        document.getElementById("budget-spent").textContent =
          `₦${this.formatNumber(monthlySpent)}`;
        document.getElementById("budget-limit").textContent = "No budget set";

        const statusElement = document.getElementById("budget-status");
        statusElement.innerHTML = `
          Set a monthly budget to track your spending goals
          <button onclick="setBudget()" class="ml-2 text-blue-600 hover:text-blue-800 text-sm underline">
            Set Budget
          </button>
        `;
        statusElement.className = "text-sm text-gray-600";
      }

      // Update remove button visibility
      this.updateRemoveBudgetButton(budgetData.budget_amount > 0);
    } catch (error) {
      console.error("Error updating budget tracker:", error);
      // Fallback to local storage method for backward compatibility
      this.updateBudgetTrackerFallback(stats);
    }
  }

  updateBudgetTrackerFallback(stats) {
    const budget = this.getBudget();
    const currentMonth = new Date().toISOString().slice(0, 7);
    const monthlySpent = stats.current_month_spent || 0;

    if (budget > 0) {
      const percentage = Math.min((monthlySpent / budget) * 100, 100);
      const remaining = budget - monthlySpent;

      document.getElementById("budget-percentage").textContent =
        `${percentage.toFixed(1)}%`;
      document.getElementById("budget-progress").style.width = `${percentage}%`;
      document.getElementById("budget-spent").textContent =
        `₦${this.formatNumber(monthlySpent)}`;
      document.getElementById("budget-limit").textContent =
        `₦${this.formatNumber(budget)}`;

      const progressBar = document.getElementById("budget-progress");
      if (percentage > 90) {
        progressBar.className =
          "bg-red-500 h-2 rounded-full transition-all duration-300";
      } else if (percentage > 75) {
        progressBar.className =
          "bg-yellow-500 h-2 rounded-full transition-all duration-300";
      } else {
        progressBar.className =
          "bg-blue-500 h-2 rounded-full transition-all duration-300";
      }

      const statusElement = document.getElementById("budget-status");
      if (remaining > 0) {
        statusElement.textContent = `₦${this.formatNumber(
          remaining,
        )} remaining this month`;
        statusElement.className = "text-sm text-green-600";
      } else {
        statusElement.textContent = `₦${this.formatNumber(
          Math.abs(remaining),
        )} over budget`;
        statusElement.className = "text-sm text-red-600";
      }
    } else {
      // No budget set - show current month spending
      const monthlySpent = stats.current_month_spent || 0;
      document.getElementById("budget-percentage").textContent = "0%";
      document.getElementById("budget-progress").style.width = "0%";
      document.getElementById("budget-spent").textContent =
        `₦${this.formatNumber(monthlySpent)}`;
      document.getElementById("budget-limit").textContent = "No budget set";

      const statusElement = document.getElementById("budget-status");
      statusElement.innerHTML = `
        Set a monthly budget to track your spending goals
        <button onclick="setBudget()" class="ml-2 text-blue-600 hover:text-blue-800 text-sm underline">
          Set Budget
        </button>
      `;
      statusElement.className = "text-sm text-gray-600";
      document.getElementById("budget-status").className =
        "text-sm text-gray-600";
    }

    this.updateRemoveBudgetButton(budget > 0);
  }

  updateSpendingGoals(stats) {
    const container = document.getElementById("spending-goals");
    if (!container) return;

    const goals = [
      {
        name: "Daily Limit",
        target: 2000,
        current: stats.daily_average,
        icon: "📅",
      },
      {
        name: "Food Budget",
        target: 15000,
        current:
          stats.top_categories?.find((c) => c.name.toLowerCase() === "food")
            ?.amount || 0,
        icon: "🍽️",
      },
      {
        name: "Transport",
        target: 8000,
        current:
          stats.top_categories?.find(
            (c) => c.name.toLowerCase() === "transport",
          )?.amount || 0,
        icon: "🚗",
      },
    ];

    container.innerHTML = goals
      .map((goal) => {
        const percentage = Math.min((goal.current / goal.target) * 100, 100);
        const status = percentage <= 100 ? "On track" : "Over limit";
        const statusClass =
          percentage <= 100 ? "text-green-600" : "text-red-600";

        return `
        <div class="space-y-2">
          <div class="flex justify-between items-center">
            <span class="text-sm font-medium text-gray-700">${goal.icon} ${
              goal.name
            }</span>
            <span class="text-xs ${statusClass}">${status}</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2">
            <div class="bg-blue-500 h-2 rounded-full transition-all duration-300" style="width: ${Math.min(
              percentage,
              100,
            )}%"></div>
          </div>
          <div class="flex justify-between text-xs text-gray-500">
            <span>₦${this.formatNumber(goal.current)}</span>
            <span>₦${this.formatNumber(goal.target)}</span>
          </div>
        </div>
      `;
      })
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
        "success",
      );

      // Clear input
      document.getElementById("nlp-input").value = "";

      // Refresh dashboard
      await this.loadDashboard();
    } catch (error) {
      console.error("Error processing natural language:", error);
      this.showToast(
        "Error processing text. Please try a different format.",
        "error",
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
        "success",
      );

      // Clear input
      document.getElementById("nlp-text").value = "";
    } catch (error) {
      console.error("Error processing natural language:", error);
      this.showToast(
        "Error processing text. Please try a different format.",
        "error",
      );
    } finally {
      this.hideLoading();
    }
  }

  async loadExpenses(page = 1) {
    try {
      this.showLoading();
      this.currentPage = page;

      const filter = document.getElementById("expense-filter").value;
      let params = {
        limit: 1000, // Get more data to handle pagination client-side
        offset: 0,
      };

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
      this.allExpenses = result.expenses || [];
      this.originalExpenses = [...this.allExpenses]; // Store original for filtering
      this.totalExpenses = this.allExpenses.length;

      // Reset enhanced features filters when loading new data
      if (window.enhancedFeatures) {
        window.enhancedFeatures.searchTerm = "";
        window.enhancedFeatures.filters = {
          category: "",
          amount: "",
          date: filter || "all",
        };

        // Clear search input
        const searchInput = document.getElementById("expense-search");
        if (searchInput) searchInput.value = "";

        // Reset filter selects
        const categoryFilter = document.getElementById("category-filter");
        const amountFilter = document.getElementById("amount-filter");
        if (categoryFilter) categoryFilter.value = "";
        if (amountFilter) amountFilter.value = "";
      }

      // Calculate pagination
      const startIndex = (this.currentPage - 1) * this.itemsPerPage;
      const endIndex = startIndex + this.itemsPerPage;
      const paginatedExpenses = this.allExpenses.slice(startIndex, endIndex);

      this.displayExpenses(paginatedExpenses);
      this.updatePagination();

      // Update count
      const countElement = document.getElementById("expense-count");
      if (countElement) {
        countElement.textContent = `${
          this.totalExpenses
        } expense${this.totalExpenses !== 1 ? "s" : ""}`;
      }
    } catch (error) {
      console.error("Error loading expenses:", error);
      this.showToast("Error loading expenses", "error");
    } finally {
      this.hideLoading();
    }
  }

  displayExpenses(expenses) {
    const tableBody = document.getElementById("expenses-table-body");
    const emptyState = document.getElementById("expenses-empty");

    if (!tableBody || !emptyState) return;

    if (expenses.length === 0) {
      tableBody.innerHTML = "";
      emptyState.classList.remove("hidden");
      return;
    }

    emptyState.classList.add("hidden");

    tableBody.innerHTML = expenses
      .map((expense, index) => {
        const expenseId = `${expense.date}-${expense.index || index}`;
        const highlightedExpense = this.highlightSearchTerm(expense.expense);

        return `
            <tr class="hover:bg-gray-50 transition-colors expense-table-row">
                <td class="px-6 py-4 whitespace-nowrap">
                    <input
                        type="checkbox"
                        class="expense-checkbox rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        data-expense-id="${expenseId}"
                        onchange="toggleExpenseSelection(this)"
                    />
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <div class="flex items-center">
                        <div class="w-10 h-10 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full flex items-center justify-center mr-3">
                            <span class="text-white font-semibold text-sm">${expense.expense
                              .charAt(0)
                              .toUpperCase()}</span>
                        </div>
                        <div>
                            <div class="text-sm font-medium text-gray-900">${highlightedExpense}</div>
                            <div class="text-sm text-gray-500">${this.getTimeAgo(
                              expense.date,
                            )}</div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        ${this.getCategoryDisplay(expense.expense)}
                    </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${this.formatDate(expense.date)}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right">
                    <div class="text-sm font-semibold text-gray-900">₦${this.formatNumber(
                      expense.amount,
                    )}</div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                    <div class="flex justify-center space-x-2">
                        <button 
                            onclick="app.editExpense('${
                              expense.date
                            }', ${expense.index || index})" 
                            class="text-blue-600 hover:text-blue-800 p-1 rounded-md hover:bg-blue-50 transition-colors action-button"
                            title="Edit expense"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                        </button>
                        <button 
                            onclick="app.deleteExpense('${
                              expense.date
                            }', ${expense.index || index})" 
                            class="text-red-600 hover:text-red-800 p-1 rounded-md hover:bg-red-50 transition-colors action-button"
                            title="Delete expense"
                        >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                            </svg>
                        </button>
                    </div>
                </td>
            </tr>
        `;
      })
      .join("");
  }

  async loadAnalytics() {
    try {
      this.showLoading();

      // Load both stats and recent expenses for comprehensive analytics
      const [stats, expenses] = await Promise.all([
        api.getStats(),
        api.getExpenses({ limit: 100 }),
      ]);

      this.displayEnhancedAnalytics(stats, expenses.expenses);
      this.populateMonthSelector(stats.monthly_spending || {});

      // Load current month breakdown by default
      const currentMonth = new Date().toISOString().slice(0, 7);
      await this.loadMonthlyBreakdown(currentMonth);
    } catch (error) {
      console.error("Error loading analytics:", error);
      this.showToast("Error loading analytics", "error");
    } finally {
      this.hideLoading();
    }
  }

  populateMonthSelector(monthlySpending) {
    const selector = document.getElementById("month-selector");
    if (!selector) return;

    const months = Object.keys(monthlySpending).sort().reverse();
    const currentMonth = new Date().toISOString().slice(0, 7);

    // Add current month if not in list
    if (!months.includes(currentMonth)) {
      months.unshift(currentMonth);
    }

    selector.innerHTML = months
      .map((month) => {
        const date = new Date(month + "-01");
        const label = date.toLocaleDateString("en-NG", {
          year: "numeric",
          month: "long",
        });
        return `<option value="${month}" ${
          month === currentMonth ? "selected" : ""
        }>${label}</option>`;
      })
      .join("");
  }

  async loadMonthlyBreakdown(month) {
    const container = document.getElementById("monthly-breakdown-content");

    if (!container) {
      console.error("Monthly breakdown container not found");
      return;
    }

    // Show loading state
    container.innerHTML = `
      <div class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-2"></div>
        <p class="text-gray-500">Loading monthly data...</p>
      </div>
    `;

    try {
      const response = await fetch(`${api.baseURL}/monthly/${month}`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      this.displayMonthlyBreakdown(data);
    } catch (error) {
      console.error("Error loading monthly breakdown:", error);
      this.showToast("Error loading monthly data", "error");

      // Show error in the container
      container.innerHTML = `
        <div class="text-center py-8">
          <p class="text-red-600 mb-2">Failed to load monthly data</p>
          <p class="text-gray-500 text-sm">${error.message}</p>
        </div>
      `;
    }
  }

  displayMonthlyBreakdown(data) {
    const container = document.getElementById("monthly-breakdown-content");
    if (!container) return;

    const categories = Object.entries(data.categories || {}).sort(
      (a, b) => b[1] - a[1],
    );

    container.innerHTML = `
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div class="bg-blue-50 rounded-lg p-4">
          <p class="text-sm text-blue-600 font-medium">Total Spent</p>
          <p class="text-2xl font-bold text-blue-900">₦${this.formatNumber(
            data.total_spent,
          )}</p>
          <p class="text-xs text-blue-600 mt-1">${
            data.transaction_count
          } transactions</p>
        </div>
        <div class="bg-green-50 rounded-lg p-4">
          <p class="text-sm text-green-600 font-medium">Daily Average</p>
          <p class="text-2xl font-bold text-green-900">₦${this.formatNumber(
            data.daily_average,
          )}</p>
          <p class="text-xs text-green-600 mt-1">${
            data.days_tracked
          } days tracked</p>
        </div>
        <div class="bg-purple-50 rounded-lg p-4">
          <p class="text-sm text-purple-600 font-medium">Top Category</p>
          <p class="text-2xl font-bold text-purple-900">${
            categories.length > 0
              ? this.formatCategoryName(categories[0][0])
              : "N/A"
          }</p>
          <p class="text-xs text-purple-600 mt-1">${
            categories.length > 0
              ? "₦" + this.formatNumber(categories[0][1])
              : "No data"
          }</p>
        </div>
      </div>

      <div class="mb-6">
        <h4 class="text-md font-semibold text-gray-900 mb-4">Spending by Category</h4>
        <div class="space-y-3">
          ${
            categories.length > 0
              ? categories
                  .map((cat) => {
                    const [name, amount] = cat;
                    const percentage = (
                      (amount / data.total_spent) *
                      100
                    ).toFixed(1);
                    return `
                    <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div class="flex-1">
                        <div class="flex justify-between items-center mb-1">
                          <span class="font-medium text-gray-900">${this.formatCategoryName(
                            name,
                          )}</span>
                          <span class="text-sm font-semibold text-gray-900">₦${this.formatNumber(
                            amount,
                          )}</span>
                        </div>
                        <div class="w-full bg-gray-200 rounded-full h-2">
                          <div class="bg-blue-500 h-2 rounded-full" style="width: ${percentage}%"></div>
                        </div>
                        <p class="text-xs text-gray-500 mt-1">${percentage}% of total</p>
                      </div>
                    </div>
                  `;
                  })
                  .join("")
              : '<p class="text-gray-500 text-center py-4">No expenses for this month</p>'
          }
        </div>
      </div>

      <div>
        <h4 class="text-md font-semibold text-gray-900 mb-4">Top Expenses</h4>
        <div class="space-y-2">
          ${
            data.top_expenses && data.top_expenses.length > 0
              ? data.top_expenses
                  .map(
                    (exp, index) => `
                  <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center space-x-3">
                      <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span class="text-blue-600 font-bold text-sm">${
                          index + 1
                        }</span>
                      </div>
                      <span class="font-medium text-gray-900">${this.formatExpenseName(
                        exp.name,
                      )}</span>
                    </div>
                    <span class="font-semibold text-gray-900">₦${this.formatNumber(
                      exp.amount,
                    )}</span>
                  </div>
                `,
                  )
                  .join("")
              : '<p class="text-gray-500 text-center py-4">No expenses for this month</p>'
          }
        </div>
      </div>
    `;
  }

  displayEnhancedAnalytics(stats, expenses) {
    // Update key metrics cards
    document.getElementById("analytics-total-spent").textContent =
      `₦${this.formatNumber(stats.total_spent)}`;
    document.getElementById("analytics-daily-avg").textContent =
      `₦${this.formatNumber(stats.daily_average)}`;
    document.getElementById("analytics-top-category").textContent =
      this.formatCategoryName(stats.most_spent_category?.name) || "N/A";
    document.getElementById("analytics-transactions").textContent =
      stats.transaction_count.toLocaleString();

    // Process expenses for additional analytics
    const processedData = this.processExpensesForAnalytics(expenses);

    // Update all charts
    this.updateEnhancedCharts(stats, processedData);

    // Update insights
    this.updateSpendingInsights(stats, processedData);

    // Update top expenses list
    this.updateTopExpensesList(stats.top_expenses || []);

    // Update detailed stats table
    this.updateDetailedStatsTable(stats, processedData);
  }

  processExpensesForAnalytics(expenses) {
    const dailyData = {};
    const monthlyData = {};
    const categoryData = {};

    expenses.forEach((expense) => {
      const date = expense.date;
      const amount = parseFloat(expense.amount);
      const category = this.getCategoryDisplay(expense.expense);
      const month = date.substring(0, 7); // YYYY-MM

      // Daily data
      dailyData[date] = (dailyData[date] || 0) + amount;

      // Monthly data
      monthlyData[month] = (monthlyData[month] || 0) + amount;

      // Category data
      categoryData[category] = (categoryData[category] || 0) + amount;
    });

    return {
      dailyData,
      monthlyData,
      categoryData,
      totalExpenses: expenses.length,
    };
  }

  updateEnhancedCharts(stats, processedData) {
    // Update existing charts
    if (stats.top_categories && stats.top_categories.length > 0) {
      charts.updateCategoryChart(stats.top_categories);
      charts.createCategoryComparisonChart(stats.top_categories);
    }

    // Create new charts
    if (Object.keys(processedData.dailyData).length > 0) {
      charts.createTrendChart(processedData.dailyData);
    }

    if (Object.keys(processedData.monthlyData).length > 0) {
      charts.createMonthlyChart(processedData.monthlyData);
    }
  }

  updateSpendingInsights(stats, processedData) {
    const insights = [];

    // Food spending insight
    const foodCategory = stats.top_categories?.find(
      (cat) => cat.name.toLowerCase() === "food",
    );
    if (foodCategory) {
      const foodPercentage = (
        (foodCategory.amount / stats.total_spent) *
        100
      ).toFixed(1);
      insights.push({
        icon: "🍽️",
        text: `Food represents ${foodPercentage}% of your total spending (₦${this.formatNumber(
          foodCategory.amount,
        )})`,
      });
    }

    // Daily average insight
    const avgDaily = stats.daily_average;
    if (avgDaily > 2000) {
      insights.push({
        icon: "📈",
        text: `Your daily average of ₦${this.formatNumber(
          avgDaily,
        )} is quite high. Consider tracking smaller expenses.`,
      });
    } else if (avgDaily < 500) {
      insights.push({
        icon: "💡",
        text: `Great job keeping daily spending low at ₦${this.formatNumber(
          avgDaily,
        )} average!`,
      });
    }

    // Transaction frequency insight
    if (stats.transaction_count > 50) {
      insights.push({
        icon: "🔄",
        text: `You have ${stats.transaction_count} transactions. Consider consolidating similar expenses.`,
      });
    }

    // Most expensive day insight
    if (stats.most_expensive_day) {
      insights.push({
        icon: "📅",
        text: `Your highest spending day was ${
          stats.most_expensive_day.date
        } with ₦${this.formatNumber(stats.most_expensive_day.amount)}`,
      });
    }

    // Render insights
    const container = document.getElementById("spending-insights");
    if (container) {
      container.innerHTML = insights
        .map(
          (insight) => `
        <div class="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
          <span class="text-2xl">${insight.icon}</span>
          <p class="text-sm text-gray-700">${insight.text}</p>
        </div>
      `,
        )
        .join("");
    }
  }

  updateTopExpensesList(topExpenses) {
    const container = document.getElementById("top-expenses-list");
    if (!container) return;

    if (topExpenses.length === 0) {
      container.innerHTML =
        '<p class="text-gray-500 text-center">No expense data available</p>';
      return;
    }

    container.innerHTML = topExpenses
      .slice(0, 5)
      .map(
        (expense, index) => `
      <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
        <div class="flex items-center space-x-3">
          <div class="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
            <span class="text-orange-600 font-bold text-sm">${index + 1}</span>
          </div>
          <div>
            <p class="font-medium text-gray-900">${this.formatExpenseName(
              expense.name,
            )}</p>
            <p class="text-sm text-gray-500">${expense.count || 1} transaction${
              (expense.count || 1) > 1 ? "s" : ""
            }</p>
          </div>
        </div>
        <span class="font-semibold text-gray-900">₦${this.formatNumber(
          expense.total_amount || expense.amount,
        )}</span>
      </div>
    `,
      )
      .join("");
  }

  updateDetailedStatsTable(stats, processedData) {
    const container = document.getElementById("detailed-stats-table");
    if (!container) return;

    const tableData = [
      {
        metric: "Total Spent",
        value: `₦${this.formatNumber(stats.total_spent)}`,
        details: "All time",
      },
      {
        metric: "Daily Average",
        value: `₦${this.formatNumber(stats.daily_average)}`,
        details: "Based on active days",
      },
      {
        metric: "Transaction Count",
        value: stats.transaction_count.toLocaleString(),
        details: "Total entries",
      },
      {
        metric: "Days Tracked",
        value: stats.days_tracked.toLocaleString(),
        details: "Days with expenses",
      },
      {
        metric: "Top Category",
        value:
          this.formatCategoryName(stats.most_spent_category?.name) || "N/A",
        details: `₦${this.formatNumber(
          stats.most_spent_category?.amount || 0,
        )}`,
      },
      {
        metric: "Most Frequent Expense",
        value:
          this.formatExpenseName(stats.most_frequent_expense?.name) || "N/A",
        details: `${stats.most_frequent_expense?.count || 0} times`,
      },
      {
        metric: "Highest Spending Day",
        value: stats.most_expensive_day?.date || "N/A",
        details: `₦${this.formatNumber(stats.most_expensive_day?.amount || 0)}`,
      },
      {
        metric: "Average per Transaction",
        value: `₦${this.formatNumber(
          stats.total_spent / stats.transaction_count,
        )}`,
        details: "Per expense entry",
      },
    ];

    container.innerHTML = tableData
      .map(
        (row) => `
      <tr>
        <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${row.metric}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${row.value}</td>
        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${row.details}</td>
      </tr>
    `,
      )
      .join("");
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

  // Enhanced utility methods
  formatNumber(num) {
    return new Intl.NumberFormat("en-NG").format(num);
  }

  highlightSearchTerm(text) {
    if (!window.enhancedFeatures || !window.enhancedFeatures.searchTerm) {
      return this.formatExpenseName(text);
    }

    const searchTerm = window.enhancedFeatures.searchTerm;
    const formattedText = this.formatExpenseName(text);
    const regex = new RegExp(`(${searchTerm})`, "gi");
    return formattedText.replace(
      regex,
      '<span class="search-highlight">$1</span>',
    );
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-NG", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  }

  formatExpenseName(name) {
    if (!name) return "N/A";
    return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
  }

  formatCategoryName(name) {
    if (!name) return "N/A";
    return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
  }

  getTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return "Today";
    if (diffDays === 2) return "Yesterday";
    if (diffDays <= 7) return `${diffDays - 1} days ago`;
    return this.formatDate(dateString);
  }

  calculateSpendingTrend(expenses) {
    if (expenses.length < 7) return "building trend...";

    const recent =
      expenses
        .slice(0, 3)
        .reduce((sum, exp) => sum + parseFloat(exp.amount), 0) / 3;
    const older =
      expenses
        .slice(3, 6)
        .reduce((sum, exp) => sum + parseFloat(exp.amount), 0) / 3;

    if (recent > older * 1.1) return "trending up";
    if (recent < older * 0.9) return "trending down";
    return "stable";
  }

  getLast7DaysData(expenses) {
    const days = [];
    const today = new Date();

    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split("T")[0];

      const dayExpenses = expenses.filter((exp) => exp.date === dateStr);
      const total = dayExpenses.reduce(
        (sum, exp) => sum + parseFloat(exp.amount),
        0,
      );

      days.push({
        date: dateStr,
        label: date.toLocaleDateString("en-NG", { weekday: "short" }),
        amount: total,
      });
    }

    return days;
  }

  calculateTrendDirection(last7Days) {
    const amounts = last7Days.map((d) => d.amount);
    const firstHalf = amounts.slice(0, 3).reduce((a, b) => a + b, 0) / 3;
    const secondHalf = amounts.slice(4).reduce((a, b) => a + b, 0) / 3;

    if (secondHalf > firstHalf * 1.2) {
      return { label: "Rising", class: "bg-red-100 text-red-600" };
    } else if (secondHalf < firstHalf * 0.8) {
      return { label: "Falling", class: "bg-green-100 text-green-600" };
    } else {
      return { label: "Stable", class: "bg-gray-100 text-gray-600" };
    }
  }

  generateSmartInsights(stats, expenses) {
    const insights = [];

    // Spending pattern insight
    if (stats.daily_average > 1500) {
      insights.push({
        icon: "💡",
        text: `Your daily average of ₦${this.formatNumber(
          stats.daily_average,
        )} is above typical range`,
      });
    }

    // Category insight
    const topCategory = stats.most_spent_category;
    if (topCategory) {
      const percentage = (
        (topCategory.amount / stats.total_spent) *
        100
      ).toFixed(0);
      insights.push({
        icon: "📊",
        text: `${this.formatCategoryName(
          topCategory.name,
        )} accounts for ${percentage}% of your spending`,
      });
    }

    // Frequency insight
    if (stats.transaction_count > 30) {
      insights.push({
        icon: "🔄",
        text: `You have ${stats.transaction_count} transactions - consider consolidating similar expenses`,
      });
    }

    // Recent activity insight
    const recentExpenses = expenses.slice(0, 3);
    if (recentExpenses.length > 0) {
      const recentTotal = recentExpenses.reduce(
        (sum, exp) => sum + parseFloat(exp.amount),
        0,
      );
      insights.push({
        icon: "⚡",
        text: `₦${this.formatNumber(
          recentTotal,
        )} spent in your last 3 transactions`,
      });
    }

    return insights.slice(0, 3); // Show max 3 insights
  }

  getBudget() {
    return parseFloat(localStorage.getItem("monthlyBudget") || "0");
  }

  getPreviousMonth(currentMonth) {
    const date = new Date(currentMonth + "-01");
    date.setMonth(date.getMonth() - 1);
    return date.toISOString().slice(0, 7);
  }

  updatePagination() {
    const totalPages = Math.ceil(this.totalExpenses / this.itemsPerPage);
    const startItem = (this.currentPage - 1) * this.itemsPerPage + 1;
    const endItem = Math.min(
      this.currentPage * this.itemsPerPage,
      this.totalExpenses,
    );

    // Update pagination info
    document.getElementById("page-start").textContent =
      this.totalExpenses > 0 ? startItem : 0;
    document.getElementById("page-end").textContent = endItem;
    document.getElementById("total-expenses").textContent = this.totalExpenses;

    // Update pagination buttons
    const prevBtn = document.getElementById("prev-page");
    const nextBtn = document.getElementById("next-page");
    const prevBtnMobile = document.getElementById("prev-page-mobile");
    const nextBtnMobile = document.getElementById("next-page-mobile");

    if (prevBtn && nextBtn && prevBtnMobile && nextBtnMobile) {
      prevBtn.disabled = this.currentPage <= 1;
      nextBtn.disabled = this.currentPage >= totalPages;
      prevBtnMobile.disabled = this.currentPage <= 1;
      nextBtnMobile.disabled = this.currentPage >= totalPages;
    }

    // Update page numbers
    this.updatePageNumbers(totalPages);

    // Show/hide pagination
    const paginationElement = document.getElementById("expenses-pagination");
    if (paginationElement) {
      if (this.totalExpenses <= this.itemsPerPage) {
        paginationElement.style.display = "none";
      } else {
        paginationElement.style.display = "block";
      }
    }
  }

  updatePageNumbers(totalPages) {
    const pageNumbersContainer = document.getElementById("page-numbers");
    if (!pageNumbersContainer) return;

    pageNumbersContainer.innerHTML = "";

    // Show max 5 page numbers
    let startPage = Math.max(1, this.currentPage - 2);
    let endPage = Math.min(totalPages, startPage + 4);

    if (endPage - startPage < 4) {
      startPage = Math.max(1, endPage - 4);
    }

    for (let i = startPage; i <= endPage; i++) {
      const pageButton = document.createElement("button");
      pageButton.textContent = i;
      pageButton.onclick = () => this.changePage(i);

      if (i === this.currentPage) {
        pageButton.className =
          "relative inline-flex items-center px-4 py-2 border border-blue-500 bg-blue-50 text-sm font-medium text-blue-600";
      } else {
        pageButton.className =
          "relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50";
      }

      pageNumbersContainer.appendChild(pageButton);
    }
  }

  changePage(direction) {
    let newPage = this.currentPage;

    if (direction === "prev") {
      newPage = Math.max(1, this.currentPage - 1);
    } else if (direction === "next") {
      const totalPages = Math.ceil(this.totalExpenses / this.itemsPerPage);
      newPage = Math.min(totalPages, this.currentPage + 1);
    } else if (typeof direction === "number") {
      newPage = direction;
    }

    if (newPage !== this.currentPage) {
      this.loadExpenses(newPage);
    }
  }

  async setBudget() {
    const budget = prompt("Set your monthly budget (₦):");
    if (budget && !isNaN(budget) && parseFloat(budget) > 0) {
      try {
        const response = await fetch(`${api.baseURL}/budget?amount=${budget}`, {
          method: "POST",
        });

        if (response.ok) {
          const result = await response.json();
          this.showToast("Budget updated successfully!", "success");
          // Refresh the dashboard to show updated budget
          this.loadDashboard();
        } else {
          throw new Error("Failed to set budget");
        }
      } catch (error) {
        console.error("Error setting budget:", error);
        // Fallback to localStorage for backward compatibility
        localStorage.setItem("monthlyBudget", budget);
        this.updateBudgetTracker({ total_spent: 0 });
        this.showToast(
          "Budget updated successfully! (Local storage)",
          "success",
        );
        this.updateRemoveBudgetButton(true);
      }
    }
  }

  async removeBudget() {
    if (confirm("Are you sure you want to remove your monthly budget?")) {
      try {
        const response = await fetch(`${api.baseURL}/budget`, {
          method: "DELETE",
        });

        if (response.ok) {
          this.showToast("Budget removed successfully!", "success");
          // Refresh the dashboard to show updated budget
          this.loadDashboard();
        } else {
          throw new Error("Failed to remove budget");
        }
      } catch (error) {
        console.error("Error removing budget:", error);
        // Fallback to localStorage for backward compatibility
        localStorage.removeItem("monthlyBudget");
        this.updateBudgetTracker({ total_spent: 0 });
        this.showToast(
          "Budget removed successfully! (Local storage)",
          "success",
        );
        this.updateRemoveBudgetButton(false);
      }
    }
  }

  updateRemoveBudgetButton(hasBudget = null) {
    const removeBtn = document.getElementById("remove-budget-btn");

    if (removeBtn) {
      if (hasBudget === null) {
        // Check both API and localStorage
        const localBudget = this.getBudget();
        hasBudget = localBudget > 0;
      }

      if (hasBudget) {
        removeBtn.classList.remove("hidden");
      } else {
        removeBtn.classList.add("hidden");
      }
    }
  }

  getCategoryDisplay(expenseName) {
    // Simple category mapping for display - this could be enhanced
    // to call the backend for actual category determination
    const expense = expenseName.toLowerCase();

    // Basic category detection for display purposes
    if (
      [
        "food",
        "lunch",
        "dinner",
        "breakfast",
        "snacks",
        "bread",
        "rice",
        "fish",
        "milk",
        "soup",
        "pear",
        "ice",
      ].some((keyword) => expense.includes(keyword))
    ) {
      return "Food";
    } else if (
      ["transport", "fuel", "taxi", "bus", "uber"].some((keyword) =>
        expense.includes(keyword),
      )
    ) {
      return "Transport";
    } else if (
      ["data", "airtime", "internet"].some((keyword) =>
        expense.includes(keyword),
      )
    ) {
      return "Data";
    } else if (
      ["electricity", "water", "gas", "phone"].some((keyword) =>
        expense.includes(keyword),
      )
    ) {
      return "Utilities";
    } else {
      return "Other";
    }
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

function switchQuickTab(tab) {
  const simpleTab = document.getElementById("simple-tab");
  const smartTab = document.getElementById("smart-tab");
  const simpleAdd = document.getElementById("simple-quick-add");
  const smartAdd = document.getElementById("smart-quick-add");

  if (tab === "simple") {
    simpleTab.className =
      "flex-1 py-2 px-3 rounded-md text-sm font-medium bg-white text-gray-900 shadow-sm";
    smartTab.className =
      "flex-1 py-2 px-3 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900";
    simpleAdd.classList.remove("hidden");
    smartAdd.classList.add("hidden");
  } else {
    smartTab.className =
      "flex-1 py-2 px-3 rounded-md text-sm font-medium bg-white text-gray-900 shadow-sm";
    simpleTab.className =
      "flex-1 py-2 px-3 rounded-md text-sm font-medium text-gray-600 hover:text-gray-900";
    smartAdd.classList.remove("hidden");
    simpleAdd.classList.add("hidden");
  }
}

function quickExpenseButton(name, amount) {
  document.getElementById("quick-expense").value = name;
  document.getElementById("quick-amount").value = amount;
  app.quickAddExpense();
}

function setBudget() {
  app.setBudget();
}

function removeBudget() {
  app.removeBudget();
}

function changePage(direction) {
  app.changePage(direction);
}

function loadMonthlyBreakdown(month) {
  if (app) {
    app.loadMonthlyBreakdown(month);
  }
}

// Initialize app when DOM is loaded
let app;
document.addEventListener("DOMContentLoaded", () => {
  app = new QuickLedger();
});
