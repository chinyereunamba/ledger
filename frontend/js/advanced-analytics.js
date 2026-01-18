// Advanced Analytics and Insights
class AdvancedAnalytics {
  constructor() {
    this.insights = [];
    this.predictions = {};
    this.comparisons = {};
    this.init();
  }

  init() {
    this.setupAnalyticsEnhancements();
  }

  setupAnalyticsEnhancements() {
    // Add event listeners for interactive analytics
    document.addEventListener("DOMContentLoaded", () => {
      this.enhanceAnalyticsSection();
    });
  }

  enhanceAnalyticsSection() {
    // Add interactive elements to analytics section
    const analyticsSection = document.getElementById("analytics-section");
    if (!analyticsSection) return;

    // Add comparison controls
    this.addComparisonControls();

    // Add prediction insights
    this.addPredictionInsights();

    // Add spending velocity indicators
    this.addSpendingVelocity();
  }

  addComparisonControls() {
    const analyticsSection = document.getElementById("analytics-section");
    if (!analyticsSection) return;

    // Find the analytics header and add comparison controls
    const breakdown = analyticsSection.querySelector(".breakdown");
    if (breakdown && breakdown.parentNode) {
      const controlsDiv = document.createElement("div");
      controlsDiv.className = "mb-6 bg-white rounded-lg shadow-md p-4";
      controlsDiv.innerHTML = `
        <h3 class="text-lg font-semibold text-gray-900 mb-4">📊 Comparison Analysis</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Compare Period</label>
            <select id="comparison-period" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="month">This Month vs Last Month</option>
              <option value="week">This Week vs Last Week</option>
              <option value="quarter">This Quarter vs Last Quarter</option>
              <option value="year">This Year vs Last Year</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Metric</label>
            <select id="comparison-metric" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              <option value="total">Total Spending</option>
              <option value="average">Daily Average</option>
              <option value="transactions">Transaction Count</option>
              <option value="categories">Category Distribution</option>
            </select>
          </div>
          <div class="flex items-end">
            <button
              onclick="advancedAnalytics.generateComparison()"
              class="w-full bg-purple-500 text-white px-4 py-2 rounded-md hover:bg-purple-600 transition-colors"
            >
              Generate Comparison
            </button>
          </div>
        </div>
        <div id="comparison-results" class="mt-4 hidden">
          <!-- Comparison results will be displayed here -->
        </div>
      `;

      breakdown.parentNode.insertBefore(controlsDiv, breakdown.nextSibling);
    }
  }

  addPredictionInsights() {
    const analyticsSection = document.getElementById("analytics-section");
    if (!analyticsSection) return;

    const predictionDiv = document.createElement("div");
    predictionDiv.className =
      "mb-8 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg shadow-md p-6 text-white";
    predictionDiv.innerHTML = `
      <h3 class="text-xl font-semibold mb-4">🔮 Spending Predictions</h3>
      <div id="prediction-content" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Predictions will be loaded here -->
      </div>
    `;

    // Insert after comparison controls
    const comparisonControls = analyticsSection.querySelector(".mb-6");
    if (comparisonControls && comparisonControls.nextSibling) {
      analyticsSection.insertBefore(
        predictionDiv,
        comparisonControls.nextSibling,
      );
    }
  }

  addSpendingVelocity() {
    const analyticsSection = document.getElementById("analytics-section");
    if (!analyticsSection) return;

    const velocityDiv = document.createElement("div");
    velocityDiv.className = "mb-8 bg-white rounded-lg shadow-md p-6";
    velocityDiv.innerHTML = `
      <h3 class="text-lg font-semibold text-gray-900 mb-4">⚡ Spending Velocity</h3>
      <div id="velocity-indicators" class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Velocity indicators will be loaded here -->
      </div>
    `;

    // Insert before charts
    const chartsGrid = analyticsSection.querySelector(
      ".grid.grid-cols-1.lg\\:grid-cols-2",
    );
    if (chartsGrid) {
      analyticsSection.insertBefore(velocityDiv, chartsGrid);
    }
  }

  async generateComparison() {
    const period = document.getElementById("comparison-period").value;
    const metric = document.getElementById("comparison-metric").value;
    const resultsDiv = document.getElementById("comparison-results");

    if (!resultsDiv) return;

    try {
      window.app.showLoading();

      const comparison = await this.calculateComparison(period, metric);
      this.displayComparisonResults(comparison, resultsDiv);

      resultsDiv.classList.remove("hidden");
    } catch (error) {
      console.error("Error generating comparison:", error);
      window.app.showToast("Error generating comparison", "error");
    } finally {
      window.app.hideLoading();
    }
  }

  async calculateComparison(period, metric) {
    const now = new Date();
    let currentStart, currentEnd, previousStart, previousEnd;

    switch (period) {
      case "month":
        currentStart = new Date(now.getFullYear(), now.getMonth(), 1);
        currentEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        previousStart = new Date(now.getFullYear(), now.getMonth() - 1, 1);
        previousEnd = new Date(now.getFullYear(), now.getMonth(), 0);
        break;
      case "week":
        const dayOfWeek = now.getDay();
        currentStart = new Date(now);
        currentStart.setDate(now.getDate() - dayOfWeek);
        currentEnd = new Date(currentStart);
        currentEnd.setDate(currentStart.getDate() + 6);
        previousStart = new Date(currentStart);
        previousStart.setDate(currentStart.getDate() - 7);
        previousEnd = new Date(previousStart);
        previousEnd.setDate(previousStart.getDate() + 6);
        break;
      // Add more period calculations as needed
    }

    // Get data for both periods
    const currentData = await api.getExpenses({
      range: `${currentStart.toISOString().split("T")[0]},${currentEnd.toISOString().split("T")[0]}`,
    });

    const previousData = await api.getExpenses({
      range: `${previousStart.toISOString().split("T")[0]},${previousEnd.toISOString().split("T")[0]}`,
    });

    return this.compareData(
      currentData.expenses,
      previousData.expenses,
      metric,
      period,
    );
  }

  compareData(currentExpenses, previousExpenses, metric, period) {
    const current = this.calculateMetric(currentExpenses, metric);
    const previous = this.calculateMetric(previousExpenses, metric);

    const change = current.value - previous.value;
    const percentageChange =
      previous.value > 0 ? (change / previous.value) * 100 : 0;

    return {
      period,
      metric,
      current,
      previous,
      change,
      percentageChange,
      trend: change > 0 ? "increase" : change < 0 ? "decrease" : "stable",
    };
  }

  calculateMetric(expenses, metric) {
    switch (metric) {
      case "total":
        const total = expenses.reduce(
          (sum, exp) => sum + parseFloat(exp.amount),
          0,
        );
        return { value: total, label: `₦${window.app.formatNumber(total)}` };

      case "average":
        const dailyTotals = {};
        expenses.forEach((exp) => {
          dailyTotals[exp.date] =
            (dailyTotals[exp.date] || 0) + parseFloat(exp.amount);
        });
        const days = Object.keys(dailyTotals).length;
        const average =
          days > 0
            ? Object.values(dailyTotals).reduce((a, b) => a + b, 0) / days
            : 0;
        return {
          value: average,
          label: `₦${window.app.formatNumber(average)}/day`,
        };

      case "transactions":
        return {
          value: expenses.length,
          label: `${expenses.length} transactions`,
        };

      case "categories":
        const categories = {};
        expenses.forEach((exp) => {
          const category = window.app.getCategoryDisplay(exp.expense);
          categories[category] =
            (categories[category] || 0) + parseFloat(exp.amount);
        });
        const topCategory = Object.entries(categories).sort(
          (a, b) => b[1] - a[1],
        )[0];
        return {
          value: topCategory ? topCategory[1] : 0,
          label: topCategory
            ? `${topCategory[0]}: ₦${window.app.formatNumber(topCategory[1])}`
            : "No data",
        };

      default:
        return { value: 0, label: "No data" };
    }
  }

  displayComparisonResults(comparison, container) {
    const trendIcon =
      comparison.trend === "increase"
        ? "📈"
        : comparison.trend === "decrease"
          ? "📉"
          : "➡️";
    const trendColor =
      comparison.trend === "increase"
        ? "text-red-600"
        : comparison.trend === "decrease"
          ? "text-green-600"
          : "text-gray-600";

    container.innerHTML = `
      <div class="bg-gray-50 rounded-lg p-4">
        <h4 class="font-semibold text-gray-900 mb-3">Comparison Results</h4>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-center">
            <p class="text-sm text-gray-600">Current Period</p>
            <p class="text-lg font-semibold text-blue-600">${comparison.current.label}</p>
          </div>
          <div class="text-center">
            <p class="text-sm text-gray-600">Previous Period</p>
            <p class="text-lg font-semibold text-gray-600">${comparison.previous.label}</p>
          </div>
          <div class="text-center">
            <p class="text-sm text-gray-600">Change</p>
            <p class="text-lg font-semibold ${trendColor}">
              ${trendIcon} ${Math.abs(comparison.percentageChange).toFixed(1)}%
            </p>
          </div>
        </div>
        <div class="mt-3 text-sm text-gray-600 text-center">
          ${this.generateComparisonInsight(comparison)}
        </div>
      </div>
    `;
  }

  generateComparisonInsight(comparison) {
    const { trend, percentageChange, metric, period } = comparison;

    if (trend === "stable") {
      return `Your ${metric} has remained stable compared to the previous ${period}.`;
    }

    const direction = trend === "increase" ? "increased" : "decreased";
    const sentiment =
      trend === "increase" && metric === "total"
        ? "Consider reviewing your spending habits."
        : trend === "decrease" && metric === "total"
          ? "Great job on reducing expenses!"
          : "Keep monitoring your spending patterns.";

    return `Your ${metric} has ${direction} by ${Math.abs(percentageChange).toFixed(1)}% compared to the previous ${period}. ${sentiment}`;
  }

  async generatePredictions(stats) {
    const predictions = [];

    // Monthly spending prediction
    const monthlyPrediction = this.predictMonthlySpending(stats);
    predictions.push({
      title: "Month-End Projection",
      value: `₦${window.app.formatNumber(monthlyPrediction.projected)}`,
      subtitle: `Based on current trend`,
      confidence: monthlyPrediction.confidence,
    });

    // Budget status prediction
    if (window.budgetManager && window.budgetManager.budgets.monthly > 0) {
      const budgetPrediction = this.predictBudgetStatus(
        stats,
        monthlyPrediction.projected,
      );
      predictions.push({
        title: "Budget Status",
        value: budgetPrediction.status,
        subtitle: budgetPrediction.message,
        confidence: budgetPrediction.confidence,
      });
    }

    // Category trend prediction
    const categoryPrediction = this.predictCategoryTrend(stats);
    if (categoryPrediction) {
      predictions.push({
        title: "Category Trend",
        value: categoryPrediction.category,
        subtitle: categoryPrediction.trend,
        confidence: categoryPrediction.confidence,
      });
    }

    this.displayPredictions(predictions);
  }

  predictMonthlySpending(stats) {
    const now = new Date();
    const daysInMonth = new Date(
      now.getFullYear(),
      now.getMonth() + 1,
      0,
    ).getDate();
    const daysPassed = now.getDate();
    const daysRemaining = daysInMonth - daysPassed;

    const currentSpent = stats.current_month_spent || 0;
    const dailyAverage = stats.daily_average || 0;

    // Simple linear projection
    const projected = currentSpent + dailyAverage * daysRemaining;

    // Calculate confidence based on data consistency
    const confidence = Math.min(
      90,
      Math.max(50, (daysPassed / daysInMonth) * 100),
    );

    return { projected, confidence };
  }

  predictBudgetStatus(stats, projectedSpending) {
    const budget = window.budgetManager.budgets.monthly;
    const currentSpent = stats.current_month_spent || 0;
    const percentageUsed = (currentSpent / budget) * 100;
    const projectedPercentage = (projectedSpending / budget) * 100;

    let status, message, confidence;

    if (projectedPercentage <= 80) {
      status = "✅ On Track";
      message = "Likely to stay within budget";
      confidence = 85;
    } else if (projectedPercentage <= 100) {
      status = "⚠️ Close Call";
      message = "May approach budget limit";
      confidence = 75;
    } else {
      status = "🚨 Over Budget";
      message = `May exceed by ₦${window.app.formatNumber(projectedSpending - budget)}`;
      confidence = 80;
    }

    return { status, message, confidence };
  }

  predictCategoryTrend(stats) {
    const categories = stats.current_month_categories || {};
    const topCategories = Object.entries(categories)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3);

    if (topCategories.length === 0) return null;

    const [topCategory, amount] = topCategories[0];
    const totalSpent = Object.values(categories).reduce((a, b) => a + b, 0);
    const percentage = (amount / totalSpent) * 100;

    let trend;
    if (percentage > 50) {
      trend = `Dominates ${percentage.toFixed(0)}% of spending`;
    } else if (percentage > 30) {
      trend = `Major category at ${percentage.toFixed(0)}%`;
    } else {
      trend = `Balanced spending at ${percentage.toFixed(0)}%`;
    }

    return {
      category: window.app.formatCategoryName(topCategory),
      trend,
      confidence: 70,
    };
  }

  displayPredictions(predictions) {
    const container = document.getElementById("prediction-content");
    if (!container) return;

    container.innerHTML = predictions
      .map(
        (prediction) => `
      <div class="bg-white bg-opacity-20 rounded-lg p-4">
        <h4 class="font-semibold text-white mb-2">${prediction.title}</h4>
        <p class="text-2xl font-bold text-white mb-1">${prediction.value}</p>
        <p class="text-sm text-white opacity-90">${prediction.subtitle}</p>
        <div class="mt-2 flex items-center">
          <div class="flex-1 bg-white bg-opacity-30 rounded-full h-2">
            <div 
              class="bg-white rounded-full h-2 transition-all duration-500" 
              style="width: ${prediction.confidence}%"
            ></div>
          </div>
          <span class="ml-2 text-xs text-white opacity-75">${prediction.confidence}%</span>
        </div>
      </div>
    `,
      )
      .join("");
  }

  async generateSpendingVelocity(stats) {
    const velocities = [];

    // Daily velocity
    const dailyVelocity = stats.daily_average || 0;
    velocities.push({
      title: "Daily Rate",
      value: `₦${window.app.formatNumber(dailyVelocity)}`,
      subtitle: "per day",
      trend: this.calculateVelocityTrend(dailyVelocity, "daily"),
    });

    // Weekly velocity
    const weeklyVelocity = dailyVelocity * 7;
    velocities.push({
      title: "Weekly Rate",
      value: `₦${window.app.formatNumber(weeklyVelocity)}`,
      subtitle: "per week",
      trend: this.calculateVelocityTrend(weeklyVelocity, "weekly"),
    });

    // Transaction frequency
    const transactionRate = stats.transaction_count / (stats.days_tracked || 1);
    velocities.push({
      title: "Transaction Rate",
      value: transactionRate.toFixed(1),
      subtitle: "per day",
      trend: this.calculateVelocityTrend(transactionRate, "transactions"),
    });

    // Spending acceleration
    const acceleration = await this.calculateSpendingAcceleration();
    velocities.push({
      title: "Acceleration",
      value: acceleration.value,
      subtitle: acceleration.direction,
      trend: acceleration.trend,
    });

    this.displayVelocityIndicators(velocities);
  }

  calculateVelocityTrend(value, type) {
    // This is a simplified trend calculation
    // In a real implementation, you'd compare with historical data
    const benchmarks = {
      daily: 1500,
      weekly: 10500,
      transactions: 2,
    };

    const benchmark = benchmarks[type] || 0;
    if (value > benchmark * 1.2) return "high";
    if (value < benchmark * 0.8) return "low";
    return "normal";
  }

  async calculateSpendingAcceleration() {
    try {
      // Get last 14 days of data
      const twoWeeksAgo = new Date();
      twoWeeksAgo.setDate(twoWeeksAgo.getDate() - 14);

      const result = await api.getExpenses({
        range: `${twoWeeksAgo.toISOString().split("T")[0]},${new Date().toISOString().split("T")[0]}`,
      });

      const expenses = result.expenses || [];

      // Split into two weeks
      const oneWeekAgo = new Date();
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);

      const firstWeek = expenses.filter(
        (exp) => new Date(exp.date) < oneWeekAgo,
      );
      const secondWeek = expenses.filter(
        (exp) => new Date(exp.date) >= oneWeekAgo,
      );

      const firstWeekTotal = firstWeek.reduce(
        (sum, exp) => sum + parseFloat(exp.amount),
        0,
      );
      const secondWeekTotal = secondWeek.reduce(
        (sum, exp) => sum + parseFloat(exp.amount),
        0,
      );

      const change = secondWeekTotal - firstWeekTotal;
      const percentageChange =
        firstWeekTotal > 0 ? (change / firstWeekTotal) * 100 : 0;

      let direction, trend, value;

      if (Math.abs(percentageChange) < 5) {
        direction = "Stable";
        trend = "normal";
        value = "±0%";
      } else if (change > 0) {
        direction = "Increasing";
        trend = "high";
        value = `+${percentageChange.toFixed(1)}%`;
      } else {
        direction = "Decreasing";
        trend = "low";
        value = `${percentageChange.toFixed(1)}%`;
      }

      return { value, direction, trend };
    } catch (error) {
      return { value: "N/A", direction: "Unknown", trend: "normal" };
    }
  }

  displayVelocityIndicators(velocities) {
    const container = document.getElementById("velocity-indicators");
    if (!container) return;

    container.innerHTML = velocities
      .map((velocity) => {
        const trendColor =
          velocity.trend === "high"
            ? "text-red-600"
            : velocity.trend === "low"
              ? "text-green-600"
              : "text-blue-600";
        const trendIcon =
          velocity.trend === "high"
            ? "⬆️"
            : velocity.trend === "low"
              ? "⬇️"
              : "➡️";

        return `
        <div class="text-center p-4 border rounded-lg">
          <h4 class="text-sm font-medium text-gray-700 mb-2">${velocity.title}</h4>
          <p class="text-2xl font-bold ${trendColor} mb-1">${velocity.value}</p>
          <p class="text-xs text-gray-500">${velocity.subtitle}</p>
          <div class="mt-2">
            <span class="text-sm ${trendColor}">${trendIcon}</span>
          </div>
        </div>
      `;
      })
      .join("");
  }
}

// Global advanced analytics instance
// window.advancedAnalytics = new AdvancedAnalytics();

// Hook into the existing analytics loading
document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing advanced analytics...");

  setTimeout(() => {
    if (!window.advancedAnalytics) {
      window.advancedAnalytics = new AdvancedAnalytics();
    }

    const originalLoadAnalytics = window.app?.loadAnalytics;
    if (originalLoadAnalytics) {
      window.app.loadAnalytics = async function () {
        await originalLoadAnalytics.call(this);

        // Generate enhanced analytics
        try {
          const stats = await api.getStats();
          await window.advancedAnalytics.generatePredictions(stats);
          await window.advancedAnalytics.generateSpendingVelocity(stats);
        } catch (error) {
          console.error("Error generating advanced analytics:", error);
        }
      };
    }
    console.log("Advanced analytics initialized");
  }, 250);
});
