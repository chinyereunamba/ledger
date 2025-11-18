// Chart management for analytics
class ChartManager {
  constructor() {
    this.categoryChart = null;
    this.expensesChart = null;
    this.colors = [
      "#3B82F6",
      "#EF4444",
      "#10B981",
      "#F59E0B",
      "#8B5CF6",
      "#EC4899",
      "#14B8A6",
      "#F97316",
      "#6366F1",
      "#84CC16",
    ];
  }

  updateCategoryChart(categories) {
    const ctx = document.getElementById("category-chart");
    if (!ctx) return;

    // Destroy existing chart
    if (this.categoryChart) {
      this.categoryChart.destroy();
    }

    // Normalize and consolidate categories by name (case-insensitive)
    const normalizedCategories = this.consolidateCategories(categories);

    const data = {
      labels: normalizedCategories.map(
        (cat) => cat.name.charAt(0).toUpperCase() + cat.name.slice(1)
      ),
      datasets: [
        {
          data: normalizedCategories.map(
            (cat) => cat.total_amount || cat.amount
          ),
          backgroundColor: this.colors.slice(0, normalizedCategories.length),
          borderWidth: 2,
          borderColor: "#ffffff",
        },
      ],
    };

    this.categoryChart = new Chart(ctx, {
      type: "doughnut",
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: {
              padding: 20,
              usePointStyle: true,
              font: {
                size: 12,
              },
            },
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const label = context.label || "";
                const value = context.parsed;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return `${label}: ₦${value.toLocaleString()} (${percentage}%)`;
              },
            },
          },
        },
        cutout: "60%",
      },
    });
  }

  updateExpensesChart(expenses) {
    const ctx = document.getElementById("expenses-chart");
    if (!ctx) return;

    // Destroy existing chart
    if (this.expensesChart) {
      this.expensesChart.destroy();
    }

    // Normalize expense names for consistent display
    const normalizedExpenses = expenses.map((exp) => ({
      ...exp,
      name: exp.name.charAt(0).toUpperCase() + exp.name.slice(1).toLowerCase(),
    }));

    const data = {
      labels: normalizedExpenses.map((exp) =>
        exp.name.length > 15 ? exp.name.substring(0, 15) + "..." : exp.name
      ),
      datasets: [
        {
          label: "Amount Spent",
          data: normalizedExpenses.map((exp) => exp.total_amount),
          backgroundColor: this.colors.slice(0, normalizedExpenses.length),
          borderColor: this.colors.slice(0, normalizedExpenses.length),
          borderWidth: 1,
        },
      ],
    };

    this.expensesChart = new Chart(ctx, {
      type: "bar",
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${
                  context.label
                }: ₦${context.parsed.y.toLocaleString()}`;
              },
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function (value) {
                return "₦" + value.toLocaleString();
              },
            },
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
          x: {
            grid: {
              display: false,
            },
            ticks: {
              maxRotation: 45,
              minRotation: 0,
            },
          },
        },
      },
    });
  }

  // Create a spending trends chart
  createTrendChart(dailyData) {
    const ctx = document.getElementById("trend-chart");
    if (!ctx) return;

    // Destroy existing chart
    if (this.trendChart) {
      this.trendChart.destroy();
    }

    const sortedDates = Object.keys(dailyData).sort();
    const data = {
      labels: sortedDates.map((date) => {
        const d = new Date(date);
        return d.toLocaleDateString("en-NG", {
          month: "short",
          day: "numeric",
        });
      }),
      datasets: [
        {
          label: "Daily Spending",
          data: sortedDates.map((date) => dailyData[date]),
          borderColor: "#3B82F6",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: "#3B82F6",
          pointBorderColor: "#ffffff",
          pointBorderWidth: 2,
          pointRadius: 5,
        },
      ],
    };

    this.trendChart = new Chart(ctx, {
      type: "line",
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `Spent: ₦${context.parsed.y.toLocaleString()}`;
              },
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function (value) {
                return "₦" + value.toLocaleString();
              },
            },
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
      },
    });
  }

  // Create monthly comparison chart
  createMonthlyChart(monthlyData) {
    const ctx = document.getElementById("monthly-chart");
    if (!ctx) return;

    // Destroy existing chart
    if (this.monthlyChart) {
      this.monthlyChart.destroy();
    }

    const months = Object.keys(monthlyData).sort();
    const data = {
      labels: months.map((month) => {
        const [year, monthNum] = month.split("-");
        const date = new Date(year, monthNum - 1);
        return date.toLocaleDateString("en-NG", {
          month: "short",
          year: "numeric",
        });
      }),
      datasets: [
        {
          label: "Monthly Spending",
          data: months.map((month) => monthlyData[month]),
          backgroundColor: "#10B981",
          borderColor: "#059669",
          borderWidth: 2,
          borderRadius: 8,
        },
      ],
    };

    this.monthlyChart = new Chart(ctx, {
      type: "bar",
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `Total: ₦${context.parsed.y.toLocaleString()}`;
              },
            },
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: function (value) {
                return "₦" + value.toLocaleString();
              },
            },
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
          x: {
            grid: {
              display: false,
            },
          },
        },
      },
    });
  }

  // Create category comparison chart (horizontal bar)
  createCategoryComparisonChart(categories) {
    const ctx = document.getElementById("category-comparison-chart");
    if (!ctx) return;

    // Destroy existing chart
    if (this.categoryComparisonChart) {
      this.categoryComparisonChart.destroy();
    }

    const normalizedCategories = this.consolidateCategories(categories);
    const topCategories = normalizedCategories.slice(0, 6); // Top 6 categories

    const data = {
      labels: topCategories.map(
        (cat) => cat.name.charAt(0).toUpperCase() + cat.name.slice(1)
      ),
      datasets: [
        {
          label: "Amount Spent",
          data: topCategories.map((cat) => cat.total_amount || cat.amount),
          backgroundColor: this.colors.slice(0, topCategories.length),
          borderColor: this.colors.slice(0, topCategories.length),
          borderWidth: 1,
          borderRadius: 6,
        },
      ],
    };

    this.categoryComparisonChart = new Chart(ctx, {
      type: "bar",
      data: data,
      options: {
        indexAxis: "y", // Horizontal bars
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false,
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((context.parsed.x / total) * 100).toFixed(
                  1
                );
                return `${
                  context.label
                }: ₦${context.parsed.x.toLocaleString()} (${percentage}%)`;
              },
            },
          },
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: {
              callback: function (value) {
                return "₦" + value.toLocaleString();
              },
            },
            grid: {
              color: "rgba(0, 0, 0, 0.1)",
            },
          },
          y: {
            grid: {
              display: false,
            },
          },
        },
      },
    });
  }

  // Consolidate categories with case-insensitive matching
  consolidateCategories(categories) {
    const consolidated = {};

    categories.forEach((cat) => {
      const normalizedName = cat.name.toLowerCase();
      const amount = cat.total_amount || cat.amount || 0;

      if (consolidated[normalizedName]) {
        consolidated[normalizedName].total_amount += amount;
      } else {
        consolidated[normalizedName] = {
          name: normalizedName,
          total_amount: amount,
          amount: amount,
        };
      }
    });

    return Object.values(consolidated).sort(
      (a, b) => b.total_amount - a.total_amount
    );
  }

  // Create dashboard mini trend chart
  createDashboardTrendChart(dailyData) {
    const ctx = document.getElementById("dashboard-trend-chart");
    if (!ctx) return;

    // Destroy existing chart
    if (this.dashboardTrendChart) {
      this.dashboardTrendChart.destroy();
    }

    const sortedDates = Object.keys(dailyData).sort().slice(-7); // Last 7 days
    const data = {
      labels: sortedDates.map((date) => {
        const d = new Date(date);
        return d.toLocaleDateString("en-NG", { weekday: "short" });
      }),
      datasets: [
        {
          data: sortedDates.map((date) => dailyData[date] || 0),
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
              label: function (context) {
                return `₦${context.parsed.y.toLocaleString()}`;
              },
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
  }

  // Destroy all charts (useful for cleanup)
  destroyAll() {
    if (this.categoryChart) {
      this.categoryChart.destroy();
      this.categoryChart = null;
    }
    if (this.expensesChart) {
      this.expensesChart.destroy();
      this.expensesChart = null;
    }
    if (this.trendChart) {
      this.trendChart.destroy();
      this.trendChart = null;
    }
    if (this.monthlyChart) {
      this.monthlyChart.destroy();
      this.monthlyChart = null;
    }
    if (this.categoryComparisonChart) {
      this.categoryComparisonChart.destroy();
      this.categoryComparisonChart = null;
    }
    if (this.dashboardTrendChart) {
      this.dashboardTrendChart.destroy();
      this.dashboardTrendChart = null;
    }
  }
}

// Create global charts instance
const charts = new ChartManager();

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = ChartManager;
}
