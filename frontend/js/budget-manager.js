// Enhanced Budget Management System
class BudgetManager {
  constructor() {
    this.budgets = {
      monthly: 0,
      categories: {},
      weekly: 0,
    };
    this.init();
  }

  init() {
    this.loadBudgets();
    this.setupEventListeners();
  }

  loadBudgets() {
    // Load from localStorage for now (can be enhanced to use API)
    const savedBudgets = localStorage.getItem("quickledger-budgets");
    if (savedBudgets) {
      this.budgets = { ...this.budgets, ...JSON.parse(savedBudgets) };
    }
  }

  saveBudgets() {
    localStorage.setItem("quickledger-budgets", JSON.stringify(this.budgets));
  }

  setupEventListeners() {
    // Enhanced budget modal will be added here
  }

  async showBudgetModal() {
    const modal = this.createBudgetModal();
    document.body.appendChild(modal);
    modal.classList.remove("hidden");
    modal.classList.add("fade-in");
  }

  createBudgetModal() {
    const modal = document.createElement("div");
    modal.id = "budget-modal";
    modal.className =
      "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50";

    modal.innerHTML = `
      <div class="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 modal-content">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-xl font-semibold text-gray-900">Budget Management</h3>
          <button onclick="budgetManager.closeBudgetModal()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="space-y-6">
          <!-- Monthly Budget -->
          <div class="border rounded-lg p-4">
            <h4 class="text-lg font-medium text-gray-900 mb-3">Monthly Budget</h4>
            <div class="flex items-center space-x-4">
              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-1">Amount (₦)</label>
                <input
                  type="number"
                  id="monthly-budget-input"
                  value="${this.budgets.monthly}"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter monthly budget"
                />
              </div>
              <button
                onclick="budgetManager.setMonthlyBudget()"
                class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
              >
                Set Budget
              </button>
            </div>
          </div>

          <!-- Category Budgets -->
          <div class="border rounded-lg p-4">
            <h4 class="text-lg font-medium text-gray-900 mb-3">Category Budgets</h4>
            <div class="space-y-3">
              ${this.renderCategoryBudgets()}
            </div>
            <button
              onclick="budgetManager.addCategoryBudget()"
              class="mt-3 text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              + Add Category Budget
            </button>
          </div>

          <!-- Weekly Budget -->
          <div class="border rounded-lg p-4">
            <h4 class="text-lg font-medium text-gray-900 mb-3">Weekly Budget</h4>
            <div class="flex items-center space-x-4">
              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-1">Amount (₦)</label>
                <input
                  type="number"
                  id="weekly-budget-input"
                  value="${this.budgets.weekly}"
                  class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter weekly budget"
                />
              </div>
              <button
                onclick="budgetManager.setWeeklyBudget()"
                class="bg-green-500 text-white px-4 py-2 rounded-md hover:bg-green-600 transition-colors"
              >
                Set Budget
              </button>
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-3 mt-6 pt-4 border-t">
          <button
            onclick="budgetManager.closeBudgetModal()"
            class="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
          >
            Close
          </button>
          <button
            onclick="budgetManager.resetAllBudgets()"
            class="bg-red-500 text-white px-4 py-2 rounded-md hover:bg-red-600 transition-colors"
          >
            Reset All
          </button>
        </div>
      </div>
    `;

    return modal;
  }

  renderCategoryBudgets() {
    const categories = ["food", "transport", "data", "utilities", "other"];
    return categories
      .map((category) => {
        const budget = this.budgets.categories[category] || 0;
        return `
        <div class="flex items-center space-x-4">
          <div class="w-20">
            <span class="text-sm font-medium text-gray-700 capitalize">${category}</span>
          </div>
          <div class="flex-1">
            <input
              type="number"
              id="category-budget-${category}"
              value="${budget}"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Budget amount"
            />
          </div>
          <button
            onclick="budgetManager.setCategoryBudget('${category}')"
            class="bg-purple-500 text-white px-3 py-1 rounded text-sm hover:bg-purple-600 transition-colors"
          >
            Set
          </button>
        </div>
      `;
      })
      .join("");
  }

  closeBudgetModal() {
    const modal = document.getElementById("budget-modal");
    if (modal) {
      modal.classList.add("hidden");
      document.body.removeChild(modal);
    }
  }

  setMonthlyBudget() {
    const input = document.getElementById("monthly-budget-input");
    const amount = parseFloat(input.value);

    if (isNaN(amount) || amount < 0) {
      window.app.showToast("Please enter a valid budget amount", "error");
      return;
    }

    this.budgets.monthly = amount;
    this.saveBudgets();
    window.app.showToast("Monthly budget updated successfully!", "success");

    // Update the dashboard if we're on it
    if (window.app && window.app.currentSection === "dashboard") {
      window.app.loadDashboard();
    }
  }

  setCategoryBudget(category) {
    const input = document.getElementById(`category-budget-${category}`);
    const amount = parseFloat(input.value);

    if (isNaN(amount) || amount < 0) {
      window.app.showToast("Please enter a valid budget amount", "error");
      return;
    }

    this.budgets.categories[category] = amount;
    this.saveBudgets();
    window.app.showToast(
      `${category.charAt(0).toUpperCase() + category.slice(1)} budget updated!`,
      "success",
    );
  }

  setWeeklyBudget() {
    const input = document.getElementById("weekly-budget-input");
    const amount = parseFloat(input.value);

    if (isNaN(amount) || amount < 0) {
      window.app.showToast("Please enter a valid budget amount", "error");
      return;
    }

    this.budgets.weekly = amount;
    this.saveBudgets();
    window.app.showToast("Weekly budget updated successfully!", "success");
  }

  resetAllBudgets() {
    if (
      confirm(
        "Are you sure you want to reset all budgets? This action cannot be undone.",
      )
    ) {
      this.budgets = {
        monthly: 0,
        categories: {},
        weekly: 0,
      };
      this.saveBudgets();
      window.app.showToast("All budgets have been reset", "success");
      this.closeBudgetModal();

      // Refresh dashboard
      if (window.app && window.app.currentSection === "dashboard") {
        window.app.loadDashboard();
      }
    }
  }

  // Enhanced budget tracking with category support
  async updateEnhancedBudgetTracker(stats) {
    const container = document.getElementById("budget-tracker");
    if (!container) return;

    const currentMonth = new Date().toISOString().slice(0, 7);
    const monthlySpent = stats.current_month_spent || 0;
    const monthlyBudget = this.budgets.monthly;

    if (monthlyBudget > 0) {
      const percentage = Math.min((monthlySpent / monthlyBudget) * 100, 100);
      const remaining = monthlyBudget - monthlySpent;

      // Update main budget display
      document.getElementById("budget-percentage").textContent =
        `${percentage.toFixed(1)}%`;
      document.getElementById("budget-progress").style.width = `${percentage}%`;
      document.getElementById("budget-spent").textContent =
        `₦${window.app.formatNumber(monthlySpent)}`;
      document.getElementById("budget-limit").textContent =
        `₦${window.app.formatNumber(monthlyBudget)}`;

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
        statusElement.textContent = `₦${window.app.formatNumber(remaining)} remaining this month`;
        statusElement.className = "text-sm text-green-600";
      } else {
        statusElement.textContent = `₦${window.app.formatNumber(Math.abs(remaining))} over budget`;
        statusElement.className = "text-sm text-red-600";
      }

      // Add category budget warnings if any category is over budget
      this.addCategoryBudgetWarnings(stats);
    } else {
      // No budget set
      document.getElementById("budget-percentage").textContent = "0%";
      document.getElementById("budget-progress").style.width = "0%";
      document.getElementById("budget-spent").textContent =
        `₦${window.app.formatNumber(monthlySpent)}`;
      document.getElementById("budget-limit").textContent = "No budget set";
      document.getElementById("budget-status").innerHTML = `
        Set a monthly budget to track your spending goals
        <button onclick="budgetManager.showBudgetModal()" class="ml-2 text-blue-600 hover:text-blue-800 text-sm underline">
          Set Budget
        </button>
      `;
      document.getElementById("budget-status").className =
        "text-sm text-gray-600";
    }
  }

  addCategoryBudgetWarnings(stats) {
    const categories = stats.current_month_categories || {};
    const warnings = [];

    Object.entries(this.budgets.categories).forEach(([category, budget]) => {
      if (budget > 0) {
        const spent = categories[category] || 0;
        const percentage = (spent / budget) * 100;

        if (percentage > 90) {
          warnings.push({
            category: category,
            percentage: percentage.toFixed(1),
            spent: spent,
            budget: budget,
            over: spent > budget,
          });
        }
      }
    });

    if (warnings.length > 0) {
      const warningContainer = document.createElement("div");
      warningContainer.className = "mt-3 space-y-1";

      warnings.forEach((warning) => {
        const warningDiv = document.createElement("div");
        warningDiv.className = `text-xs ${warning.over ? "text-red-600" : "text-yellow-600"}`;
        warningDiv.textContent = `${warning.category.charAt(0).toUpperCase() + warning.category.slice(1)}: ${warning.over ? "Over" : "Near"} budget (${warning.percentage}%)`;
        warningContainer.appendChild(warningDiv);
      });

      const statusElement = document.getElementById("budget-status");
      statusElement.appendChild(warningContainer);
    }
  }

  // Get budget information for a specific category
  getCategoryBudget(category) {
    return this.budgets.categories[category.toLowerCase()] || 0;
  }

  // Check if any budget is exceeded
  getBudgetAlerts(stats) {
    const alerts = [];
    const monthlySpent = stats.current_month_spent || 0;

    // Check monthly budget
    if (this.budgets.monthly > 0 && monthlySpent > this.budgets.monthly) {
      alerts.push({
        type: "monthly",
        message: `Monthly budget exceeded by ₦${window.app.formatNumber(monthlySpent - this.budgets.monthly)}`,
      });
    }

    // Check category budgets
    const categories = stats.current_month_categories || {};
    Object.entries(this.budgets.categories).forEach(([category, budget]) => {
      if (budget > 0) {
        const spent = categories[category] || 0;
        if (spent > budget) {
          alerts.push({
            type: "category",
            category: category,
            message: `${category.charAt(0).toUpperCase() + category.slice(1)} budget exceeded by ₦${window.app.formatNumber(spent - budget)}`,
          });
        }
      }
    });

    return alerts;
  }
}

// Global budget manager instance
// window.budgetManager = new BudgetManager();

// Global functions
function showEnhancedBudgetModal() {
  console.log("showEnhancedBudgetModal called");
  if (window.budgetManager) {
    window.budgetManager.showBudgetModal();
  } else {
    console.error("Budget manager not loaded");
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing budget manager...");

  // Wait for other components to load
  setTimeout(() => {
    if (!window.budgetManager) {
      window.budgetManager = new BudgetManager();
    }

    // Replace the simple setBudget function with enhanced version
    window.setBudget = showEnhancedBudgetModal;
    console.log("Budget manager initialized");
  }, 150);
});
