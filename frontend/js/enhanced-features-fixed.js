// Enhanced features for QuickLedger - Fixed Version
console.log("Loading enhanced features...");

// Global state
window.enhancedFeaturesState = {
  selectedExpenses: new Set(),
  searchTerm: "",
  filters: {
    category: "",
    amount: "",
    date: "all",
  },
  darkMode: localStorage.getItem("darkMode") === "true",
};

// Dark Mode Functions
function toggleDarkMode() {
  console.log("toggleDarkMode called");

  window.enhancedFeaturesState.darkMode =
    !window.enhancedFeaturesState.darkMode;
  localStorage.setItem("darkMode", window.enhancedFeaturesState.darkMode);

  const icon = document.getElementById("dark-mode-icon");
  if (window.enhancedFeaturesState.darkMode) {
    document.documentElement.setAttribute("data-theme", "dark");
    if (icon) icon.textContent = "☀️";
  } else {
    document.documentElement.removeAttribute("data-theme");
    if (icon) icon.textContent = "🌙";
  }

  console.log("Dark mode toggled:", window.enhancedFeaturesState.darkMode);
}

// Export Functions
function showExportModal() {
  console.log("showExportModal called");
  const modal = document.getElementById("export-modal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.classList.add("fade-in");
    console.log("Export modal shown");
  } else {
    console.error("Export modal not found");
  }
}

function closeExportModal() {
  console.log("closeExportModal called");
  const modal = document.getElementById("export-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("fade-in");
    console.log("Export modal closed");
  }
}

function exportExpenses() {
  console.log("exportExpenses called");

  const format = document.getElementById("export-format")?.value || "csv";
  const range = document.getElementById("export-range")?.value || "all";

  // Simple export for now
  if (window.app && window.app.allExpenses) {
    const expenses = window.app.allExpenses;

    if (format === "csv") {
      exportToCSV(expenses);
    } else {
      exportToJSON(expenses);
    }

    closeExportModal();
    if (window.app.showToast) {
      window.app.showToast(
        `Exported ${expenses.length} expenses successfully!`,
        "success",
      );
    }
  } else {
    console.error("No expenses data available");
    if (window.app && window.app.showToast) {
      window.app.showToast("No expenses data available", "error");
    }
  }
}

function exportToCSV(expenses) {
  const headers = ["Date", "Expense", "Category", "Amount"];
  const csvContent = [
    headers.join(","),
    ...expenses.map((expense) =>
      [
        expense.date,
        `"${expense.expense}"`,
        `"${window.app ? window.app.getCategoryDisplay(expense.expense) : "Other"}"`,
        expense.amount,
      ].join(","),
    ),
  ].join("\n");

  downloadFile(
    csvContent,
    `quickledger-expenses-${new Date().toISOString().split("T")[0]}.csv`,
    "text/csv",
  );
}

function exportToJSON(expenses) {
  const exportData = {
    exported_at: new Date().toISOString(),
    total_expenses: expenses.length,
    expenses: expenses,
  };

  const jsonContent = JSON.stringify(exportData, null, 2);
  downloadFile(
    jsonContent,
    `quickledger-expenses-${new Date().toISOString().split("T")[0]}.json`,
    "application/json",
  );
}

function downloadFile(content, filename, mimeType) {
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

// Import Functions
function showImportModal() {
  console.log("showImportModal called");
  const modal = document.getElementById("import-modal");
  if (modal) {
    modal.classList.remove("hidden");
    modal.classList.add("fade-in");
    console.log("Import modal shown");
  } else {
    console.error("Import modal not found");
  }
}

function closeImportModal() {
  console.log("closeImportModal called");
  const modal = document.getElementById("import-modal");
  if (modal) {
    modal.classList.add("hidden");
    modal.classList.remove("fade-in");
    console.log("Import modal closed");
  }
}

function importExpenses() {
  console.log("importExpenses called");
  const fileInput = document.getElementById("import-file");
  const file = fileInput?.files[0];

  if (!file) {
    if (window.app && window.app.showToast) {
      window.app.showToast("Please select a file to import", "error");
    }
    return;
  }

  console.log("Importing file:", file.name);

  const reader = new FileReader();
  reader.onload = function (e) {
    try {
      const content = e.target.result;
      let expenses = [];

      if (file.name.endsWith(".json")) {
        const data = JSON.parse(content);
        if (data.expenses && Array.isArray(data.expenses)) {
          expenses = data.expenses;
        } else if (Array.isArray(data)) {
          expenses = data;
        }
      } else if (file.name.endsWith(".csv")) {
        expenses = parseCSVContent(content);
      }

      console.log("Parsed expenses:", expenses.length);

      if (expenses.length > 0) {
        // For now, just show success message
        if (window.app && window.app.showToast) {
          window.app.showToast(
            `Found ${expenses.length} expenses in file. Import functionality coming soon!`,
            "info",
          );
        }
      } else {
        if (window.app && window.app.showToast) {
          window.app.showToast("No valid expenses found in file", "warning");
        }
      }

      closeImportModal();
    } catch (error) {
      console.error("Import error:", error);
      if (window.app && window.app.showToast) {
        window.app.showToast("Error importing file: " + error.message, "error");
      }
    }
  };

  reader.readAsText(file);
}

function parseCSVContent(content) {
  const lines = content.split("\n").filter((line) => line.trim());
  if (lines.length < 2) return [];

  const expenses = [];
  for (let i = 1; i < lines.length; i++) {
    const values = lines[i].split(",");
    if (values.length >= 3) {
      expenses.push({
        date: values[0] || new Date().toISOString().split("T")[0],
        expense: values[1].replace(/"/g, ""),
        amount: parseFloat(values[3] || values[2]) || 0,
      });
    }
  }

  return expenses.filter((exp) => exp.expense && exp.amount > 0);
}

// Search and Filter Functions
function setupSearchAndFilters() {
  console.log("Setting up search and filters...");

  // Search functionality
  const searchInput = document.getElementById("expense-search");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      window.enhancedFeaturesState.searchTerm = e.target.value.toLowerCase();
      applyFilters();
    });
    console.log("Search input listener added");
  }

  // Category filter
  const categoryFilter = document.getElementById("category-filter");
  if (categoryFilter) {
    categoryFilter.addEventListener("change", (e) => {
      window.enhancedFeaturesState.filters.category = e.target.value;
      applyFilters();
    });
    console.log("Category filter listener added");
  }

  // Amount filter
  const amountFilter = document.getElementById("amount-filter");
  if (amountFilter) {
    amountFilter.addEventListener("change", (e) => {
      window.enhancedFeaturesState.filters.amount = e.target.value;
      applyFilters();
    });
    console.log("Amount filter listener added");
  }
}

function applyFilters() {
  if (!window.app || !window.app.allExpenses) {
    console.log("App or expenses not available for filtering");
    return;
  }

  console.log("Applying filters...");
  let filteredExpenses = [...window.app.allExpenses];

  // Apply search filter
  if (window.enhancedFeaturesState.searchTerm) {
    filteredExpenses = filteredExpenses.filter((expense) =>
      expense.expense
        .toLowerCase()
        .includes(window.enhancedFeaturesState.searchTerm),
    );
  }

  // Apply category filter
  if (window.enhancedFeaturesState.filters.category) {
    filteredExpenses = filteredExpenses.filter((expense) => {
      const category = window.app
        .getCategoryDisplay(expense.expense)
        .toLowerCase();
      return category === window.enhancedFeaturesState.filters.category;
    });
  }

  // Apply amount filter
  if (window.enhancedFeaturesState.filters.amount) {
    filteredExpenses = filteredExpenses.filter((expense) => {
      const amount = parseFloat(expense.amount);
      switch (window.enhancedFeaturesState.filters.amount) {
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

  console.log(
    `Filtered ${window.app.allExpenses.length} expenses to ${filteredExpenses.length}`,
  );

  // Update the app's expense list
  window.app.allExpenses = filteredExpenses;
  window.app.totalExpenses = filteredExpenses.length;
  window.app.currentPage = 1;

  // Update display
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

// Bulk Selection Functions
function toggleSelectAll() {
  console.log("toggleSelectAll called");
  const selectAllCheckbox = document.getElementById("select-all");
  const expenseCheckboxes = document.querySelectorAll(".expense-checkbox");

  if (selectAllCheckbox && selectAllCheckbox.checked) {
    expenseCheckboxes.forEach((checkbox) => {
      checkbox.checked = true;
      const expenseId = checkbox.dataset.expenseId;
      window.enhancedFeaturesState.selectedExpenses.add(expenseId);
    });
  } else {
    expenseCheckboxes.forEach((checkbox) => {
      checkbox.checked = false;
      const expenseId = checkbox.dataset.expenseId;
      window.enhancedFeaturesState.selectedExpenses.delete(expenseId);
    });
    window.enhancedFeaturesState.selectedExpenses.clear();
  }

  updateBulkActions();
}

function toggleExpenseSelection(checkbox) {
  console.log("toggleExpenseSelection called");
  const expenseId = checkbox.dataset.expenseId;

  if (checkbox.checked) {
    window.enhancedFeaturesState.selectedExpenses.add(expenseId);
  } else {
    window.enhancedFeaturesState.selectedExpenses.delete(expenseId);
  }

  updateBulkActions();
}

function updateBulkActions() {
  const bulkActions = document.getElementById("bulk-actions");
  const selectedCount = document.getElementById("selected-count");

  if (window.enhancedFeaturesState.selectedExpenses.size > 0) {
    if (bulkActions) bulkActions.classList.remove("hidden");
    if (selectedCount)
      selectedCount.textContent = `${window.enhancedFeaturesState.selectedExpenses.size} selected`;
  } else {
    if (bulkActions) bulkActions.classList.add("hidden");
  }
}

function bulkDeleteExpenses() {
  console.log("bulkDeleteExpenses called");
  if (window.enhancedFeaturesState.selectedExpenses.size === 0) return;

  const confirmed = confirm(
    `Are you sure you want to delete ${window.enhancedFeaturesState.selectedExpenses.size} selected expense(s)?`,
  );
  if (confirmed) {
    // For now, just show a message
    if (window.app && window.app.showToast) {
      window.app.showToast(
        `Bulk delete of ${window.enhancedFeaturesState.selectedExpenses.size} expenses - functionality coming soon!`,
        "info",
      );
    }
    clearSelection();
  }
}

function clearSelection() {
  console.log("clearSelection called");
  window.enhancedFeaturesState.selectedExpenses.clear();
  const checkboxes = document.querySelectorAll(
    ".expense-checkbox, #select-all",
  );
  checkboxes.forEach((checkbox) => (checkbox.checked = false));
  updateBulkActions();
}

// Notification Settings
function showNotificationSettings() {
  console.log("showNotificationSettings called");
  if (window.app && window.app.showToast) {
    window.app.showToast(
      "Notification settings - functionality coming soon!",
      "info",
    );
  }
}

// Keyboard Shortcuts
function setupKeyboardShortcuts() {
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
      showExportModal();
    }

    // Ctrl/Cmd + I for import
    if ((e.ctrlKey || e.metaKey) && e.key === "i") {
      e.preventDefault();
      showImportModal();
    }

    // Escape to close modals
    if (e.key === "Escape") {
      closeExportModal();
      closeImportModal();
    }
  });

  console.log("Keyboard shortcuts set up");
}

// Initialize everything
function initializeEnhancedFeatures() {
  console.log("Initializing enhanced features...");

  // Initialize dark mode
  if (window.enhancedFeaturesState.darkMode) {
    document.documentElement.setAttribute("data-theme", "dark");
    const icon = document.getElementById("dark-mode-icon");
    if (icon) icon.textContent = "☀️";
  }

  // Set up event listeners
  setupSearchAndFilters();
  setupKeyboardShortcuts();

  console.log("Enhanced features initialized successfully!");
}

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeEnhancedFeatures);
} else {
  initializeEnhancedFeatures();
}

// Also initialize after a short delay to ensure all elements are available
setTimeout(initializeEnhancedFeatures, 500);

console.log("Enhanced features script loaded");
