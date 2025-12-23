async function getRecs() {
  const input = document.getElementById("courseInput").value;
  const container = document.getElementById("resultsList");
  const status = document.querySelector(".div2");

  if (!input) return alert("Enter a course name");

  status.innerText = "Status: Searching...";

  const formData = new FormData();
  formData.append("user_id", input);

  const response = await fetch("/recommend", {
    method: "POST",
    body: formData,
  });
  const data = await response.json();

  if (data.recs.length > 0) {
    container.innerHTML = data.recs
      .map(
        (course) => `
            <div class="course-card" onclick="window.open('${course.url}', '_blank')">
                <div class="badge">${course.diff}</div>
                <h4>${course.name}</h4>
                <p class="univ">${course.univ}</p>
                <div class="rating">★ ${course.rate}</div>
            </div>
        `
      )
      .join("");
    status.innerText = "Status: Matches Found";
  } else {
    container.innerHTML = "<p>No courses found.</p>";
    status.innerText = "Status: Not Found";
  }
}
