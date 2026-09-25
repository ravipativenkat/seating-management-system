function showResult(el, data, isError) {
  el.style.display = "block";
  el.className = "result-box " + (isError ? "error" : "success");
  el.textContent = data.error ? data.error : data.message;
}

document.getElementById("ai-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const prompt = document.getElementById("ai-prompt").value;
  const resultEl = document.getElementById("ai-result");
  resultEl.style.display = "block";
  resultEl.className = "result-box";
  resultEl.textContent = "Thinking...";

  try {
    const res = await fetch("/api/ai-assist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt }),
    });
    const data = await res.json();
    showResult(resultEl, data, !res.ok);
    if (res.ok) setTimeout(() => location.reload(), 1200);
  } catch (err) {
    showResult(resultEl, { error: "Network error: " + err }, true);
  }
});

document.getElementById("manual-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const employee_id = document.getElementById("manual-employee").value;
  const seat_label = document.getElementById("manual-seat").value || null;
  const resultEl = document.getElementById("manual-result");

  try {
    const res = await fetch("/api/assign", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ employee_id, seat_label }),
    });
    const data = await res.json();
    showResult(resultEl, data, !res.ok);
    if (res.ok) setTimeout(() => location.reload(), 800);
  } catch (err) {
    showResult(resultEl, { error: "Network error: " + err }, true);
  }
});

document.getElementById("add-employee-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("emp-name").value;
  const department = document.getElementById("emp-dept").value;
  const res = await fetch("/api/employees", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, department }),
  });
  if (res.ok) location.reload();
  else alert((await res.json()).error);
});

document.getElementById("add-seat-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const label = document.getElementById("seat-label").value;
  const floor = document.getElementById("seat-floor").value;
  const res = await fetch("/api/seats", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ label, floor }),
  });
  if (res.ok) location.reload();
  else alert((await res.json()).error);
});
