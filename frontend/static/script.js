// Global variable to track the chart instance and prevent ghosting/memory leaks
let patternChart = null;

/**
 * Main Controller: Fetches data and updates the dashboard zones
 */
async function getRecs() {
  const inputField = document.getElementById("courseInput");
  const resultsContainer = document.getElementById("resultsList");
  const statusDiv = document.querySelector(".div2");
  const metricsDiv = document.querySelector(".div4");

  const userInput = inputField.value.trim();

  if (!userInput) {
    alert("Enter a topic or course name, nacho!");
    return;
  }

  // 1. UI Loading State (Neon Pulse)
  resultsContainer.innerHTML =
    '<div class="neon-text" style="animation: pulse 1.5s infinite">INITIALIZING NEURAL SEARCH...</div>';
  statusDiv.innerHTML = `<span>STATUS:</span> ANALYZING QUERY [${userInput.toUpperCase()}]`;

  try {
    const formData = new FormData();
    formData.append("user_id", userInput);

    // 2. Fetch from Python Backend
    const response = await fetch("/recommend", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Backend connection failed");

    const data = await response.json();

    if (data.recs && data.recs.length > 0) {
      // 3. Update Div 5: Recommendation Cards
      renderCards(data.recs, resultsContainer);

      // 4. Update Div 4: Evaluation Metrics
      renderMetrics(data.metrics, metricsDiv);

      // 5. Update Div 3: Visualization (Similarity Curve)
      renderChart(data.pattern_data);

      // 6. Update Div 2: AI Advisor Reasoning (RAG)
      const advisorText = data.ai_advice || data.recs[0].reason;
      statusDiv.innerHTML = `
                <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
                    <div><span style="color: var(--accent); font-weight: bold;">[AI ADVISOR]:</span> ${advisorText}</div>
                    <div style="font-size: 0.7rem; opacity: 0.6;">SYSTEM OPTIMIZED | P@K: ${Math.round(
                      data.metrics.precision * 100
                    )}%</div>
                </div>
            `;
    } else {
      resultsContainer.innerHTML =
        '<div class="neon-text">NO MATCHING DATA PATHS FOUND.</div>';
      statusDiv.innerText = "STATUS: ZERO RESULTS";
    }
  } catch (error) {
    console.error("Fetch Error:", error);
    resultsContainer.innerHTML =
      '<div class="neon-text" style="color:red">ERROR: CORE CONNECTION FAILED</div>';
    statusDiv.innerText = "STATUS: SYSTEM CRITICAL ERROR";
  }
}

/**
 * Zone: Div 5 - Horizontal Scroll Cards
 */
function renderCards(recs, container) {
  container.innerHTML = recs
    .map(
      (course) => `
        <div class="course-card" onclick="window.open('${course.url}', '_blank')">
            <div class="badge">${course.diff}</div>
            <h4>${course.name}</h4>
            <p class="univ">${course.univ}</p>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top: auto;">
                <span class="rating">★ ${course.rate}</span>
                <span style="font-size:9px; color:var(--accent); letter-spacing:1px;">ACCESS ></span>
            </div>
        </div>
    `
    )
    .join("");
}

/**
 * Zone: Div 4 - Precision & Recall UI
 */
function renderMetrics(metrics, container) {
  container.innerHTML = `
        <h3 style="margin-bottom: 10px;">Model Performance</h3>
        <div style="display: flex; flex-direction: column; gap: 8px;">
            <div>
                <div style="display:flex; justify-content:space-between; font-size: 0.8rem;">
                    <span>Precision@${metrics.k}</span>
                    <span>${(metrics.precision * 100).toFixed(1)}%</span>
                </div>
                <div style="width:100%; height:4px; background:#1a1a1a; margin-top:4px; border-radius:2px;">
                    <div style="width:${
                      metrics.precision * 100
                    }%; height:100%; background:var(--accent); box-shadow:0 0 8px var(--accent)"></div>
                </div>
            </div>
            <div>
                <div style="display:flex; justify-content:space-between; font-size: 0.8rem;">
                    <span>Recall@${metrics.k}</span>
                    <span>${(metrics.recall * 100).toFixed(1)}%</span>
                </div>
                <div style="width:100%; height:4px; background:#1a1a1a; margin-top:4px; border-radius:2px;">
                    <div style="width:${
                      metrics.recall * 100
                    }%; height:100%; background:var(--accent); opacity: 0.7;"></div>
                </div>
            </div>
        </div>
    `;
}

/**
 * Zone: Div 3 - Pattern Chart (Chart.js)
 */
function renderChart(patternData) {
  const ctx = document.getElementById("patternChart");
  if (!ctx) return;

  if (patternChart) {
    patternChart.destroy();
  }

  patternChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: patternData.map((_, i) => `Match ${i + 1}`),
      datasets: [
        {
          label: "Similarity Score",
          data: patternData,
          borderColor: "#00ff41",
          borderWidth: 2,
          pointRadius: 2,
          tension: 0.4,
          fill: true,
          backgroundColor: "rgba(0, 255, 65, 0.05)",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          grid: { color: "#1a1a1a" },
          ticks: { display: false },
        },
        x: {
          grid: { display: false },
          ticks: { color: "#444", font: { size: 9 } },
        },
      },
    },
  });
}

// --- INITIALIZATION & EVENT LISTENERS ---
document.addEventListener("DOMContentLoaded", () => {
  const courseInput = document.getElementById("courseInput");

  if (courseInput) {
    courseInput.addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        event.preventDefault();
        getRecs(); // Triggers search on Enter
      }
    });
  }
});
