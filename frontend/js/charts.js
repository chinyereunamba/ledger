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

    const data = {
      labels: categories.map(
        (cat) => cat.name.charAt(0).toUpperCase() + cat.name.slice(1)
      ),
      datasets: [
        {
          data: categories.map((cat) => cat.total_amount),
          backgroundColor: this.colors.slice(0, categories.length),
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

    const data = {
      labels: expenses.map((exp) =>
        exp.name.length > 15 ? exp.name.substring(0, 15) + "..." : exp.name
      ),
      datasets: [
        {
          label: "Amount Spent",
          data: expenses.map((exp) => exp.total_amount),
          backgroundColor: this.colors.slice(0, expenses.length),
          borderColor: this.colors.slice(0, expenses.length),
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

  // Create a simple line chart for daily spending trends
  createTrendChart(dailyData) {
    const ctx = document.getElementById("trend-chart");
    if (!ctx) return;

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
          borderWidth: 2,
          fill: true,
          tension: 0.4,
        },
      ],
    };

    new Chart(ctx, {
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
          },
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
  }
}

// Create global charts instance
const charts = new ChartManager();

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = ChartManager;
}
