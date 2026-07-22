document.addEventListener("DOMContentLoaded", () => {
    // Navigation Setup
    const navItems = document.querySelectorAll(".nav-item");
    const sections = document.querySelectorAll(".dashboard-section");

    navItems.forEach(item => {
        item.addEventListener("click", (e) => {
            e.preventDefault();
            const targetId = item.getAttribute("href").substring(1);
            
            navItems.forEach(nav => nav.classList.remove("active"));
            sections.forEach(sec => sec.classList.remove("active-section"));
            
            item.classList.add("active");
            document.getElementById(targetId).classList.add("active-section");
        });
    });

    // Preset configurations for simulator
    const presets = {
        normal: {
            amount: 350,
            hour_of_day: 12,
            time_since_last_txn_min: 480,
            payment_app: "Paytm",
            transaction_type: "P2P",
            user_avg_txn_value: 500,
            user_avg_monthly_txn: 25,
            user_loyalty_score: 0.8,
            device_type: "Android",
            user_kyc_status: "Verified",
            is_risk_user: "0",
            new_device_flag: "0",
            ip_location_mismatch: "0",
            failed_attempts_last_24h: 0,
            transaction_velocity: 1,
            amount_deviation_score: 0.1
        },
        speed_hack: {
            amount: 4200,
            hour_of_day: 3,
            time_since_last_txn_min: 5,
            payment_app: "PhonePe",
            transaction_type: "P2P",
            user_avg_txn_value: 300,
            user_avg_monthly_txn: 12,
            user_loyalty_score: 0.35,
            device_type: "iOS",
            user_kyc_status: "Verified",
            is_risk_user: "0",
            new_device_flag: "1",
            ip_location_mismatch: "1",
            failed_attempts_last_24h: 0,
            transaction_velocity: 3,
            amount_deviation_score: 4.5
        },
        pin_guess: {
            amount: 15000,
            hour_of_day: 21,
            time_since_last_txn_min: 1440,
            payment_app: "GPay",
            transaction_type: "Subscription",
            user_avg_txn_value: 1000,
            user_avg_monthly_txn: 40,
            user_loyalty_score: 0.9,
            device_type: "Android",
            user_kyc_status: "Verified",
            is_risk_user: "1",
            new_device_flag: "0",
            ip_location_mismatch: "0",
            failed_attempts_last_24h: 4,
            transaction_velocity: 1,
            amount_deviation_score: 5.2
        },
        night_drain: {
            amount: 85000,
            hour_of_day: 2,
            time_since_last_txn_min: 60,
            payment_app: "BHIM",
            transaction_type: "P2M",
            user_avg_txn_value: 400,
            user_avg_monthly_txn: 15,
            user_loyalty_score: 0.2,
            device_type: "Android",
            user_kyc_status: "Not Verified",
            is_risk_user: "1",
            new_device_flag: "1",
            ip_location_mismatch: "1",
            failed_attempts_last_24h: 2,
            transaction_velocity: 2,
            amount_deviation_score: 9.5
        }
    };

    const presetButtons = document.querySelectorAll(".preset-btn");
    presetButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            presetButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            
            const presetName = btn.dataset.preset;
            const config = presets[presetName];
            
            if (config) {
                // Populate form fields
                Object.keys(config).forEach(key => {
                    const el = document.getElementById(key);
                    if (el) el.value = config[key];
                });
                showToast(`Loaded ${btn.textContent.trim()} Scenario`);
            }
        });
    });

    // Form submission & Analysis
    const simForm = document.getElementById("simulator-form");
    simForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        
        // Gather input data
        const inputData = {
            amount: parseFloat(document.getElementById("amount").value),
            hour_of_day: parseInt(document.getElementById("hour_of_day").value),
            is_weekend: parseInt(document.getElementById("is_weekend").value),
            is_night_transaction: parseInt(document.getElementById("hour_of_day").value) < 6 || parseInt(document.getElementById("hour_of_day").value) >= 22 ? 1 : 0,
            time_since_last_txn_min: parseFloat(document.getElementById("time_since_last_txn_min").value),
            user_avg_monthly_txn: parseInt(document.getElementById("user_avg_monthly_txn").value),
            user_avg_txn_value: parseFloat(document.getElementById("user_avg_txn_value").value),
            user_loyalty_score: parseFloat(document.getElementById("user_loyalty_score").value),
            new_device_flag: parseInt(document.getElementById("new_device_flag").value),
            ip_location_mismatch: parseInt(document.getElementById("ip_location_mismatch").value),
            failed_attempts_last_24h: parseInt(document.getElementById("failed_attempts_last_24h").value),
            transaction_velocity: parseInt(document.getElementById("transaction_velocity").value),
            amount_deviation_score: parseFloat(document.getElementById("amount_deviation_score").value),
            recurring_payment_flag: parseInt(document.getElementById("recurring_payment_flag").value),
            balance_after_transaction: parseFloat(document.getElementById("balance_after_transaction").value),
            transaction_frequency_score: parseFloat(document.getElementById("transaction_frequency_score").value),
            account_age_days: parseInt(document.getElementById("account_age_days").value),
            linked_bank_count: parseInt(document.getElementById("linked_bank_count").value),
            is_risk_user: parseInt(document.getElementById("is_risk_user").value),
            avg_daily_transactions: parseFloat(document.getElementById("avg_daily_transactions").value),
            is_registered: parseInt(document.getElementById("is_registered").value),
            rating: parseFloat(document.getElementById("rating").value),
            receiver_type: document.getElementById("receiver_type").value,
            transaction_type: document.getElementById("transaction_type").value,
            payment_app: document.getElementById("payment_app").value,
            device_type: document.getElementById("device_type").value,
            user_city_tier: document.getElementById("user_city_tier").value,
            user_kyc_status: document.getElementById("user_kyc_status").value,
            age_group: document.getElementById("age_group").value,
            city: document.getElementById("city").value,
            merchant_category: document.getElementById("merchant_category").value,
            merchant_size: document.getElementById("merchant_size").value
        };

        // If P2M, map some defaults
        if (inputData.transaction_type === "P2M") {
            inputData.receiver_type = "Merchant";
            inputData.merchant_category = "Shopping";
            inputData.merchant_size = "Medium";
            inputData.avg_daily_transactions = 150.0;
            inputData.is_registered = 1;
            inputData.rating = 4.2;
        } else {
            inputData.receiver_type = "User";
            inputData.merchant_category = "P2P_Transfer";
            inputData.merchant_size = "None";
            inputData.avg_daily_transactions = 0.0;
            inputData.is_registered = 0;
            inputData.rating = 0.0;
        }

        try {
            showToast("Analyzing UPI transaction...", "info");
            
            // Post payload to FastAPI endpoint
            const response = await fetch("/api/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(inputData)
            });

            if (!response.ok) {
                const errDetail = await response.json();
                throw new Error(errDetail.detail || "Server error occurred");
            }

            const data = await response.json();
            updateSimulatorUI(data);
            showToast("Analysis Complete", "success");
        } catch (error) {
            console.error(error);
            showToast(error.message, "error");
        }
    });

    // Update Simulator Results UI
    function updateSimulatorUI(data) {
        const scorePct = Math.round(data.risk_score * 100);
        
        // 1. Update circular gauge variables
        const gaugeFill = document.getElementById("risk-gauge-fill");
        const gaugeCover = document.getElementById("risk-gauge-fill").parentNode;
        const resultCard = document.getElementById("risk-result-card");
        
        // Define color based on risk score
        let riskColor = "var(--color-safe)";
        let verdict = "LEGITIMATE";
        let verdictDesc = "The transaction aligns with typical user spending profiles and normal device behavioral telemetry.";
        
        if (data.risk_score >= 0.65) {
            riskColor = "var(--color-danger)";
            verdict = "FRAUD DETECTED";
            verdictDesc = "High fraud indicators triggered across deep learning sequence structures and baseline anomaly classifiers.";
            resultCard.classList.add("pulse-red-shadow");
        } else if (data.risk_score >= 0.35) {
            riskColor = "var(--color-warning)";
            verdict = "HIGH RISK / SUSPICIOUS";
            verdictDesc = "Moderate risk signals detected. Unusual transaction parameters require supplementary user authentication.";
            resultCard.classList.remove("pulse-red-shadow");
        } else {
            resultCard.classList.remove("pulse-red-shadow");
        }
        
        gaugeCover.style.setProperty("--risk-value", scorePct);
        gaugeCover.style.setProperty("--risk-color", riskColor);
        document.getElementById("risk-percent-text").textContent = `${scorePct}%`;
        document.getElementById("risk-percent-text").style.color = riskColor;
        
        // Verdict text
        document.getElementById("verdict-title").textContent = verdict;
        document.getElementById("verdict-title").style.color = riskColor;
        document.getElementById("verdict-desc").textContent = verdictDesc;
        
        // 2. Risk Signals
        const signalsCard = document.getElementById("risk-signals-card");
        const signalsIcon = document.getElementById("signals-icon");
        const signalsList = document.getElementById("signals-list");
        
        signalsCard.classList.remove("disabled");
        signalsList.innerHTML = "";
        
        if (data.risk_signals.length > 0) {
            signalsIcon.className = "fa-solid fa-bell text-danger";
            signalsIcon.style.color = "var(--color-danger)";
            
            data.risk_signals.forEach(sig => {
                const li = document.createElement("li");
                li.className = "warning-signal";
                li.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${sig}`;
                signalsList.appendChild(li);
            });
        } else {
            signalsIcon.className = "fa-solid fa-circle-check text-success";
            signalsIcon.style.color = "var(--color-safe)";
            
            const li = document.createElement("li");
            li.className = "safe-signal";
            li.innerHTML = `<i class="fa-solid fa-circle-check"></i> Standard behavior - No risk signals triggered`;
            signalsList.appendChild(li);
        }
        
        // 3. Multi-Model Breakdown
        const modelPredictions = data.model_predictions;
        const keysMapping = {
            "Random Forest": "res-rf",
            "1D CNN": "res-cnn",
            "Autoencoder": "res-ae",
            "K-Means": "res-kmeans",
            "Local Outlier Factor": "res-lof"
        };
        
        Object.keys(keysMapping).forEach(modelName => {
            const elementId = keysMapping[modelName];
            const el = document.getElementById(elementId);
            const mData = modelPredictions[modelName];
            
            if (el && mData) {
                const isFraud = mData.is_fraud === 1;
                const score = mData.score;
                
                el.innerHTML = isFraud 
                    ? `<span class="badge badge-danger"><i class="fa-solid fa-shield-virus"></i> Suspicious (${Math.round(score*100)}%)</span>` 
                    : `<span class="badge badge-safe"><i class="fa-solid fa-circle-check"></i> Legitimate (${Math.round(score*100)}%)</span>`;
            } else if (el) {
                el.innerHTML = `<span class="badge badge-gray">Not Loaded</span>`;
            }
        });
    }

    // Retrain button click
    const btnRetrain = document.getElementById("btn-re-train");
    btnRetrain.addEventListener("click", async () => {
        try {
            btnRetrain.disabled = true;
            btnRetrain.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Training Models...`;
            showToast("Retraining ML models on Kaggle dataset. This takes up to 30-40 seconds...", "info");
            
            const response = await fetch("/api/train", { method: "POST" });
            if (!response.ok) {
                throw new Error("Failed to train models on the backend");
            }
            
            const data = await response.json();
            showToast("All models retrained and metrics updated successfully!", "success");
            
            // Reload statistics and charts
            loadDashboardData();
        } catch (error) {
            console.error(error);
            showToast(error.message, "error");
        } finally {
            btnRetrain.disabled = false;
            btnRetrain.innerHTML = `<i class="fa-solid fa-rotate"></i> Retrain Models`;
        }
    });

    // Charts references
    let chartFraudRatio = null;
    let chartAmountDist = null;
    let chartHourlyTrend = null;
    let chartModelsF1 = null;

    // Toast alerts helper
    function showToast(message, type = "info") {
        const toast = document.getElementById("toast");
        if (!toast) return;
        const toastMsg = document.getElementById("toast-message");
        const toastIcon = toast.querySelector(".toast-icon");
        
        if (toastMsg) toastMsg.textContent = message;
        
        // Style by type
        toast.className = "toast show";
        if (type === "success") {
            toast.style.borderLeftColor = "var(--color-safe)";
            if (toastIcon) {
                toastIcon.className = "fa-solid fa-circle-check";
                toastIcon.style.color = "var(--color-safe)";
            }
        } else if (type === "error") {
            toast.style.borderLeftColor = "var(--color-danger)";
            if (toastIcon) {
                toastIcon.className = "fa-solid fa-circle-exclamation";
                toastIcon.style.color = "var(--color-danger)";
            }
        } else {
            toast.style.borderLeftColor = "var(--color-primary)";
            if (toastIcon) {
                toastIcon.className = "fa-solid fa-circle-info";
                toastIcon.style.color = "var(--color-primary)";
            }
        }
        
        setTimeout(() => {
            toast.classList.remove("show");
        }, 4000);
    }


    // Load API Stats & Charts
    async function loadDashboardData() {
        try {
            // 1. Fetch Stats
            const statsRes = await fetch("/api/stats");
            if (!statsRes.ok) throw new Error("Could not fetch KPI metrics");
            const stats = await statsRes.ok ? await statsRes.json() : null;
            
            if (stats) {
                document.getElementById("stat-total-txns").textContent = stats.total_transactions.toLocaleString();
                document.getElementById("stat-success-rate").textContent = `${stats.success_rate}%`;
                document.getElementById("stat-fraud-rate").textContent = `${stats.fraud_rate}%`;
                document.getElementById("stat-avg-amount").textContent = `₹${stats.avg_transaction_amount.toFixed(2)}`;
            }

            // 2. Fetch Charts Data
            const chartsRes = await fetch("/api/charts");
            if (!chartsRes.ok) throw new Error("Could not fetch chart distributions");
            const chartsData = await chartsRes.json();
            
            renderCharts(chartsData);
            renderPerformanceTable(chartsData.metrics);
        } catch (error) {
            console.error(error);
            showToast("Server files or model weights not ready. Run the training script first.", "error");
        }
    }

    // Render Chart.js items
    function renderCharts(data) {
        // Options common configuration
        const commonOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: "#cbd5e0" }
                }
            },
            scales: {
                x: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#a0aec0" } },
                y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#a0aec0" } }
            }
        };

        // 1. Fraud Ratio (Doughnut)
        if (chartFraudRatio) chartFraudRatio.destroy();
        const ctxFraud = document.getElementById("chart-fraud-ratio").getContext("2d");
        chartFraudRatio = new Chart(ctxFraud, {
            type: 'doughnut',
            data: {
                labels: data.fraud_vs_safe.labels,
                datasets: [{
                    data: data.fraud_vs_safe.data,
                    backgroundColor: ['rgba(0, 230, 118, 0.85)', 'rgba(255, 0, 85, 0.85)'],
                    borderColor: ['#141622', '#141622'],
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { color: '#cbd5e0' } }
                }
            }
        });

        // 2. Amount Distribution (Bar)
        if (chartAmountDist) chartAmountDist.destroy();
        const ctxAmt = document.getElementById("chart-amount-dist").getContext("2d");
        chartAmountDist = new Chart(ctxAmt, {
            type: 'bar',
            data: {
                labels: data.amount_distribution.labels,
                datasets: [{
                    label: 'Transaction Count',
                    data: data.amount_distribution.data,
                    backgroundColor: 'rgba(0, 242, 254, 0.7)',
                    borderColor: 'var(--color-primary)',
                    borderWidth: 1
                }]
            },
            options: commonOptions
        });

        // 3. Hourly trends (Line)
        if (chartHourlyTrend) chartHourlyTrend.destroy();
        const ctxHour = document.getElementById("chart-hourly-trend").getContext("2d");
        chartHourlyTrend = new Chart(ctxHour, {
            type: 'line',
            data: {
                labels: data.hourly_distribution.labels,
                datasets: [{
                    label: 'Transactions volume',
                    data: data.hourly_distribution.data,
                    backgroundColor: 'rgba(127, 0, 255, 0.2)',
                    borderColor: '#a78bfa',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: commonOptions
        });

        // 4. Model Comparison (Horizontal Bar Chart)
        if (chartModelsF1) chartModelsF1.destroy();
        const ctxF1 = document.getElementById("chart-models-f1").getContext("2d");
        
        const modelNames = Object.keys(data.metrics || {});
        const f1Scores = modelNames.map(name => data.metrics[name].f1_score);
        const accuracyScores = modelNames.map(name => data.metrics[name].accuracy);
        
        chartModelsF1 = new Chart(ctxF1, {
            type: 'bar',
            data: {
                labels: modelNames,
                datasets: [
                    {
                        label: 'F1-Score',
                        data: f1Scores,
                        backgroundColor: 'rgba(255, 0, 85, 0.8)',
                    },
                    {
                        label: 'Accuracy',
                        data: accuracyScores,
                        backgroundColor: 'rgba(0, 242, 254, 0.8)',
                    }
                ]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { labels: { color: "#cbd5e0" } }
                },
                scales: {
                    x: { min: 0.0, max: 1.0, grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#a0aec0" } },
                    y: { grid: { color: "rgba(255, 255, 255, 0.05)" }, ticks: { color: "#a0aec0" } }
                }
            }
        });
    }

    // Render Metrics Table
    function renderPerformanceTable(metrics) {
        const tbody = document.querySelector("#perf-table tbody");
        tbody.innerHTML = "";
        
        if (!metrics || Object.keys(metrics).length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">No model metrics loaded. Run retraining.</td></tr>`;
            return;
        }
        
        Object.keys(metrics).forEach(modelName => {
            const m = metrics[modelName];
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${modelName}</td>
                <td>${(m.accuracy * 100).toFixed(2)}%</td>
                <td>${(m.precision * 100).toFixed(2)}%</td>
                <td>${(m.recall * 100).toFixed(2)}%</td>
                <td>${(m.f1_score).toFixed(4)}</td>
                <td>${(m.auc).toFixed(4)}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    // Initial Load
    loadDashboardData();
});
