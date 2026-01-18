// Simple Budget Manager
console.log("Loading simple budget manager...");

// Global budget state
window.budgetState = {
  monthly: parseFloat(localStorage.getItem("monthlyBudget") || "0"),
  categories: JSON.parse(localStorage.getItem("categoryBudgets") || "{}"),
};

function showEnhancedBudgetModal() {
  console.log("showEnhancedBudgetModal called");

  // Create a simple budget modal
  const modal = document.createElement("div");
  modal.id = "budget-modal-simple";
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
    <div style="background: white; padding: 30px; border-radius: 8px; max-width: 500px; width: 90%;">
      <h3 style="margin-top: 0; margin-bottom: 20px; font-size: 20px;">Set Monthly Budget</h3>
      
      <div style="margin-bottom: 20px;">
        <label style="display: block; margin-bottom: 5px; font-weight: bold;">Monthly Budget Amount (₦)</label>
        <input 
          type="number" 
          id="budget-amount-input" 
          value="${window.budgetState.monthly}"
          style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px;"
          placeholder="Enter your monthly budget"
        />
      </div>
      
      <div style="display: flex; gap: 10px; justify-content: flex-end;">
        <button 
          onclick="closeBudgetModal()"
          style="padding: 10px 20px; background: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer;"
        >
          Cancel
        </button>
        <button 
          onclick="saveBudget()"
          style="padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;"
        >
          Save Budget
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Focus on input
  setTimeout(() => {
    const input = document.getElementById("budget-amount-input");
    if (input) input.focus();
  }, 100);
}

function closeBudgetModal() {
  const modal = document.getElementById("budget-modal-simple");
  if (modal) {
    document.body.removeChild(modal);
  }
}

function saveBudget() {
  const input = document.getElementById("budget-amount-input");
  const amount = parseFloat(input.value);

  if (isNaN(amount) || amount < 0) {
    alert("Please enter a valid budget amount");
    return;
  }

  // Save to localStorage
  localStorage.setItem("monthlyBudget", amount.toString());
  window.budgetState.monthly = amount;

  // Show success message
  if (window.app && window.app.showToast) {
    window.app.showToast(
      `Monthly budget set to ₦${amount.toLocaleString()}!`,
      "success",
    );
  } else {
    alert(`Monthly budget set to ₦${amount.toLocaleString()}!`);
  }

  // Close modal
  closeBudgetModal();

  // Refresh dashboard if available
  if (window.app && window.app.loadDashboard) {
    window.app.loadDashboard();
  }

  console.log("Budget saved:", amount);
}

// Override the global setBudget function
window.setBudget = showEnhancedBudgetModal;

console.log("Simple budget manager loaded");
