/* ==========================================
   BevInsight AI Copilot - Application Logic
   ========================================== */

document.addEventListener("DOMContentLoaded", () => {
    // API endpoint definitions
    const API_HEALTH = "/api/health";
    const API_DASHBOARD = "/api/dashboard";
    const API_ALERTS = "/api/alerts";
    const API_QUERY = "/api/query";

    // Chart.js instances (stored globally to allow re-rendering)
    let weeklyTrendChartInstance = null;
    let regionalChartInstance = null;
    let categoryChartInstance = null;

    // DOM Elements
    const currentTimeEl = document.getElementById("current-time");
    const backendStatusEl = document.getElementById("backend-status");
    const refreshDashboardBtn = document.getElementById("refresh-dashboard-btn");

    // KPI Elements
    const kpiRevenueEl = document.getElementById("kpi-revenue");
    const kpiUnitsEl = document.getElementById("kpi-units");
    const kpiPromoPctEl = document.getElementById("kpi-promo-pct");
    const kpiTopProductEl = document.getElementById("kpi-top-product");
    const kpiTopRegionEl = document.getElementById("kpi-top-region");
    const kpiInventoryRiskEl = document.getElementById("kpi-inventory-risk");

    // Tabs & Navigation
    const tabChatBtn = document.getElementById("tab-chat-btn");
    const tabAlertsBtn = document.getElementById("tab-alerts-btn");
    const tabChatContent = document.getElementById("tab-chat");
    const tabAlertsContent = document.getElementById("tab-alerts");
    const alertsCountBadge = document.getElementById("alerts-count-badge");

    // Chat Elements
    const chatMessagesContainer = document.getElementById("chat-messages");
    const chatInputForm = document.getElementById("chat-input-form");
    const chatInputField = document.getElementById("chat-input-field");
    const templatePills = document.querySelectorAll(".template-pill");

    // Inspector Elements
    const dataInspectorPanel = document.getElementById("data-inspector");
    const closeInspectorBtn = document.getElementById("close-inspector-btn");
    const copySqlBtn = document.getElementById("copy-sql-btn");
    const generatedSqlCodeEl = document.getElementById("generated-sql-code");
    const queryResultsTable = document.getElementById("query-results-table");

    // Alerts List Container
    const alertsListEl = document.getElementById("alerts-list");

    // Update time clock
    function updateClock() {
        const now = new Date();
        currentTimeEl.textContent = now.toLocaleTimeString() + " (Local)";
    }
    setInterval(updateClock, 1000);
    updateClock();

    // Check Backend Connection Health
    async function checkHealth() {
        try {
            const res = await fetch(API_HEALTH);
            const data = await res.json();
            if (data.status === "healthy") {
                backendStatusEl.textContent = "SQLite & Gemini Active";
                const dot = backendStatusEl.previousElementSibling;
                dot.className = "badge-dot pulse-green";
            } else {
                setBackendOffline(data.database || "Unhealthy status");
            }
        } catch (err) {
            setBackendOffline(err.message);
        }
    }

    function setBackendOffline(errText) {
        backendStatusEl.textContent = "Backend Offline";
        const dot = backendStatusEl.previousElementSibling;
        dot.className = "badge-dot";
        dot.style.backgroundColor = "#ef4444";
        dot.style.boxShadow = "0 0 8px #ef4444";
        console.error("Backend health failure:", errText);
    }

    // Toggle Panels (Chat / Alerts)
    tabChatBtn.addEventListener("click", () => {
        tabChatBtn.classList.add("active");
        tabAlertsBtn.classList.remove("active");
        tabChatContent.classList.add("active");
        tabAlertsContent.classList.remove("active");
    });

    tabAlertsBtn.addEventListener("click", () => {
        tabAlertsBtn.classList.add("active");
        tabChatBtn.classList.remove("active");
        tabAlertsContent.classList.add("active");
        tabChatContent.classList.remove("active");
    });

    // Close SQL & Table Data Inspector Panel
    closeInspectorBtn.addEventListener("click", () => {
        dataInspectorPanel.classList.add("hidden");
    });

    // Copy SQL to Clipboard
    copySqlBtn.addEventListener("click", () => {
        const sqlText = generatedSqlCodeEl.textContent;
        navigator.clipboard.writeText(sqlText).then(() => {
            const originalHTML = copySqlBtn.innerHTML;
            copySqlBtn.innerHTML = `<i data-lucide="check" class="icon-xs"></i> Copied!`;
            lucide.createIcons();
            setTimeout(() => {
                copySqlBtn.innerHTML = originalHTML;
                lucide.createIcons();
            }, 2000);
        });
    });

    // Fetch and Populate Executive Dashboard
    async function loadDashboard() {
        try {
            refreshDashboardBtn.classList.add("spin-animation");
            const res = await fetch(API_DASHBOARD);
            if (!res.ok) throw new Error("Dashboard fetch failed");
            
            const data = await res.json();
            
            // Populate KPIs
            const kpis = data.kpis;
            kpiRevenueEl.textContent = "$" + kpis.total_revenue.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
            kpiUnitsEl.textContent = kpis.total_units_sold.toLocaleString("en-US");
            kpiPromoPctEl.textContent = kpis.promo_revenue_pct + "%";
            kpiTopProductEl.textContent = kpis.top_product;
            kpiTopRegionEl.textContent = kpis.top_region;
            kpiInventoryRiskEl.textContent = kpis.inventory_risk_count;

            // Render Charts
            renderTrendChart(data.charts.weekly_trend);
            renderRegionalChart(data.charts.regional_distribution);
            renderCategoryChart(data.charts.category_distribution);

        } catch (err) {
            console.error("Error loading dashboard data:", err);
        } finally {
            refreshDashboardBtn.classList.remove("spin-animation");
        }
    }

    // Chart 1: Render Revenue / Volume Weekly Trend
    function renderTrendChart(trendData) {
        const ctx = document.getElementById("weeklyTrendChart").getContext("2d");
        
        if (weeklyTrendChartInstance) {
            weeklyTrendChartInstance.destroy();
        }

        const labels = trendData.map(d => {
            // Convert 'YYYY-MM-DD' into readable label e.g., 'Jan 04'
            const parts = d.week_start_date.split("-");
            const dateObj = new Date(parts[0], parts[1] - 1, parts[2]);
            return dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric" });
        });
        const revenues = trendData.map(d => d.revenue);
        const volumes = trendData.map(d => d.units);

        weeklyTrendChartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [
                    {
                        label: "Weekly Revenue ($)",
                        data: revenues,
                        borderColor: "#00f2fe",
                        backgroundColor: "rgba(0, 242, 254, 0.05)",
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        yAxisID: "y-rev"
                    },
                    {
                        label: "Weekly Volume (Units)",
                        data: volumes,
                        borderColor: "#b176fc",
                        backgroundColor: "rgba(177, 118, 252, 0.0)",
                        borderWidth: 1.5,
                        borderDash: [5, 5],
                        tension: 0.4,
                        fill: false,
                        yAxisID: "y-vol"
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: "index",
                        intersect: false,
                        padding: 10,
                        backgroundColor: "rgba(10, 15, 30, 0.9)",
                        titleColor: "#f8fafc",
                        bodyColor: "#f8fafc",
                        borderColor: "rgba(255, 255, 255, 0.08)",
                        borderWidth: 1
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: "#64748b", font: { size: 9 } }
                    },
                    "y-rev": {
                        type: "linear",
                        position: "left",
                        grid: { color: "rgba(255, 255, 255, 0.03)" },
                        ticks: { 
                            color: "#64748b",
                            font: { size: 9 },
                            callback: value => "$" + value.toLocaleString()
                        }
                    },
                    "y-vol": {
                        type: "linear",
                        position: "right",
                        grid: { display: false },
                        ticks: {
                            color: "#64748b",
                            font: { size: 9 },
                            callback: value => value.toLocaleString()
                        }
                    }
                }
            }
        });
    }

    // Chart 2: Render Regional Sales Share
    function renderRegionalChart(regionalData) {
        const ctx = document.getElementById("regionalChart").getContext("2d");
        
        if (regionalChartInstance) {
            regionalChartInstance.destroy();
        }

        const labels = regionalData.map(d => d.region);
        const revenues = regionalData.map(d => d.revenue);

        regionalChartInstance = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: revenues,
                    backgroundColor: [
                        "#4facfe", // North
                        "#00f2fe", // South
                        "#10b981", // West
                        "#f59e0b"  // East
                    ],
                    borderWidth: 2,
                    borderColor: "#0c1224"
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: "#94a3b8",
                            boxWidth: 8,
                            padding: 10,
                            font: { size: 9, family: "Inter" }
                        }
                    },
                    tooltip: {
                        backgroundColor: "rgba(10, 15, 30, 0.9)",
                        titleColor: "#f8fafc",
                        bodyColor: "#f8fafc",
                        borderWidth: 1,
                        borderColor: "rgba(255, 255, 255, 0.08)",
                        callbacks: {
                            label: function(context) {
                                const label = context.label || "";
                                const val = context.raw || 0;
                                return ` ${label}: $${val.toLocaleString()}`;
                            }
                        }
                    }
                },
                cutout: "75%"
            }
        });
    }

    // Chart 3: Render Sales Category Distribution
    function renderCategoryChart(categoryData) {
        const ctx = document.getElementById("categoryChart").getContext("2d");
        
        if (categoryChartInstance) {
            categoryChartInstance.destroy();
        }

        const labels = categoryData.map(d => d.category);
        const revenues = categoryData.map(d => d.revenue);

        categoryChartInstance = new Chart(ctx, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Category Revenue",
                    data: revenues,
                    backgroundColor: "rgba(0, 242, 254, 0.65)",
                    hoverBackgroundColor: "#00f2fe",
                    borderRadius: 4,
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: "rgba(10, 15, 30, 0.9)",
                        titleColor: "#f8fafc",
                        bodyColor: "#f8fafc"
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: "#64748b", font: { size: 9 } }
                    },
                    y: {
                        grid: { color: "rgba(255, 255, 255, 0.03)" },
                        ticks: {
                            color: "#64748b",
                            font: { size: 9 },
                            callback: value => "$" + value.toLocaleString()
                        }
                    }
                }
            }
        });
    }

    // Fetch and Populate Smart Alerts
    async function loadAlerts() {
        try {
            const res = await fetch(API_ALERTS);
            if (!res.ok) throw new Error("Alerts fetch failed");
            
            const alerts = await res.json();
            
            // Update Tab Badge Count
            if (alerts.length > 0) {
                alertsCountBadge.textContent = alerts.length;
                alertsCountBadge.classList.remove("hidden");
            } else {
                alertsCountBadge.classList.add("hidden");
            }
            
            // Build alerts HTML list
            if (alerts.length === 0) {
                alertsListEl.innerHTML = `
                    <div class="alerts-placeholder">
                        <i data-lucide="shield-check" class="placeholder-icon text-slate-500"></i>
                        <p>No active critical warnings. System running normally.</p>
                    </div>
                `;
            } else {
                alertsListEl.innerHTML = alerts.map(alert => {
                    const sevClass = `severity-${alert.severity.toLowerCase()}`;
                    const badgeClass = `badge-${alert.severity.toLowerCase()}`;
                    
                    let iconName = "info";
                    if (alert.severity === "CRITICAL") iconName = "alert-triangle";
                    else if (alert.severity === "WARNING") iconName = "alert-circle";
                    
                    return `
                        <div class="alert-node ${sevClass}">
                            <i data-lucide="${iconName}" class="alert-icon icon-sm mt-05"></i>
                            <div class="alert-details">
                                <span class="alert-node-title">${alert.title}</span>
                                <span class="alert-node-desc">${alert.description}</span>
                                <div class="alert-node-footer">
                                    <span class="alert-node-time">${alert.timestamp}</span>
                                    <span class="alert-badge ${badgeClass}">${alert.severity}</span>
                                </div>
                            </div>
                        </div>
                    `;
                }).join("");
            }
            
            lucide.createIcons();

        } catch (err) {
            console.error("Error loading smart alerts:", err);
        }
    }

    // Chat Assistant: Submit Question Handler
    chatInputForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const questionText = chatInputField.value.trim();
        if (!questionText) return;

        submitQuestion(questionText);
    });

    // Handle template pill clicks
    templatePills.forEach(pill => {
        pill.addEventListener("click", () => {
            const q = pill.getAttribute("data-question");
            submitQuestion(q);
        });
    });

    // Central function to submit a question to the backend
    async function submitQuestion(question) {
        // Clear input field
        chatInputField.value = "";

        // 1. Add User bubble to chat history
        appendChatBubble("user", question);

        // 2. Add loading skeleton bubble for AI response
        const loadingId = "ai-loading-" + Date.now();
        appendLoadingBubble(loadingId);

        // Scroll chat container to bottom
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;

        try {
            const response = await fetch(API_QUERY, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question })
            });

            if (!response.ok) throw new Error("Failed to process query.");

            const data = await response.json();
            
            // Remove loading skeleton
            const loadingBubbleEl = document.getElementById(loadingId);
            if (loadingBubbleEl) loadingBubbleEl.remove();

            if (data.success) {
                // 3. Append AI response bubble (contains HTML content)
                appendChatBubble("system", data.insights);

                // 4. Update and display Data Inspector (SQL & Table Results)
                generatedSqlCodeEl.textContent = data.sql;
                renderResultsTable(data.results);
                
                // Show data inspector
                dataInspectorPanel.classList.remove("hidden");
            } else {
                appendChatBubble("system", `
                    <div class="insight-container">
                        <p class="text-neon-rose font-bold mb-2">Query Compilation Failed</p>
                        <p class="mb-4">I encountered an issue compiling the SQLite query or processing the results:</p>
                        <div class="sql-code-block mb-4">
                            <pre><code>${data.error || "Unknown SQLite Error"}</code></pre>
                        </div>
                        <p class="text-xs text-slate-400">Please try rephrasing your question or asking a different query.</p>
                    </div>
                `);
            }

        } catch (err) {
            console.error("Error submitting query:", err);
            const loadingBubbleEl = document.getElementById(loadingId);
            if (loadingBubbleEl) loadingBubbleEl.remove();
            
            appendChatBubble("system", `
                <div class="insight-container">
                    <p class="text-neon-rose font-semibold">Service Connection Error</p>
                    <p class="text-xs text-slate-400">Could not communicate with the backend server. Please verify that the server is running.</p>
                </div>
            `);
        }

        // Scroll chat container to bottom
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    }

    // Append standard message bubble
    function appendChatBubble(sender, content) {
        const bubble = document.createElement("div");
        bubble.className = `chat-bubble ${sender}`;

        const headerIcon = sender === "user" ? "user" : "sparkles";
        const senderName = sender === "user" ? "You" : "BevInsight Copilot";
        const iconColor = sender === "user" ? "" : "text-neon-teal";

        bubble.innerHTML = `
            <div class="bubble-header">
                <i data-lucide="${headerIcon}" class="${iconColor} icon-xs"></i>
                <span>${senderName}</span>
            </div>
            <div class="bubble-content">
                ${content}
            </div>
        `;
        chatMessagesContainer.appendChild(bubble);
        lucide.createIcons();
    }

    // Append loading skeleton
    function appendLoadingBubble(id) {
        const bubble = document.createElement("div");
        bubble.id = id;
        bubble.className = "chat-bubble system";
        bubble.innerHTML = `
            <div class="bubble-header">
                <i data-lucide="sparkles" class="text-neon-teal icon-xs"></i>
                <span>BevInsight Copilot is analyzing...</span>
            </div>
            <div class="bubble-content">
                <div class="loading-skeleton">
                    <div class="skeleton-line w-full"></div>
                    <div class="skeleton-line w-3-4"></div>
                    <div class="skeleton-line w-1-2"></div>
                </div>
            </div>
        `;
        chatMessagesContainer.appendChild(bubble);
        lucide.createIcons();
    }

    // Render Raw SQL Result Rows to Inspector Table
    function renderResultsTable(results) {
        if (!results || results.length === 0) {
            queryResultsTable.innerHTML = `
                <thead><tr><th>No Data</th></tr></thead>
                <tbody><tr><td>The query executed successfully but returned zero rows.</td></tr></tbody>
            `;
            return;
        }

        // Extract column names from first item keys
        const columns = Object.keys(results[0]);

        // Build header row
        const theadHTML = `
            <tr>
                ${columns.map(col => `<th>${col}</th>`).join("")}
            </tr>
        `;

        // Build table rows
        const tbodyHTML = results.map(row => {
            return `
                <tr>
                    ${columns.map(col => {
                        let cellVal = row[col];
                        if (cellVal === null || cellVal === undefined) return `<td><em class="text-muted">null</em></td>`;
                        if (typeof cellVal === "number" && col.toLowerCase().includes("revenue")) {
                            return `<td>$${cellVal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</td>`;
                        }
                        if (typeof cellVal === "number") {
                            return `<td>${cellVal.toLocaleString()}</td>`;
                        }
                        return `<td>${cellVal}</td>`;
                    }).join("")}
                </tr>
            `;
        }).join("");

        queryResultsTable.innerHTML = `
            <thead>${theadHTML}</thead>
            <tbody>${tbodyHTML}</tbody>
        `;
    }

    // Refresh dashboard data click handler
    refreshDashboardBtn.addEventListener("click", () => {
        loadDashboard();
        loadAlerts();
    });

    // Initial Load Sequence
    checkHealth();
    loadDashboard();
    loadAlerts();
});
