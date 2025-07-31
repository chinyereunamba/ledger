// Progressive Web App functionality
class PWAManager {
  constructor() {
    this.deferredPrompt = null;
    this.init();
  }

  init() {
    // Register service worker
    this.registerServiceWorker();

    // Handle install prompt
    this.setupInstallPrompt();

    // Handle app updates
    this.handleAppUpdates();

    // Setup offline detection
    this.setupOfflineDetection();
  }

  async registerServiceWorker() {
    if ("serviceWorker" in navigator) {
      try {
        const registration = await navigator.serviceWorker.register("/sw.js");
        console.log("Service Worker registered successfully:", registration);

        // Handle updates
        registration.addEventListener("updatefound", () => {
          const newWorker = registration.installing;
          newWorker.addEventListener("statechange", () => {
            if (
              newWorker.state === "installed" &&
              navigator.serviceWorker.controller
            ) {
              this.showUpdateAvailable();
            }
          });
        });
      } catch (error) {
        console.error("Service Worker registration failed:", error);
      }
    }
  }

  setupInstallPrompt() {
    window.addEventListener("beforeinstallprompt", (e) => {
      // Prevent the mini-infobar from appearing on mobile
      e.preventDefault();

      // Save the event so it can be triggered later
      this.deferredPrompt = e;

      // Show install button
      this.showInstallButton();
    });

    // Handle successful installation
    window.addEventListener("appinstalled", () => {
      console.log("PWA was installed");
      this.hideInstallButton();
      this.showToast("App installed successfully!", "success");
    });
  }

  showInstallButton() {
    // Create install button if it doesn't exist
    let installBtn = document.getElementById("install-btn");
    if (!installBtn) {
      installBtn = document.createElement("button");
      installBtn.id = "install-btn";
      installBtn.className =
        "fixed bottom-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-blue-600 transition-colors z-50";
      installBtn.innerHTML = "📱 Install App";
      installBtn.onclick = () => this.installApp();
      document.body.appendChild(installBtn);
    }
    installBtn.style.display = "block";
  }

  hideInstallButton() {
    const installBtn = document.getElementById("install-btn");
    if (installBtn) {
      installBtn.style.display = "none";
    }
  }

  async installApp() {
    if (!this.deferredPrompt) return;

    // Show the install prompt
    this.deferredPrompt.prompt();

    // Wait for the user to respond to the prompt
    const { outcome } = await this.deferredPrompt.userChoice;

    if (outcome === "accepted") {
      console.log("User accepted the install prompt");
    } else {
      console.log("User dismissed the install prompt");
    }

    // Clear the deferredPrompt
    this.deferredPrompt = null;
    this.hideInstallButton();
  }

  handleAppUpdates() {
    // Listen for service worker updates
    navigator.serviceWorker?.addEventListener("controllerchange", () => {
      // Reload the page to get the latest version
      window.location.reload();
    });
  }

  showUpdateAvailable() {
    // Create update notification
    const updateDiv = document.createElement("div");
    updateDiv.className =
      "fixed top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-6 py-3 rounded-lg shadow-lg z-50";
    updateDiv.innerHTML = `
            <div class="flex items-center space-x-3">
                <span>New version available!</span>
                <button onclick="pwa.updateApp()" class="bg-white text-blue-500 px-3 py-1 rounded text-sm font-medium">
                    Update
                </button>
                <button onclick="this.parentElement.parentElement.remove()" class="text-white hover:text-gray-200">
                    ✕
                </button>
            </div>
        `;
    document.body.appendChild(updateDiv);
  }

  updateApp() {
    // Skip waiting and activate new service worker
    navigator.serviceWorker?.getRegistration().then((registration) => {
      if (registration?.waiting) {
        registration.waiting.postMessage({ type: "SKIP_WAITING" });
      }
    });
  }

  setupOfflineDetection() {
    // Show offline indicator
    window.addEventListener("offline", () => {
      this.showOfflineIndicator();
    });

    window.addEventListener("online", () => {
      this.hideOfflineIndicator();
      this.showToast("Back online!", "success");
    });

    // Check initial state
    if (!navigator.onLine) {
      this.showOfflineIndicator();
    }
  }

  showOfflineIndicator() {
    let offlineDiv = document.getElementById("offline-indicator");
    if (!offlineDiv) {
      offlineDiv = document.createElement("div");
      offlineDiv.id = "offline-indicator";
      offlineDiv.className =
        "fixed top-0 left-0 right-0 bg-red-500 text-white text-center py-2 z-50";
      offlineDiv.innerHTML = "📡 You are offline. Some features may not work.";
      document.body.appendChild(offlineDiv);
    }
    offlineDiv.style.display = "block";
  }

  hideOfflineIndicator() {
    const offlineDiv = document.getElementById("offline-indicator");
    if (offlineDiv) {
      offlineDiv.style.display = "none";
    }
  }

  showToast(message, type = "info") {
    // Use the app's toast system if available
    if (window.app && window.app.showToast) {
      window.app.showToast(message, type);
    } else {
      console.log(`${type.toUpperCase()}: ${message}`);
    }
  }

  // Check if app is running as PWA
  isRunningAsPWA() {
    return (
      window.matchMedia("(display-mode: standalone)").matches ||
      window.navigator.standalone === true
    );
  }

  // Get app info
  getAppInfo() {
    return {
      isOnline: navigator.onLine,
      isPWA: this.isRunningAsPWA(),
      hasServiceWorker: "serviceWorker" in navigator,
      canInstall: !!this.deferredPrompt,
    };
  }
}

// Create global PWA instance
const pwa = new PWAManager();

// Export for use in other modules
if (typeof module !== "undefined" && module.exports) {
  module.exports = PWAManager;
}
