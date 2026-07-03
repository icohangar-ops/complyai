/**
 * ComplyAI Popup Script
 *
 * Handles page scanning, API calls, and result display.
 * Communicates with content script to extract page text,
 * sends it to the backend, and renders compliance results.
 */

const API_BASE = "http://localhost:8787";

// ─── DOM References ──────────────────────────
const scanBtn = document.getElementById("scanBtn");
const loading = document.getElementById("loading");
const error = document.getElementById("error");
const errorText = document.getElementById("errorText");
const retryBtn = document.getElementById("retryBtn");
const results = document.getElementById("results");
const scoreValue = document.getElementById("scoreValue");
const scoreArc = document.getElementById("scoreArc");
const flagsList = document.getElementById("flagsList");
const criticalCount = document.getElementById("criticalCount");
const highCount = document.getElementById("highCount");
const mediumCount = document.getElementById("mediumCount");
const lowCount = document.getElementById("lowCount");
const serverDot = document.getElementById("serverDot");
const serverLabel = document.getElementById("serverLabel");
const noServerMsg = document.getElementById("noServerMsg");
const refreshServerBtn = document.getElementById("refreshServerBtn");

const SEVERITY_COLORS = {
  critical: { bg: "#fef2f2", border: "#dc2626", text: "#991b1b", label: "Critical" },
  high: { bg: "#fff7ed", border: "#f97316", text: "#9a3412", label: "High" },
  medium: { bg: "#fefce8", border: "#eab308", text: "#854d0e", label: "Medium" },
  low: { bg: "#f0f9ff", border: "#3b82f6", text: "#1e40af", label: "Low" },
};

// ─── Initialization ──────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  checkServer();
  scanBtn.addEventListener("click", scanPage);
  retryBtn.addEventListener("click", scanPage);
  refreshServerBtn.addEventListener("click", checkServer);
});

// ─── Server Health Check ─────────────────────
async function checkServer() {
  serverDot.className = "dot dot-offline";
  serverLabel.textContent = "Checking...";

  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      serverDot.className = "dot dot-online";
      serverLabel.textContent = "Connected";
      noServerMsg.classList.add("hidden");
      scanBtn.disabled = false;
    } else {
      throw new Error("Unhealthy");
    }
  } catch {
    serverDot.className = "dot dot-offline";
    serverLabel.textContent = "Offline";
    scanBtn.disabled = true;
  }
}

// ─── Scan Page ───────────────────────────────
async function scanPage() {
  // Reset UI
  hideAll();
  loading.classList.remove("hidden");
  scanBtn.disabled = true;

  try {
    // Step 1: Get page text from content script
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) throw new Error("Could not access current tab");

    const response = await chrome.tabs.sendMessage(tab.id, { action: "scan" });
    if (!response?.text) throw new Error("Could not extract page text");

    const pageText = response.text;
    if (pageText.trim().length < 50) {
      throw new Error("Page content too short to analyze");
    }

    // Step 2: Send to backend for analysis
    const checkRes = await fetch(`${API_BASE}/check`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text: pageText.substring(0, 40000), // Limit
        jurisdiction: "US",
      }),
    });

    if (!checkRes.ok) {
      const detail = await checkRes.json().catch(() => ({}));
      throw new Error(detail.detail || `Server error: ${checkRes.status}`);
    }

    const data = await checkRes.json();

    // Step 3: Render results
    renderResults(data);
  } catch (err) {
    loading.classList.add("hidden");
    error.classList.remove("hidden");
    errorText.textContent = err.message;
    scanBtn.disabled = false;
  }
}

// ─── Render Results ──────────────────────────
function renderResults(data) {
  loading.classList.add("hidden");
  results.classList.remove("hidden");
  scanBtn.disabled = false;

  // Score
  const score = data.score;
  scoreValue.textContent = score;

  // Arc animation
  const circumference = 339.292; // 2 * pi * 54
  const offset = circumference - (score / 100) * circumference;
  scoreArc.style.strokeDasharray = circumference;
  scoreArc.style.strokeDashoffset = offset;

  // Color based on score
  if (score >= 80) {
    scoreArc.style.stroke = "#22c55e"; // green
  } else if (score >= 50) {
    scoreArc.style.stroke = "#eab308"; // yellow
  } else {
    scoreArc.style.stroke = "#ef4444"; // red
  }

  // Summary
  const s = data.summary || { critical: 0, high: 0, medium: 0, low: 0 };
  criticalCount.textContent = `${s.critical} Critical`;
  highCount.textContent = `${s.high} High`;
  mediumCount.textContent = `${s.medium} Medium`;
  lowCount.textContent = `${s.low} Low`;

  criticalCount.className = `badge badge-${s.critical > 0 ? "critical" : "none"}`;
  highCount.className = `badge badge-${s.high > 0 ? "high" : "none"}`;
  mediumCount.className = `badge badge-${s.medium > 0 ? "medium" : "none"}`;
  lowCount.className = `badge badge-${s.low > 0 ? "low" : "none"}`;

  // Flags
  flagsList.innerHTML = "";
  if (!data.flags || data.flags.length === 0) {
    flagsList.innerHTML = '<p class="no-flags">✅ No compliance issues detected</p>';
    return;
  }

  data.flags.forEach((flag) => {
    const color = SEVERITY_COLORS[flag.severity] || SEVERITY_COLORS.medium;
    const flagEl = document.createElement("div");
    flagEl.className = "flag-item";
    flagEl.style.borderLeftColor = color.border;
    flagEl.style.backgroundColor = color.bg;

    flagEl.innerHTML = `
      <div class="flag-header">
        <span class="flag-badge" style="background:${color.border};color:white">${color.label}</span>
        <span class="flag-rule">${flag.rule}</span>
      </div>
      <p class="flag-message">${flag.message}</p>
      <p class="flag-passage">"${escapeHtml(flag.passage)}"</p>
    `;

    flagsList.appendChild(flagEl);
  });
}

// ─── Utilities ───────────────────────────────
function hideAll() {
  loading.classList.add("hidden");
  error.classList.add("hidden");
  results.classList.add("hidden");
  noServerMsg.classList.add("hidden");
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
