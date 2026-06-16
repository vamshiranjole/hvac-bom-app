const API_URL = "https://hvac-bom-app-production.up.railway.app";

const jobId = new URLSearchParams(window.location.search).get("job");

function checkStatus() {
    fetch(`${API_URL}/jobs/${jobId}`, {headers: {"x-api-key": "hvac2024securekey123456789abc"}})
        .then(res => res.json())
        .then(data => {
            updateProgress(data.status);
            if (data.status === "complete") {
                clearInterval(interval);
                fetchResult();
            } else if (data.status && data.status.startsWith("failed")) {
                clearInterval(interval);
                showError(data.status);
            }
        })
        .catch(err => console.error(err));
}

function updateProgress(status) {
    const steps = ["step1", "step2", "step3", "step4", "step5"];
    const statusMap = {
        "queued": 1,
        "processing": 3,
        "complete": 5
    };
    const activeStep = statusMap[status] || 1;
    steps.forEach((id, index) => {
        const el = document.getElementById(id);
        if (!el) return;
        if (index + 1 < activeStep) {
            el.classList.add("done");
            el.classList.remove("active");
        } else if (index + 1 === activeStep) {
            el.classList.add("active");
            el.classList.remove("done");
        }
    });
}

function fetchResult() {
    fetch(`${API_URL}/jobs/${jobId}/result`, {headers: {"x-api-key": "hvac2024securekey123456789abc"}})
        .then(res => res.json())
        .then(data => {
            renderBOM(data);
            updateSummary(data);
        });
}

function renderBOM(data) {
    const tbody = document.getElementById("bom-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";

    data.bom.forEach(item => {
        const tr = document.createElement("tr");
        const colorMap = {
            "auto_approved": "#D1FAE5",
            "likely_ok": "#FEF9C3",
            "needs_review": "#FFEDD5",
            "manual_required": "#FEE2E2"
        };
        tr.style.background = colorMap[item.review_status] || "white";
        tr.innerHTML = `
            <td class="px-4 py-3 font-medium">${item.equipment_tag || "-"}</td>
            <td class="px-4 py-3">${item.equipment_type || "-"}</td>
            <td class="px-4 py-3">${item.manufacturer || "-"}</td>
            <td class="px-4 py-3">${item.model_number || "-"}</td>
            <td class="px-4 py-3">${item.quantity || "-"}</td>
            <td class="px-4 py-3">${item.capacity || "-"}</td>
            <td class="px-4 py-3">${item.voltage || "-"}</td>
            <td class="px-4 py-3">${item.confidence_score ? Math.round(item.confidence_score * 100) + "%" : "-"}</td>
            <td class="px-4 py-3"><span class="px-2 py-0.5 rounded-full text-xs">${item.review_status || "-"}</span></td>
        `;
        tbody.appendChild(tr);
    });
}

function updateSummary(data) {
    const itemCount = document.getElementById("item-count");
    const reviewCount = document.getElementById("review-count");
    const issueCount = document.getElementById("issue-count");

    if (itemCount) itemCount.textContent = data.item_count || 0;
    if (reviewCount) reviewCount.textContent = data.bom ? data.bom.filter(i => i.review_status === "needs_review" || i.review_status === "manual_required").length : 0;
    if (issueCount) issueCount.textContent = data.issues ? data.issues.length : 0;
}

function showError(status) {
    const el = document.getElementById("error-message");
    if (el) {
        el.textContent = "Processing failed: " + status;
        el.style.display = "block";
    }
}

let interval;
if (jobId) {
    interval = setInterval(checkStatus, 3000);
    checkStatus();
} else {
    showError("No job ID found in URL.");
}
