async function getRecs() {
  const input = document.getElementById("courseInput");
  const container = document.getElementById("resultsList");
  const status = document.querySelector(".div2"); // Use Div 2 for status updates

  if (!input.value.trim()) {
    alert("Enter a course name first, broski!");
    return;
  }

  // UI: Loading State
  container.innerHTML = '<div class="loader">Calculating Similarity...</div>';
  status.innerText = "Status: Processing Math...";

  try {
    const formData = new FormData();
    formData.append("user_id", input.value);

    const response = await fetch("/recommend", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.recs && data.recs.length > 0) {
      // Build the Netflix Cards
      container.innerHTML = data.recs
        .map(
          (course) => `
                <div class="course-card" onclick="window.open('${course["Course URL"]}', '_blank')">
                    <div class="badge">${course["Difficulty Level"]}</div>
                    <h4>${course["Course Name"]}</h4>
                    <p class="univ">${course["University"]}</p>
                    <div class="rating">★ ${course["Course Rating"]}</div>
                </div>
            `
        )
        .join("");
      status.innerText = "Status: Recommendations Found";
    } else {
      container.innerHTML =
        '<p class="error">No matches. Try something else.</p>';
      status.innerText = "Status: No Match Found";
    }
  } catch (err) {
    container.innerHTML = '<p class="error">Server Error. Check terminal.</p>';
    status.innerText = "Status: Error";
  }
}
