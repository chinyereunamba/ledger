// Enhanced features for QuickLedger
class EnhancedFeatures {
  constructor() {
    this.selectedExpenses = new Set();
    this.searchTerm = "";
    this.filters = {
      category: "",
      amount: "",
      date: "all",
    };
    this.darkMode = localStorage.getItem("darkMode") === "true";
    this.initialized = false;
  }

  init() {
    if (this.initialized) return;

    this.initDarkMode();
    this.setupEventListeners();
    this.setupKeyboardShortcuts();
    this.initialized = true;
    console.log("Enhanced features initialized successfully");
  }

  initDarkMode() {
    if (this.darkMode) {
      document.documentElement.setAttribute("data-theme", "dark");
      const icon = document.getElementById("dark-mode-icon");
      if (icon) icon.textContent = "☀️";
    }
  }

  setupEventListeners() {
    // Search functionality
    const searchInput = document.getElementById("expense-search");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        this.searchTerm = e.target.value.toLowerCase();
        this.applyFilters();
      });
      console.log("Search input listener added");
    } else {
      console.warn("Search input not found");
    }

    // Filter functionality
    const categoryFilter = document.getElementById("category-filter");
    const amountFilter = document.getElementById("amount-filter");

    if (categoryFilter) {
      categoryFilter.addEventListener("change", (e) => {
        this.filters.category = e.target.value;
        this.applyFilters();
      });
      console.log("Category filter listener added");
    } else {
      console.warn("Category filter not found");
    }

    if (amountFilter) {
      amountFilter.addEventListener("change", (e) => {
        this.filters.amount = e.target.value;
        this.applyFilters();
      });
    }

    // Export range selector
    const exportRange = document.getElementById("export-range");
    if (exportRange) {
      exportRange.addEventListener("change", (e) => {
        const customRange = document.getElementById("custom-date-range");
        if (customRange) {
          if (e.target.value === "custom") {
            customRange.classList.remove("hidden");
          } else {
            customRange.classList.add("hidden");
          }
        }
      });
    }
  }

  setupKeyboardShortcuts() {
    document.addEventListener("keydown", (e) => {
      // Ctrl/Cmd + K for search
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        const searchInput = document.getElementById("expense-search");
        if (searchInput) searchInput.focus();
      }

      // Ctrl/Cmd + E for export
      if ((e.ctrlKey || e.metaKey) && e.key === "e") {
        e.preventDefault();
        this.showExportModal();
      }

      // Ctrl/Cmd + I for import
      if ((e.ctrlKey || e.metaKey) && e.key === "i") {
        e.preventDefault();
        this.showImportModal();
      }

      // Escape to close modals
      if (e.key === "Escape") {
        this.closeAllModals();
      }

      // Delete key for bulk delete
      if (e.key === "Delete" && this.selectedExpenses.size > 0) {
        e.preventDefault();
        this.bulkDeleteExpenses();
      }
    });
  }

  applyFilters() {
    if (!window.app) {
      console.warn("App not loaded yet, cannot apply filters");
      return;
    }

    // Store original expenses if not already stored
    if (!window.app.originalExpenses && window.app.allExpenses) {
      window.app.originalExpenses = [...window.app.allExpenses];
    }

    if (!window.app.originalExpenses) {
      console.warn("No expenses to filter");
      return;
    }

    let filteredExpenses = [...window.app.originalExpenses];

    // Apply search filter
    if (this.searchTerm) {
      filteredExpenses = filteredExpenses.filter((expense) =>
        expense.expense.toLowerCase().includes(this.searchTerm),
      );
    }

    // Apply category filter
    if (this.filters.category) {
      filteredExpenses = filteredExpenses.filter((expense) => {
        const category = window.app
          .getCategoryDisplay(expense.expense)
          .toLowerCase();
        return category === this.filters.category;
      });
    }

    // Apply amount filter
    if (this.filters.amount) {
      filteredExpenses = filteredExpenses.filter((expense) => {
        const amount = parseFloat(expense.amount);
        switch (this.filters.amount) {
          case "0-500":
            return amount >= 0 && amount <= 500;
          case "500-1000":
            return amount > 500 && amount <= 1000;
          case "1000-2000":
            return amount > 1000 && amount <= 2000;
          case "2000-5000":
            return amount > 2000 && amount <= 5000;
          case "5000+":
            return amount > 5000;
          default:
            return true;
        }
      });
    }

    // Update display
    window.app.allExpenses = filteredExpenses;
    window.app.totalExpenses = filteredExpenses.length;
    window.app.currentPage = 1;

    const startIndex = (window.app.currentPage - 1) * window.app.itemsPerPage;
    const endIndex = startIndex + window.app.itemsPerPage;
    const paginatedExpenses = filteredExpenses.slice(startIndex, endIndex);

    window.app.displayExpenses(paginatedExpenses);
    window.app.updatePagination();

    // Update count
    const countElement = document.getElementById("expense-count");
    if (countElement) {
      countElement.textContent = `${filteredExpenses.length} expense${filteredExpenses.length !== 1 ? "s" : ""}`;
    }
  }

  // Dark mode functionality
  toggleDarkMode() {
    this.darkMode = !this.darkMode;
    localStorage.setItem("darkMode", this.darkMode);

    const icon = document.getElementById("dark-mode-icon");
    if (this.darkMode) {
      document.documentElement.setAttribute("data-theme", "dark");
      if (icon) icon.textContent = "☀️";
    } else {
      document.documentElement.removeAttribute("data-theme");
      if (icon) icon.textContent = "🌙";
    }
  }

  // Bulk selection functionality
  toggleSelectAll() {
    const selectAllCheckbox = document.getElementById("select-all");
    const expenseCheckboxes = document.querySelectorAll(".expense-checkbox");

    if (selectAllCheckbox.checked) {
      expenseCheckboxes.forEach((checkbox) => {
        checkbox.checked = true;
        const expenseId = checkbox.dataset.expenseId;
        this.selectedExpenses.add(expenseId);
        this.highlightExpenseRow(checkbox, true);
      });
    } else {
      expenseCheckboxes.forEach((checkbox) => {
        checkbox.checked = false;
        const expenseId = checkbox.dataset.expenseId;
        this.selectedExpenses.delete(expenseId);
        this.highlightExpenseRow(checkbox, false);
      });
      this.selectedExpenses.clear();
    }

    this.updateBulkActions();
  }

  toggleExpenseSelection(checkbox) {
    const expenseId = checkbox.dataset.expenseId;

    if (checkbox.checked) {
      this.selectedExpenses.add(expenseId);
      this.highlightExpenseRow(checkbox, true);
    } else {
      this.selectedExpenses.delete(expenseId);
      this.highlightExpenseRow(checkbox, false);
    }

    this.updateBulkActions();
    this.updateSelectAllCheckbox();
  }

  highlightExpenseRow(checkbox, selected) {
    const row = checkbox.closest("tr");
    if (row) {
      if (selected) {
        row.classList.add("expense-row-selected");
      } else {
        row.classList.remove("expense-row-selected");
      }
    }
  }

  updateBulkActions() {
    const bulkActions = document.getElementById("bulk-actions");
    const selectedCount = document.getElementById("selected-count");

    if (this.selectedExpenses.size > 0) {
      bulkActions.classList.remove("hidden");
      selectedCount.textContent = `${this.selectedExpenses.size} selected`;
    } else {
      bulkActions.classList.add("hidden");
    }
  }

  updateSelectAllCheckbox() {
    const selectAllCheckbox = document.getElementById("select-all");
    const expenseCheckboxes = document.querySelectorAll(".expense-checkbox");
    const checkedBoxes = document.querySelectorAll(".expense-checkbox:checked");

    if (checkedBoxes.length === 0) {
      selectAllCheckbox.checked = false;
      selectAllCheckbox.indeterminate = false;
    } else if (checkedBoxes.length === expenseCheckboxes.length) {
      selectAllCheckbox.checked = true;
      selectAllCheckbox.indeterminate = false;
    } else {
      selectAllCheckbox.checked = false;
      selectAllCheckbox.indeterminate = true;
    }
  }

  clearSelection() {
    this.selectedExpenses.clear();
    const checkboxes = document.querySelectorAll(
      ".expense-checkbox, #select-all",
    );
    checkboxes.forEach((checkbox) => {
      checkbox.checked = false;
      if (checkbox.classList.contains("expense-checkbox")) {
        this.highlightExpenseRow(checkbox, false);
      }
    });
    this.updateBulkActions();
  }

  async bulkDeleteExpenses() {
    if (this.selectedExpenses.size === 0) return;

    const confirmed = confirm(
      `Are you sure you want to delete ${this.selectedExpenses.size} selected expense(s)?`,
    );
    if (!confirmed) return;

    try {
      window.app.showLoading();

      // Convert selected IDs back to date/index pairs and delete
      const deletePromises = [];
      this.selectedExpenses.forEach((expenseId) => {
        const [date, index] = expenseId.split("-");
        deletePromises.push(api.deleteExpense(date, parseInt(index)));
      });

      await Promise.all(deletePromises);

      window.app.showToast(
        `${this.selectedExpenses.size} expense(s) deleted successfully!`,
        "success",
      );
      this.clearSelection();
      await window.app.loadExpenses();
    } catch (error) {
      console.error("Error deleting expenses:", error);
      window.app.showToast("Error deleting expenses", "error");
    } finally {
      window.app.hideLoading();
    }
  }

  // Export functionality
  showExportModal() {
    let modal = document.getElementById("export-modal");

    // Create modal if it doesn't exist
    if (!modal) {
      modal = this.createExportModal();
      document.body.appendChild(modal);
    }

    if (modal) {
      modal.classList.remove("hidden");
      modal.classList.add("fade-in");
    }
  }

  createExportModal() {
    const modal = document.createElement("div");
    modal.id = "export-modal";
    modal.className =
      "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden";

    modal.innerHTML = `
      <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4 modal-content">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Export Expenses</h3>
          <button onclick="closeExportModal()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Export Format</label>
            <select id="export-format" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="csv">CSV (Excel compatible)</option>
              <option value="json">JSON (Backup format)</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
            <select id="export-range" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="all">All Time</option>
              <option value="month">This Month</option>
              <option value="week">This Week</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>
          
          <div id="custom-date-range" class="hidden space-y-2">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input type="date" id="export-start-date" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input type="date" id="export-end-date" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
            </div>
          </div>
          
          <div class="flex space-x-3 pt-4">
            <button
              onclick="exportExpenses()"
              class="flex-1 bg-blue-500 text-white py-2 px-4 rounded-md hover:bg-blue-600 transition-colors"
            >
              Export
            </button>
            <button
              onclick="closeExportModal()"
              class="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    `;

    // Add event listener for range selector
    const rangeSelect = modal.querySelector("#export-range");
    if (rangeSelect) {
      rangeSelect.addEventListener("change", (e) => {
        const customRange = modal.querySelector("#custom-date-range");
        if (customRange) {
          if (e.target.value === "custom") {
            customRange.classList.remove("hidden");
          } else {
            customRange.classList.add("hidden");
          }
        }
      });
    }

    return modal;
  }

  closeExportModal() {
    const modal = document.getElementById("export-modal");
    if (modal) {
      modal.classList.add("hidden");
      modal.classList.remove("fade-in");
    }
  }

  async exportExpenses() {
    try {
      const format = document.getElementById("export-format").value;
      const range = document.getElementById("export-range").value;

      let params = {};

      // Set date range parameters
      switch (range) {
        case "month":
          const now = new Date();
          const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
          const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
          params.range = `${firstDay.toISOString().split("T")[0]},${lastDay.toISOString().split("T")[0]}`;
          break;
        case "week":
          params.week = true;
          break;
        case "custom":
          const startDate = document.getElementById("export-start-date").value;
          const endDate = document.getElementById("export-end-date").value;
          if (!startDate || !endDate) {
            window.app.showToast(
              "Please select both start and end dates",
              "error",
            );
            return;
          }
          params.range = `${startDate},${endDate}`;
          break;
      }

      window.app.showLoading();

      // Get expenses data
      const result = await api.getExpenses(params);
      const expenses = result.expenses || [];

      if (expenses.length === 0) {
        window.app.showToast(
          "No expenses found for the selected range",
          "warning",
        );
        return;
      }

      // Generate filename
      const timestamp = new Date().toISOString().split("T")[0];
      const filename = `quickledger-expenses-${timestamp}.${format}`;

      if (format === "csv") {
        this.exportToCSV(expenses, filename);
      } else {
        this.exportToJSON(expenses, filename);
      }

      this.closeExportModal();
      window.app.showToast(
        `Exported ${expenses.length} expenses successfully!`,
        "success",
      );
    } catch (error) {
      console.error("Error exporting expenses:", error);
      window.app.showToast("Error exporting expenses", "error");
    } finally {
      window.app.hideLoading();
    }
  }

  exportToCSV(expenses, filename) {
    const headers = ["Date", "Expense", "Category", "Amount"];
    const csvContent = [
      headers.join(","),
      ...expenses.map((expense) =>
        [
          expense.date,
          `"${expense.expense}"`,
          `"${window.app.getCategoryDisplay(expense.expense)}"`,
          expense.amount,
        ].join(","),
      ),
    ].join("\n");

    this.downloadFile(csvContent, filename, "text/csv");
  }

  exportToJSON(expenses, filename) {
    const exportData = {
      exported_at: new Date().toISOString(),
      total_expenses: expenses.length,
      expenses: expenses.map((expense) => ({
        ...expense,
        category: window.app.getCategoryDisplay(expense.expense),
      })),
    };

    const jsonContent = JSON.stringify(exportData, null, 2);
    this.downloadFile(jsonContent, filename, "application/json");
  }

  downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  // Import functionality
  showImportModal() {
    let modal = document.getElementById("import-modal");

    // Create modal if it doesn't exist
    if (!modal) {
      modal = this.createImportModal();
      document.body.appendChild(modal);
    }

    if (modal) {
      modal.classList.remove("hidden");
      modal.classList.add("fade-in");
    }
  }

  createImportModal() {
    const modal = document.createElement("div");
    modal.id = "import-modal";
    modal.className =
      "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 hidden";

    modal.innerHTML = `
      <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4 modal-content">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Import Expenses</h3>
          <button onclick="closeImportModal()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Select File</label>
            <input
              type="file"
              id="import-file"
              accept=".json,.csv"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p class="text-xs text-gray-500 mt-1">Supports JSON and CSV files</p>
          </div>
          
          <div class="flex space-x-3 pt-4">
            <button
              onclick="importExpenses()"
              class="flex-1 bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition-colors"
            >
              Import
            </button>
            <button
              onclick="closeImportModal()"
              class="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-400 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    `;

    return modal;
  }

  closeImportModal() {
    const modal = document.getElementById("import-modal");
    if (modal) {
      modal.classList.add("hidden");
      modal.classList.remove("fade-in");
    }
  }

  async importExpenses() {
    const fileInput = document.getElementById("import-file");
    const file = fileInput.files[0];

    if (!file) {
      window.app.showToast("Please select a file to import", "error");
      return;
    }

    try {
      window.app.showLoading();

      const fileContent = await this.readFile(file);
      let expenses = [];

      if (file.name.endsWith(".json")) {
        expenses = this.parseJSONImport(fileContent);
      } else if (file.name.endsWith(".csv")) {
        expenses = this.parseCSVImport(fileContent);
      } else {
        throw new Error(
          "Unsupported file format. Please use JSON or CSV files.",
        );
      }

      if (expenses.length === 0) {
        window.app.showToast("No valid expenses found in the file", "warning");
        return;
      }

      // Import expenses
      let imported = 0;
      for (const expense of expenses) {
        try {
          await api.addExpense(expense);
          imported++;
        } catch (error) {
          console.warn("Failed to import expense:", expense, error);
        }
      }

      this.closeImportModal();
      window.app.showToast(
        `Successfully imported ${imported} out of ${expenses.length} expenses!`,
        "success",
      );

      // Refresh the current view
      if (window.app.currentSection === "dashboard") {
        await window.app.loadDashboard();
      } else if (window.app.currentSection === "expenses") {
        await window.app.loadExpenses();
      }
    } catch (error) {
      console.error("Error importing expenses:", error);
      window.app.showToast(`Import error: ${error.message}`, "error");
    } finally {
      window.app.hideLoading();
    }
  }

  readFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  parseJSONImport(content) {
    try {
      const data = JSON.parse(content);

      // Handle different JSON formats
      let expenses = [];

      if (data.expenses && Array.isArray(data.expenses)) {
        // QuickLedger export format
        expenses = data.expenses;
      } else if (Array.isArray(data)) {
        // Simple array format
        expenses = data;
      } else {
        // Raw ledger format
        for (const [date, dayExpenses] of Object.entries(data)) {
          if (Array.isArray(dayExpenses)) {
            dayExpenses.forEach((expense) => {
              expenses.push({
                expense: expense.expense,
                amount: parseFloat(expense.amount),
                date: date,
              });
            });
          }
        }
      }

      return expenses
        .map((expense) => ({
          expense: expense.expense || expense.name || "",
          amount: parseFloat(expense.amount) || 0,
          date: expense.date || new Date().toISOString().split("T")[0],
        }))
        .filter((expense) => expense.expense && expense.amount > 0);
    } catch (error) {
      throw new Error("Invalid JSON format");
    }
  }

  parseCSVImport(content) {
    try {
      const lines = content.split("\n").filter((line) => line.trim());
      if (lines.length < 2)
        throw new Error(
          "CSV file must have at least a header and one data row",
        );

      const headers = lines[0]
        .split(",")
        .map((h) => h.trim().toLowerCase().replace(/"/g, ""));
      const expenses = [];

      for (let i = 1; i < lines.length; i++) {
        const values = this.parseCSVLine(lines[i]);
        if (values.length < headers.length) continue;

        const expense = {};
        headers.forEach((header, index) => {
          expense[header] = values[index] || "";
        });

        // Map common column names
        const expenseName =
          expense.expense || expense.description || expense.name || "";
        const amount = parseFloat(
          expense.amount || expense.cost || expense.price || 0,
        );
        const date = expense.date || new Date().toISOString().split("T")[0];

        if (expenseName && amount > 0) {
          expenses.push({
            expense: expenseName,
            amount: amount,
            date: date,
          });
        }
      }

      return expenses;
    } catch (error) {
      throw new Error("Invalid CSV format");
    }
  }

  parseCSVLine(line) {
    const values = [];
    let current = "";
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];

      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === "," && !inQuotes) {
        values.push(current.trim());
        current = "";
      } else {
        current += char;
      }
    }

    values.push(current.trim());
    return values.map((v) => v.replace(/^"|"$/g, ""));
  }

  closeAllModals() {
    this.closeExportModal();
    this.closeImportModal();
  }
}

// Create a temporary instance for immediate function availability
let tempEnhancedFeatures = null;

// Global functions for HTML onclick handlers
function toggleDarkMode() {
  console.log("toggleDarkMode called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.toggleDarkMode();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.toggleDarkMode();
  } else {
    console.error("Enhanced features not loaded");
  }
}

function showExportModal() {
  console.log("showExportModal called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.showExportModal();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.showExportModal();
  } else {
    console.error("Enhanced features not loaded");
  }
}

function closeExportModal() {
  console.log("closeExportModal called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.closeExportModal();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.closeExportModal();
  } else {
    console.error("Enhanced features not loaded");
  }
}

function exportExpenses() {
  console.log("exportExpenses called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.exportExpenses();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.exportExpenses();
  } else {
    console.error("Enhanced features not loaded");
  }
}

function showImportModal() {
  console.log("showImportModal called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.showImportModal();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.showImportModal();
  } else {
    console.error("Enhanced features not loaded");
  }
}

function closeImportModal() {
  console.log("closeImportModal called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.closeImportModal();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.closeImportModal();
  } else {
    console.error("Enhanced features not loaded");
  }
}

function importExpenses() {
  console.log("importExpenses called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.importExpenses();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.importExpenses();
  } else {
    console.error("Enhanced features not loaded");
  }
}

function toggleSelectAll() {
  console.log("toggleSelectAll called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.toggleSelectAll();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.toggleSelectAll();
  } else {
    console.error("Enhanced features not loaded");
  }
}

function toggleExpenseSelection(checkbox) {
  console.log("toggleExpenseSelection called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.toggleExpenseSelection(checkbox);
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.toggleExpenseSelection(checkbox);
  } else {
    console.error("Enhanced features not loaded");
  }
}

function bulkDeleteExpenses() {
  console.log("bulkDeleteExpenses called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.bulkDeleteExpenses();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.bulkDeleteExpenses();
  } else {
    console.error("Enhanced features not loaded");
  }
}

function clearSelection() {
  console.log("clearSelection called");
  if (window.enhancedFeatures) {
    window.enhancedFeatures.clearSelection();
  } else if (tempEnhancedFeatures) {
    tempEnhancedFeatures.clearSelection();
  } else {
    console.error("Enhanced features not loaded");
  }
}

// Initialize enhanced features when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, initializing enhanced features...");

  // Wait a bit for other scripts to load
  setTimeout(() => {
    window.enhancedFeatures = new EnhancedFeatures();
    window.enhancedFeatures.init();

    // Re-initialize when app is ready
    if (window.app) {
      console.log("App found, enhanced features ready");
    } else {
      console.log("App not found yet, will retry...");
      // Try again after app loads
      const checkApp = setInterval(() => {
        if (window.app) {
          console.log("App loaded, re-initializing enhanced features");
          window.enhancedFeatures.init();
          clearInterval(checkApp);
        }
      }, 100);
    }
  }, 100);
});
