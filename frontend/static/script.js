// Global variable to track the chart instance and prevent duplicates
let patternChart = null;

/**
 * Main function to fetch recommendations and update all dashboard zones
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

  // 1. UI Loading State
  resultsContainer.innerHTML =
    '<div class="neon-text">INITIALIZING NEURAL SEARCH...</div>';
  statusDiv.innerHTML = `<span>STATUS:</span> ANALYZING QUERY [${userInput.toUpperCase()}]`;

  try {
    // Prepare data to send to Flask
    const formData = new FormData();
    formData.append("user_id", userInput);

    // 2. FETCH LOGIC: Connecting to the /recommend endpoint
    const response = await fetch("/recommend", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Backend connection failed");

    const data = await response.json();

    if (data.recs && data.recs.length > 0) {
      // 3. Update Div 5: Netflix-style Recommendation Cards
      renderCards(data.recs, resultsContainer);

      // 4. Update Div 4: Evaluation Metrics (Precision/Recall)
      renderMetrics(data.metrics, metricsDiv);

      // 5. Update Div 3: Visualization (Learning Patterns)
      renderChart(data.pattern_data);

      // 6. Update Div 2: AI Reasoning (Explainability)
      statusDiv.innerHTML = `
                <span style="color: var(--accent)">AI LOGIC:</span> ${
                  data.recs[0].reason
                }
                <span style="float:right">PRECISION: ${Math.round(
                  data.metrics.precision * 100
                )}%</span>
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
 * Renders the horizontal scroll cards in Div 5
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
                <span style="font-size:10px; color:var(--accent); opacity:0.7">VIEW COURSE ></span>
            </div>
        </div>
    `
    )
    .join("");
}

/**
 * Updates the Model Metrics in Div 4
 */
function renderMetrics(metrics, container) {
  container.innerHTML = `
        <h3>Model Metrics</h3>
        <div style="margin-top:15px">
            <p class="neon-text" style="font-size:0.85rem">Precision@${
              metrics.k
            }: <span style="color:#fff">${(metrics.precision * 100).toFixed(
    1
  )}%</span></p>
            <p class="neon-text" style="font-size:0.85rem">Recall@${
              metrics.k
            }: <span style="color:#fff">${(metrics.recall * 100).toFixed(
    1
  )}%</span></p>
            <div style="width:100%; height:4px; background:#222; margin-top:10px; border-radius:2px; border: 1px solid var(--accent-glow)">
                <div style="width:${
                  metrics.precision * 100
                }%; height:100%; background:var(--accent); box-shadow:0 0 10px var(--accent)"></div>
            </div>
        </div>
    `;
}

/**
 * Creates/Updates the Line Chart in Div 3 using Chart.js
 */
function renderChart(patternData) {
  const ctx = document.getElementById("patternChart");
  if (!ctx) return;

  // Destroy existing chart to prevent ghosting
  if (patternChart) {
    patternChart.destroy();
  }

  patternChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: patternData.map((_, i) => `M${i + 1}`),
      datasets: [
        {
          label: "Similarity",
          data: patternData,
          borderColor: "#00ff41",
          borderWidth: 2,
          pointRadius: 3,
          tension: 0.4,
          fill: true,
          backgroundColor: "rgba(0, 255, 65, 0.1)",
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
          grid: { display: false },
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
