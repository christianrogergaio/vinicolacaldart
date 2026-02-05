document.addEventListener('DOMContentLoaded', async () => {
    console.log("History Page Loaded (New Design)");

    // Define weather/risk helpers
    // CSV Export
    window.exportTableToCSV = function () {
        const rows = document.querySelectorAll("table tr");
        let csv = [];
        for (const row of rows) {
            const cols = row.querySelectorAll("td, th");
            const rowData = [];
            for (const col of cols) rowData.push(col.innerText.replace(/(\r\n|\n|\r)/gm, " ").trim());
            csv.push(rowData.join(","));
        }
        const csvFile = new Blob([csv.join("\n")], { type: "text/csv" });
        const downloadLink = document.createElement("a");
        downloadLink.download = `relatorio_caldart_${new Date().toISOString().slice(0, 10)}.csv`;
        downloadLink.href = window.URL.createObjectURL(csvFile);
        downloadLink.style.display = "none";
        document.body.appendChild(downloadLink);
        downloadLink.click();
    };

    // Bind Export Button
    const btnExport = document.querySelector('button[onclick="window.print()"]');
    if (btnExport) {
        // Change onclick to export CSV (Print is still useful via Ctrl+P, but button says Export CSV now)
        btnExport.onclick = window.exportTableToCSV;
    }

    async function loadHistory() {
        try {
            // Using new Daily Report API
            const res = await fetch('/api/relatorios/diario?dias=30');
            const json = await res.json();
            const data = json.relatorio || [];

            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-text-secondary">Nenhum dado encontrado.</td></tr>';
                return;
            }

            tbody.innerHTML = '';

            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.className = "group hover:bg-slate-50/80 transition-colors border-b border-gray-50 last:border-0";

                // Risk Badge Logic
                let badgeClass = "bg-green-50 text-green-700 border-green-200";
                let badgeLabel = row.semaforo;

                if (row.semaforo === "VERMELHO") badgeClass = "bg-red-50 text-red-700 border-red-200";
                else if (row.semaforo === "AMARELO") badgeClass = "bg-amber-50 text-amber-700 border-amber-200";

                tr.innerHTML = `
                    <td class="px-5 py-4 font-mono text-text-secondary text-sm font-bold">${formatDate(row.data)}</td>
                    <td class="px-5 py-4">
                        <div class="flex items-center gap-3 text-sm">
                            <span class="text-blue-500 font-semibold">${row.t_min}°C</span>
                            <span class="text-gray-300">|</span>
                            <span class="text-red-500 font-semibold">${row.t_max}°C</span>
                        </div>
                    </td>
                    <td class="px-5 py-4 text-center">
                        <span class="inline-flex items-center px-2 py-1 rounded bg-blue-50 text-blue-700 text-xs font-bold gap-1">
                            <span class="material-symbols-outlined text-[14px]">water_drop</span>
                            ${row.molhamento_h}h
                        </span>
                    </td>
                    <td class="px-5 py-4">
                        <div class="w-full max-w-[100px]">
                            <div class="flex justify-between text-[10px] text-text-secondary mb-1">
                                <span>SEV</span>
                                <strong>${row.sev.toFixed(2)}</strong>
                            </div>
                            <div class="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                                <div class="bg-slate-400 h-1.5 rounded-full" style="width: ${Math.min((row.sev / 2.0) * 100, 100)}%"></div>
                            </div>
                        </div>
                    </td>
                    <td class="px-5 py-4">
                         <span class="px-2 py-1 rounded text-[10px] font-bold border ${badgeClass}">${badgeLabel}</span>
                         <div class="text-[10px] text-text-secondary mt-1 truncate max-w-[150px]" title="${row.risco_msg}">${row.risco_msg}</div>
                    </td>
                    <td class="px-5 py-4 text-right">
                        <button class="text-sage hover:text-green-700 text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity uppercase tracking-wide">
                            Ver Logs
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });

            if (footerCount) footerCount.innerText = `Mostrando ${data.length} dias`;

        } catch (e) {
            console.error("Error loading history:", e);
            tbody.innerHTML = '<tr><td colspan="6" class="px-5 py-8 text-center text-red-500">Erro ao carregar dados. Verifique a conexão.</td></tr>';
        }
    }

    // Formatting helper (Just Date)
    const formatDate = (dateStr) => {
        const parts = dateStr.split('-');
        if (parts.length === 3) return `${parts[2]}/${parts[1]}`;
        return dateStr;
    };
    // Initial Load
    loadHistory();

    // Refresh every 30s
    setInterval(loadHistory, 30000);
});
