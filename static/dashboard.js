// --- Splash screen ---
window.addEventListener("load", () => {
    setTimeout(() => {
        document.getElementById("splash-screen").style.display = "none";
        document.getElementById("app-wrapper").style.display = "";
        loadHomeWidgets();
        loadInventory();
        loadWasteRisk();
    }, 1200);
});

// --- Tab switching ---
document.querySelectorAll(".tab-link").forEach(link => {
    link.addEventListener("click", (e) => {
        e.preventDefault();
        document.querySelectorAll(".tab-link").forEach(l => l.classList.remove("active"));
        document.querySelectorAll(".tab-panel").forEach(p => p.classList.remove("active"));
        link.classList.add("active");
        document.getElementById(link.dataset.tab).classList.add("active");
    });
});

// --- Table rendering helper ---
function renderTable(containerId, rows, columns) {
    const container = document.getElementById(containerId);
    if (!rows.length) {
        container.innerHTML = "<p>No data.</p>";
        return;
    }
    let html = '<table class="table table-dark table-striped"><thead><tr>';
    columns.forEach(col => html += `<th>${col.label}</th>`);
    html += "</tr></thead><tbody>";
    rows.forEach(row => {
        html += "<tr>";
        columns.forEach(col => {
            let value = row[col.key];
            if (col.key === "is_waste_risk") {
                value = value ? '<span class="risk-true">Yes</span>' : '<span class="risk-false">No</span>';
            }
            html += `<td>${value !== undefined && value !== null ? value : "—"}</td>`;
        });
        html += "</tr>";
    });
    html += "</tbody></table>";
    container.innerHTML = html;
}

// --- Home widgets ---
function loadHomeWidgets() {
    Promise.all([
        fetch("/api/inventory").then(r => r.json()),
        fetch("/api/waste-risk").then(r => r.json()),
    ]).then(([inventory, wasteRisk]) => {
        const totalItems = inventory.length;
        const riskCount = wasteRisk.length;
        const totalUnits = inventory.reduce((sum, i) => sum + i.quantity, 0);

        const widgetRow = document.getElementById("widget-row");
        widgetRow.innerHTML = `
            <div class="col-md-4">
                <div class="widget-card" style="background:#1B268E;">
                    <h6>Total Items Tracked</h6>
                    <h2>${totalItems}</h2>
                </div>
            </div>
            <div class="col-md-4">
                <div class="widget-card" style="background:#8B1E3F;">
                    <h6>Waste-Risk Items</h6>
                    <h2>${riskCount}</h2>
                </div>
            </div>
            <div class="col-md-4">
                <div class="widget-card" style="background:#2E7D32;">
                    <h6>Total Units in Stock</h6>
                    <h2>${totalUnits.toFixed(0)}</h2>
                </div>
            </div>
        `;
    });
}

function loadInventory() {
    fetch("/api/inventory").then(res => res.json()).then(data =>
        renderTable("inventory-table", data, [
            { key: "name", label: "Item" }, { key: "quantity", label: "Quantity" },
            { key: "unit", label: "Unit" }, { key: "expiry_date", label: "Expiry Date" },
            { key: "reorder_threshold", label: "Reorder Threshold" },
        ]));
}

function loadWasteRisk() {
    fetch("/api/waste-risk").then(res => res.json()).then(data =>
        renderTable("waste-risk-table", data, [
            { key: "name", label: "Item" }, { key: "quantity", label: "Quantity" },
            { key: "expiry_date", label: "Expiry Date" },
        ]));
}

function loadPredict() {
    const date = document.getElementById("predict-date").value;
    fetch(`/api/predict?date=${date}`).then(res => res.json()).then(data =>
        renderTable("predict-table", data, [
            { key: "name", label: "Item" }, { key: "predicted_quantity", label: "Predicted Quantity" },
        ]));
}

function loadRecommend() {
    const date = document.getElementById("recommend-date").value;
    fetch(`/api/recommend?date=${date}`).then(res => res.json()).then(data =>
        renderTable("recommend-table", data, [
            { key: "name", label: "Item" }, { key: "current_quantity", label: "Current Qty" },
            { key: "predicted_quantity", label: "Predicted Qty" }, { key: "recommended_order_qty", label: "Recommend Order" },
            { key: "is_waste_risk", label: "Waste Risk" },
        ]));
}

document.getElementById("predict-btn").addEventListener("click", loadPredict);
document.getElementById("recommend-btn").addEventListener("click", loadRecommend);