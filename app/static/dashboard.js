(function () {
  "use strict";

  const scriptTag = document.currentScript;
  const targetDate = scriptTag.getAttribute("data-date");

  const STATUS_COLORS = {
    booked: "#3b82f6",
    completed: "#10b981",
    cancelled: "#ef4444",
    no_show: "#f59e0b"
  };

  async function fetchJson(url) {
    const response = await fetch(url, {
      headers: { Accept: "application/json" },
      credentials: "same-origin"
    });
    if (!response.ok) {
      throw new Error("Request failed with status " + response.status);
    }
    return response.json();
  }

  function renderStatusChart(data) {
    const labels = Object.keys(data);
    const values = labels.map(function (key) { return data[key]; });
    const colors = labels.map(function (key) {
      return STATUS_COLORS[key] || "#6b7280";
    });

    new Chart(document.getElementById("statusChart"), {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [{ data: values, backgroundColor: colors }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } }
      }
    });
  }

  function renderRevenueChart(rows) {
    const labels = rows.map(function (row) { return row.service_name; });
    const values = rows.map(function (row) {
      return (row.revenue_cents || 0) / 100;
    });

    new Chart(document.getElementById("revenueChart"), {
      type: "bar",
      data: {
        labels: labels,
        datasets: [{
          label: "Ingresos (EUR)",
          data: values,
          backgroundColor: "#8b5cf6"
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  function init() {
    const query = "?date=" + encodeURIComponent(targetDate);

    fetchJson("/api/status-breakdown" + query)
      .then(renderStatusChart)
      .catch(function (err) { console.error("status chart:", err); });

    fetchJson("/api/revenue-by-service" + query)
      .then(renderRevenueChart)
      .catch(function (err) { console.error("revenue chart:", err); });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
