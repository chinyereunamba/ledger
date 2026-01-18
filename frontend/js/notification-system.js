// Enhanced Notification System
class NotificationSystem {
  constructor() {
    this.notifications = [];
    this.settings = {
      budgetAlerts: true,
      dailyReminders: true,
      achievementNotifications: true,
      browserNotifications: false,
    };
    this.init();
  }

  init() {
    this.loadSettings();
    this.requestNotificationPermission();
    this.setupPeriodicChecks();
    this.createNotificationCenter();
  }

  loadSettings() {
    const saved = localStorage.getItem("quickledger-notification-settings");
    if (saved) {
      this.settings = { ...this.settings, ...JSON.parse(saved) };
    }
  }

  saveSettings() {
    localStorage.setItem(
      "quickledger-notification-settings",
      JSON.stringify(this.settings),
    );
  }

  async requestNotificationPermission() {
    if ("Notification" in window && this.settings.browserNotifications) {
      const permission = await Notification.requestPermission();
      this.settings.browserNotifications = permission === "granted";
      this.saveSettings();
    }
  }

  setupPeriodicChecks() {
    // Check for budget alerts every 5 minutes
    setInterval(
      () => {
        this.checkBudgetAlerts();
      },
      5 * 60 * 1000,
    );

    // Check for daily reminders
    this.checkDailyReminders();
    setInterval(
      () => {
        this.checkDailyReminders();
      },
      60 * 60 * 1000,
    ); // Every hour
  }

  createNotificationCenter() {
    const container = document.createElement("div");
    container.id = "notification-center";
    container.className = "fixed top-20 right-4 w-80 z-40 space-y-2";
    document.body.appendChild(container);
  }

  async checkBudgetAlerts() {
    if (!this.settings.budgetAlerts || !window.budgetManager) return;

    try {
      const stats = await api.getStats();
      const alerts = window.budgetManager.getBudgetAlerts(stats);

      alerts.forEach((alert) => {
        this.showNotification({
          type: "warning",
          title: "Budget Alert",
          message: alert.message,
          persistent: true,
          actions: [
            {
              text: "View Budget",
              action: () => window.budgetManager.showBudgetModal(),
            },
          ],
        });
      });
    } catch (error) {
      console.error("Error checking budget alerts:", error);
    }
  }

  checkDailyReminders() {
    if (!this.settings.dailyReminders) return;

    const now = new Date();
    const lastReminder = localStorage.getItem("quickledger-last-reminder");
    const today = now.toDateString();

    // Show reminder if it's evening and no expenses logged today
    if (now.getHours() >= 18 && lastReminder !== today) {
      this.checkTodayExpenses().then((hasExpenses) => {
        if (!hasExpenses) {
          this.showNotification({
            type: "info",
            title: "Daily Reminder",
            message: "Don't forget to log your expenses for today!",
            actions: [
              {
                text: "Add Expense",
                action: () => {
                  window.app.showSection("add");
                  this.dismissNotification();
                },
              },
            ],
          });
          localStorage.setItem("quickledger-last-reminder", today);
        }
      });
    }
  }

  async checkTodayExpenses() {
    try {
      const today = new Date().toISOString().split("T")[0];
      const result = await api.getExpenses({ date: today });
      return result.expenses && result.expenses.length > 0;
    } catch (error) {
      return false;
    }
  }

  showNotification(options) {
    const notification = {
      id: Date.now() + Math.random(),
      type: options.type || "info",
      title: options.title || "Notification",
      message: options.message || "",
      persistent: options.persistent || false,
      actions: options.actions || [],
      timestamp: new Date(),
    };

    this.notifications.push(notification);
    this.renderNotification(notification);

    // Show browser notification if enabled
    if (this.settings.browserNotifications && "Notification" in window) {
      new Notification(notification.title, {
        body: notification.message,
        icon: "/icons/icon-192x192.png",
      });
    }

    // Auto-dismiss non-persistent notifications
    if (!notification.persistent) {
      setTimeout(() => {
        this.dismissNotification(notification.id);
      }, 5000);
    }

    return notification.id;
  }

  renderNotification(notification) {
    const container = document.getElementById("notification-center");
    if (!container) return;

    const notificationEl = document.createElement("div");
    notificationEl.id = `notification-${notification.id}`;
    notificationEl.className = `notification-card bg-white rounded-lg shadow-lg border-l-4 p-4 transform transition-all duration-300 translate-x-full ${this.getNotificationStyles(notification.type)}`;

    notificationEl.innerHTML = `
      <div class="flex justify-between items-start">
        <div class="flex-1">
          <div class="flex items-center">
            <span class="notification-icon mr-2">${this.getNotificationIcon(notification.type)}</span>
            <h4 class="font-semibold text-gray-900">${notification.title}</h4>
          </div>
          <p class="text-sm text-gray-600 mt-1">${notification.message}</p>
          ${
            notification.actions.length > 0
              ? `
            <div class="flex space-x-2 mt-3">
              ${notification.actions
                .map(
                  (action) => `
                <button
                  onclick="notificationSystem.executeAction('${notification.id}', ${notification.actions.indexOf(action)})"
                  class="text-xs bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition-colors"
                >
                  ${action.text}
                </button>
              `,
                )
                .join("")}
            </div>
          `
              : ""
          }
        </div>
        <button
          onclick="notificationSystem.dismissNotification('${notification.id}')"
          class="text-gray-400 hover:text-gray-600 ml-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    `;

    container.appendChild(notificationEl);

    // Animate in
    setTimeout(() => {
      notificationEl.classList.remove("translate-x-full");
    }, 100);
  }

  getNotificationStyles(type) {
    switch (type) {
      case "success":
        return "border-green-500";
      case "warning":
        return "border-yellow-500";
      case "error":
        return "border-red-500";
      case "info":
      default:
        return "border-blue-500";
    }
  }

  getNotificationIcon(type) {
    switch (type) {
      case "success":
        return "✅";
      case "warning":
        return "⚠️";
      case "error":
        return "❌";
      case "info":
      default:
        return "ℹ️";
    }
  }

  executeAction(notificationId, actionIndex) {
    const notification = this.notifications.find((n) => n.id == notificationId);
    if (notification && notification.actions[actionIndex]) {
      notification.actions[actionIndex].action();
      this.dismissNotification(notificationId);
    }
  }

  dismissNotification(notificationId) {
    const notificationEl = document.getElementById(
      `notification-${notificationId}`,
    );
    if (notificationEl) {
      notificationEl.classList.add("translate-x-full");
      setTimeout(() => {
        notificationEl.remove();
      }, 300);
    }

    // Remove from array
    this.notifications = this.notifications.filter(
      (n) => n.id != notificationId,
    );
  }

  // Achievement system
  checkAchievements(stats) {
    if (!this.settings.achievementNotifications) return;

    const achievements = [];

    // First expense achievement
    if (stats.transaction_count === 1) {
      achievements.push({
        title: "🎉 First Step!",
        message:
          "You logged your first expense! Great start to tracking your finances.",
      });
    }

    // Milestone achievements
    if ([10, 50, 100, 500].includes(stats.transaction_count)) {
      achievements.push({
        title: "🏆 Milestone Reached!",
        message: `You've logged ${stats.transaction_count} expenses! Keep up the great work.`,
      });
    }

    // Budget adherence achievement
    if (window.budgetManager && window.budgetManager.budgets.monthly > 0) {
      const monthlySpent = stats.current_month_spent || 0;
      const budget = window.budgetManager.budgets.monthly;
      const percentage = (monthlySpent / budget) * 100;

      if (percentage <= 80 && stats.days_tracked >= 15) {
        achievements.push({
          title: "💰 Budget Master!",
          message: `You're staying within 80% of your monthly budget. Excellent financial discipline!`,
        });
      }
    }

    // Consistency achievement
    if (stats.days_tracked >= 30) {
      achievements.push({
        title: "📅 Consistency Champion!",
        message: `You've been tracking expenses for ${stats.days_tracked} days. Consistency is key to financial success!`,
      });
    }

    // Show achievements
    achievements.forEach((achievement) => {
      this.showNotification({
        type: "success",
        title: achievement.title,
        message: achievement.message,
        persistent: false,
      });
    });
  }

  // Settings management
  showNotificationSettings() {
    const modal = this.createSettingsModal();
    document.body.appendChild(modal);
    modal.classList.remove("hidden");
  }

  createSettingsModal() {
    const modal = document.createElement("div");
    modal.id = "notification-settings-modal";
    modal.className =
      "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50";

    modal.innerHTML = `
      <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4 modal-content">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-lg font-semibold text-gray-900">Notification Settings</h3>
          <button onclick="notificationSystem.closeSettingsModal()" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-gray-700">Budget Alerts</label>
            <input
              type="checkbox"
              id="budget-alerts-toggle"
              ${this.settings.budgetAlerts ? "checked" : ""}
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </div>
          
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-gray-700">Daily Reminders</label>
            <input
              type="checkbox"
              id="daily-reminders-toggle"
              ${this.settings.dailyReminders ? "checked" : ""}
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </div>
          
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-gray-700">Achievement Notifications</label>
            <input
              type="checkbox"
              id="achievement-notifications-toggle"
              ${this.settings.achievementNotifications ? "checked" : ""}
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </div>
          
          <div class="flex items-center justify-between">
            <label class="text-sm font-medium text-gray-700">Browser Notifications</label>
            <input
              type="checkbox"
              id="browser-notifications-toggle"
              ${this.settings.browserNotifications ? "checked" : ""}
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
          </div>
        </div>
        
        <div class="flex justify-end space-x-3 mt-6 pt-4 border-t">
          <button
            onclick="notificationSystem.closeSettingsModal()"
            class="bg-gray-300 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-400 transition-colors"
          >
            Cancel
          </button>
          <button
            onclick="notificationSystem.saveNotificationSettings()"
            class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
          >
            Save Settings
          </button>
        </div>
      </div>
    `;

    return modal;
  }

  saveNotificationSettings() {
    this.settings.budgetAlerts = document.getElementById(
      "budget-alerts-toggle",
    ).checked;
    this.settings.dailyReminders = document.getElementById(
      "daily-reminders-toggle",
    ).checked;
    this.settings.achievementNotifications = document.getElementById(
      "achievement-notifications-toggle",
    ).checked;
    this.settings.browserNotifications = document.getElementById(
      "browser-notifications-toggle",
    ).checked;

    this.saveSettings();

    // Request permission if browser notifications enabled
    if (this.settings.browserNotifications) {
      this.requestNotificationPermission();
    }

    this.closeSettingsModal();
    window.app.showToast("Notification settings saved!", "success");
  }

  closeSettingsModal() {
    const modal = document.getElementById("notification-settings-modal");
    if (modal) {
      modal.classList.add("hidden");
      document.body.removeChild(modal);
    }
  }

  // Clear all notifications
  clearAllNotifications() {
    this.notifications.forEach((notification) => {
      this.dismissNotification(notification.id);
    });
  }
}

// Global notification system instance
// window.notificationSystem = new NotificationSystem();

// Global functions
function showNotificationSettings() {
  console.log("showNotificationSettings called");
  if (window.notificationSystem) {
    window.notificationSystem.showNotificationSettings();
  } else {
    console.error("Notification system not loaded");
  }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  console.log("Initializing notification system...");

  setTimeout(() => {
    if (!window.notificationSystem) {
      window.notificationSystem = new NotificationSystem();
    }

    // Hook into app events to show achievements
    const originalLoadDashboard = window.app?.loadDashboard;
    if (originalLoadDashboard) {
      window.app.loadDashboard = async function () {
        await originalLoadDashboard.call(this);

        // Check for achievements after loading dashboard
        try {
          const stats = await api.getStats();
          window.notificationSystem.checkAchievements(stats);
        } catch (error) {
          console.error("Error checking achievements:", error);
        }
      };
    }
    console.log("Notification system initialized");
  }, 200);
});
