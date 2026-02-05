document.addEventListener('DOMContentLoaded', function () {
    console.log("Dashboard Loaded");

    // Initialize Chart
    // Initialize Charts
    let tempChart = null;
    let umidChart = null;

    try {
        if (typeof Chart === 'undefined') throw new Error("Chart.js not loaded");

        // --- Temp Chart ---
        const ctxTemp = document.getElementById('tempChart').getContext('2d');
        tempChart = new Chart(ctxTemp, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Temperatura (°C)',
                    data: [],
                    borderColor: '#ED8936', // Amber/Orange
                    backgroundColor: 'rgba(237, 137, 54, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Temperatura (°C)' }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { unit: 'minute', displayFormats: { minute: 'HH:mm' } },
                        display: false // Hide X axis labels on top chart to reduce clutter
                    },
                    y: { type: 'linear', display: true, suggestedMin: 10, suggestedMax: 35 }
                }
            }
        });

        // --- Humidity Chart ---
        const ctxUmid = document.getElementById('umidChart').getContext('2d');
        umidChart = new Chart(ctxUmid, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Umidade (%)',
                    data: [],
                    borderColor: '#3182CE', // Blue
                    backgroundColor: 'rgba(49, 130, 206, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 2,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    title: { display: true, text: 'Umidade (%)' }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: { unit: 'minute', displayFormats: { minute: 'HH:mm' } },
                        title: { display: true, text: 'Horário' }
                    },
                    y: { type: 'linear', display: true, min: 0, max: 100 }
                }
            }
        });

    } catch (e) {
        console.error("Chart Init Error:", e);
    }

    // --- Date Logic ---
    function updateDate() {
        const dateElement = document.getElementById('header-date');
        if (dateElement) {
            const options = { weekday: 'long', day: 'numeric', month: 'long' };
            const today = new Date();
            // Capitalize first letter
            let dateString = today.toLocaleDateString('pt-BR', options);
            dateString = dateString.charAt(0).toUpperCase() + dateString.slice(1);
            dateElement.innerText = dateString;
        }
    }
    updateDate();

    // --- Helper: Risk Color ---
    function updateRiskColor(elementId, riskLevel) {
        const el = document.getElementById(elementId);
        if (!el) return;

        // Remove old classes
        el.classList.remove('text-sage', 'text-amber', 'text-coral', 'text-slate-300', 'text-text-primary');

        const upperRisk = (riskLevel || '').toUpperCase();
        if (upperRisk.includes('BAIXO')) {
            el.classList.add('text-sage');
        } else if (upperRisk.includes('MÉDIO') || upperRisk.includes('MEDIO') || upperRisk.includes('MODERADO')) {
            el.classList.add('text-amber');
        } else if (upperRisk.includes('ALTO') || upperRisk.includes('CRÍTICO') || upperRisk.includes('CRITICO')) {
            el.classList.add('text-coral');
        } else {
            el.classList.add('text-text-primary'); // Default
        }
    }



    // Function to fetch data
    async function fetchData() {
        try {
            const response = await fetch('/api/historico');
            const data = await response.json();

            if (!data || data.length === 0) return;

            // Update Arrays for Chart
            const labels = [];
            const temps = [];
            const umids = [];

            // Sort data by time if needed (usually DB returns sorted)
            data.forEach(reading => {
                // Fix Date Format (Space -> T) for Safari/Cross-Browser compatibility
                let dateStr = reading.data_hora;
                if (dateStr && typeof dateStr === 'string' && dateStr.indexOf('T') === -1) {
                    dateStr = dateStr.replace(' ', 'T');
                }
                const date = new Date(dateStr);

                labels.push(date);
                temps.push(reading.temperatura);
                umids.push(reading.umidade);
            });

            // Update Chart
            // Update Charts
            if (tempChart) {
                tempChart.data.labels = labels;
                tempChart.data.datasets[0].data = temps;
                tempChart.update();
            }
            if (umidChart) {
                umidChart.data.labels = labels;
                umidChart.data.datasets[0].data = umids;
                umidChart.update();
            }

            // Update Current Values (Last Reading)
            const last = data[data.length - 1];
            if (last) {
                document.getElementById('val-temp').innerText = last.temperatura.toFixed(1);
                document.getElementById('val-umid').innerText = last.umidade.toFixed(1);

                let lastDateStr = last.data_hora;
                if (lastDateStr && typeof lastDateStr === 'string' && lastDateStr.indexOf('T') === -1) {
                    lastDateStr = lastDateStr.replace(' ', 'T');
                }
                document.getElementById('last-update').innerText = 'Última atualização: ' + new Date(lastDateStr).toLocaleTimeString();

                // Improved Client-Side Risk Calculation (Míldio Focus)
                // Temp 18-25 is critical window.
                let risk = "BAIXO";
                const t = last.temperatura;
                const h = last.umidade;

                if (t >= 18 && t <= 26) {
                    if (h >= 85) risk = "ALTO";
                    else if (h >= 75) risk = "MÉDIO"; // Pays attention to 75-84 range
                }
                // Fallback for extreme humidity outside temp range
                else if (h >= 90) {
                    risk = "MÉDIO";
                }

                const riskEl = document.getElementById('val-risco');
                if (riskEl) {
                    riskEl.innerText = risk;
                    updateRiskColor('val-risco', risk);
                }
            }

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    // --- Dropdown Management & Configuration ---
    let configData = null;

    async function loadConfig() {
        try {
            const res = await fetch('/api/config');
            configData = await res.json();

            // Populate Plants
            const selPlanta = document.getElementById('sel-planta');
            if (selPlanta) {
                selPlanta.innerHTML = '';
                configData.plantas.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p;
                    opt.innerText = p;
                    selPlanta.appendChild(opt);
                });
                // Trigger change to populate dependent dropdowns
                selPlanta.addEventListener('change', updateDropdowns);
                updateDropdowns(); // Initial call
            }

            // Populate Diseases (Initial)
            const selDoenca = document.getElementById('sel-doenca');
            if (selDoenca) {
                selDoenca.innerHTML = '';
                configData.doencas.forEach(d => {
                    const opt = document.createElement('option');
                    opt.value = d;
                    opt.innerText = d;
                    selDoenca.appendChild(opt);
                });
            }

        } catch (e) {
            console.error("Error loading config:", e);
        }
    }

    function updateDropdowns() {
        if (!configData) return;

        const selPlanta = document.getElementById('sel-planta');
        const selEstadio = document.getElementById('sel-estadio');

        if (!selPlanta || !selEstadio) return;

        const planta = selPlanta.value;
        const estadios = configData.estadios_por_planta[planta] || [];

        selEstadio.innerHTML = '';
        estadios.forEach(e => {
            const opt = document.createElement('option');
            opt.value = e;
            opt.innerText = e;
            selEstadio.appendChild(opt);
        });
    }

    // Initialize
    loadConfig();
    fetchData();
    fetchPrediction(); // New call
    setInterval(fetchData, 5000); // Poll every 5 seconds

    // --- Weather Prediction ---
    // --- Weather Prediction ---
    async function fetchPrediction() {
        try {
            const resp = await fetch('/api/previsao');
            const data = await resp.json();

            if (data.semaforo) {
                // UI Elements
                const elTitle = document.getElementById('risk-title');
                const elMsg = document.getElementById('risk-msg');
                const elBadge = document.getElementById('risk-badge');
                const elGlow = document.getElementById('risk-glow');
                const elIcon = document.getElementById('risk-icon');

                const elSevVal = document.getElementById('sev-val');
                const elSevBar = document.getElementById('sev-bar');

                const elIncVal = document.getElementById('inc-val');
                const elIncBar = document.getElementById('inc-bar');

                // 1. Semantic Traffic Light
                if (data.semaforo === "VERDE") {
                    updateRiskUI("Sem Risco", "safe_check", "bg-sage", "text-sage", "bg-sage-light");
                    elMsg.innerText = data.mensagem || "Prognóstico Negativo: Economize aplicação.";
                } else if (data.semaforo === "AMARELO") {
                    updateRiskUI("Alerta", "warning", "bg-amber", "text-amber", "bg-amber/20");
                    elMsg.innerText = data.mensagem || "Alerta: Esporos ativos. Monitore chuva.";
                } else {
                    updateRiskUI("INFECÇÃO", "gpp_bad", "bg-coral", "text-coral", "bg-coral/20");
                    elMsg.innerText = data.mensagem || "Risco Alto: Infecção confirmada.";
                }

                function updateRiskUI(title, icon, bgColor, textColor, glowColor) {
                    elTitle.innerText = title;
                    elTitle.className = `text-2xl font-black text-center mb-1 ${textColor} transition-colors`;

                    elBadge.innerText = data.semaforo;
                    elBadge.className = `text-[10px] font-bold text-white ${bgColor} px-2 py-1 rounded-md transition-colors`;

                    elIcon.innerText = icon;
                    if (elGlow) elGlow.className = `absolute top-0 right-0 w-32 h-32 rounded-full blur-[40px] pointer-events-none transition-colors duration-500 ${glowColor}`;
                }

                // 2. Severity Bar (0 to 10 scale)
                const sev = data.sev || 0;
                elSevVal.innerText = sev.toFixed(2);
                let sevPct = Math.min((sev / 2.0) * 100, 100); // Scale: 2.0 SEV = 100% (High Severity)
                if (elSevBar) elSevBar.style.width = `${sevPct}%`;

                // 3. Incubation Bar (0 to 100%)
                const inc = data.incubacao_percent || 0;
                elIncVal.innerText = `${inc.toFixed(1)}%`;
                if (elIncBar) elIncBar.style.width = `${inc}%`;
            }

            // Legacy/Prediction Card Update (if exists)
            const elTrend = document.getElementById('val-risco-futuro');
            if (elTrend && data.gdd_previsto) {
                elTrend.innerText = `${data.gdd_previsto.toFixed(1)} GDD`;
                const ctx = document.querySelector('#card-previsao p.text-gray-500');
                if (ctx) ctx.innerText = data.detalhes_clima || "";
            }

        } catch (e) {
            console.error("Prediction Fetch Error:", e);
        }
    }
    // --- Relatório de Sinais Visuais ---
    function openReportModal() {
        document.getElementById('reportModal').classList.remove('hidden');
        document.getElementById('reportModal').style.display = 'flex';
    }

    function closeReportModal() {
        document.getElementById('reportModal').classList.add('hidden');
        document.getElementById('reportModal').style.display = 'none';
    }

    async function submitReport(sinal) {
        const obs = document.getElementById('reportObs').value;

        try {
            const response = await fetch('/api/report', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sinal: sinal,
                    severidade: sinal === 'Sem Sinais' ? 'nenhuma' : 'media',
                    observacoes: obs
                })
            });

            if (response.ok) {
                alert("Obrigado! Sua observação foi registrada.");
                closeReportModal();
            } else {
                alert("Erro ao salvar observação.");
            }
        } catch (error) {
            console.error("Erro no envio:", error);
            alert("Erro de conexão.");
        }
    }

    // Ensure modal is hidden on load
    document.addEventListener('DOMContentLoaded', () => {
        const modal = document.getElementById('reportModal');
        if (modal) {
            modal.classList.add('hidden');
            modal.style.display = 'none';
        }
    });
});
