// Simple Notification System
console.log("Loading simple notification system...");

function showNotificationSettings() {
  console.log("showNotificationSettings called");

  // Create a simple settings modal
  const modal = document.createElement("div");
  modal.id = "notification-settings-modal-simple";
  modal.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  `;

  modal.innerHTML = `
    <div style="background: white; padding: 30px; border-radius: 8px; max-width: 400px; width: 90%;">
      <h3 style="margin-top: 0; margin-bottom: 20px; font-size: 20px;">Notification Settings</h3>
      
      <div style="margin-bottom: 15px;">
        <label style="display: flex; align-items: center; cursor: pointer;">
          <input type="checkbox" id="budget-alerts" checked style="margin-right: 10px;">
          <span>Budget Alerts</span>
        </label>
      </div>
      
      <div style="margin-bottom: 15px;">
        <label style="display: flex; align-items: center; cursor: pointer;">
          <input type="checkbox" id="daily-reminders" checked style="margin-right: 10px;">
          <span>Daily Reminders</span>
        </label>
      </div>
      
      <div style="margin-bottom: 20px;">
        <label style="display: flex; align-items: center; cursor: pointer;">
          <input type="checkbox" id="achievement-notifications" checked style="margin-right: 10px;">
          <span>Achievement Notifications</span>
        </label>
      </div>
      
      <div style="display: flex; gap: 10px; justify-content: flex-end;">
        <button 
          onclick="closeNotificationSettings()"
          style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;"
        >
          Cancel
        </button>
        <button 
          onclick="saveNotificationSettings()"
          style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;"
        >
          Save Settings
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);
}

function closeNotificationSettings() {
  const modal = document.getElementById("notification-settings-modal-simple");
  if (modal) {
    document.body.removeChild(modal);
  }
}

function saveNotificationSettings() {
  const budgetAlerts = document.getElementById("budget-alerts").checked;
  const dailyReminders = document.getElementById("daily-reminders").checked;
  const achievementNotifications = document.getElementById(
    "achievement-notifications",
  ).checked;

  // Save to localStorage
  const settings = {
    budgetAlerts,
    dailyReminders,
    achievementNotifications,
  };

  localStorage.setItem("notificationSettings", JSON.stringify(settings));

  // Show success message
  if (window.app && window.app.showToast) {
    window.app.showToast("Notification settings saved!", "success");
  } else {
    alert("Notification settings saved!");
  }

  closeNotificationSettings();
  console.log("Notification settings saved:", settings);
}

console.log("Simple notification system loaded");
