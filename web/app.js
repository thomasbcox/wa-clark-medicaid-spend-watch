const API_BASE = "/api";

async function init() {
    await loadStats();
    await loadFlaggedProviders();
}

async function loadStats() {
    try {
        const res = await fetch(`${API_BASE}/summary`);
        const data = await res.json();
        document.getElementById('total-spend').textContent = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(data.total_spend);
        document.getElementById('total-providers').textContent = data.total_providers.toLocaleString();
        document.getElementById('total-flags').textContent = data.total_flags.toLocaleString();
    } catch (err) {
        console.error("Failed to load stats", err);
    }
}

async function loadFlaggedProviders() {
    const list = document.getElementById('provider-list');
    try {
        const res = await fetch(`${API_BASE}/flagged-providers`);
        const providers = await res.json();

        list.innerHTML = providers.map(p => `
            <div class="p-4 hover:bg-indigo-50 cursor-pointer transition-colors group" onclick="showProvider('${p.npi}')">
                <div class="flex justify-between items-start mb-1">
                    <div class="font-bold text-slate-800 line-clamp-1">${p.name || 'Unknown Provider'}</div>
                    <div class="bg-rose-100 text-rose-700 text-[10px] font-bold px-2 py-0.5 rounded-full">${p.flag_count}🚩</div>
                </div>
                <div class="text-xs text-slate-500 mb-2 truncate">${p.taxonomy_desc || 'No Specialty'}</div>
                <div class="flex justify-between items-center">
                    <span class="text-[10px] text-slate-400 font-mono">NPI: ${p.npi}</span>
                    <span class="text-xs font-semibold text-slate-700">${new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(p.total_spend)}</span>
                </div>
            </div>
        `).join('');
    } catch (err) {
        list.innerHTML = `<div class="p-4 text-rose-500">Error loading providers</div>`;
    }
}

async function showProvider(npi) {
    const detail = document.getElementById('detail-view');
    detail.innerHTML = `<div class="p-8 text-center">Loading details...</div>`;

    try {
        const res = await fetch(`${API_BASE}/provider/${npi}`);
        const data = await res.json();
        const p = data.details;

        detail.innerHTML = `
            <div class="w-full">
                <div class="flex justify-between items-start mb-8">
                    <div>
                        <h2 class="text-3xl font-bold text-slate-800 mb-1">${p.name || 'Unknown Provider'}</h2>
                        <div class="flex gap-4 text-sm text-slate-500">
                            <span>📍 ${p.city}, ${p.state}</span>
                            <span>🏷️ ${p.taxonomy_desc || 'N/A'}</span>
                            <span>🆔 NPI: ${p.npi}</span>
                        </div>
                    </div>
                    <div class="text-right">
                        <div class="text-xs font-semibold uppercase text-slate-400 mb-1">Exclusion Status</div>
                        ${p.is_excluded ?
                '<span class="bg-rose-600 text-white px-3 py-1 rounded-lg font-bold">EXCLUDED (OIG LEIE)</span>' :
                '<span class="bg-emerald-100 text-emerald-700 px-3 py-1 rounded-lg font-bold uppercase tracking-tight">No Exclusions Found</span>'
            }
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <div class="bg-slate-50 p-6 rounded-xl border border-slate-200">
                        <h3 class="font-bold text-slate-800 mb-4 flex items-center">Detected Risk Signals</h3>
                        <div class="space-y-4">
                            ${data.flags.map(f => `
                                <div class="bg-white p-3 rounded-lg border-l-4 border-rose-500 shadow-sm">
                                    <div class="text-[10px] font-bold text-rose-600 uppercase mb-1">${f.flag_type.replace(/_/g, ' ')}</div>
                                    <div class="text-sm text-slate-700">${f.reason}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <div class="bg-slate-50 p-6 rounded-xl border border-slate-200">
                        <h3 class="font-bold text-slate-800 mb-4">Spend Background</h3>
                        <p class="text-sm text-slate-600 mb-4">Total recorded Medicaid spend for this organization within the monitor period.</p>
                        <div class="text-4xl font-bold text-slate-800">
                            ${new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(
                data.spend_trend.reduce((sum, t) => sum + t.spend, 0)
            )}
                        </div>
                        <div class="text-xs text-slate-400 mt-2">Analyzed periods: ${data.spend_trend.length} months</div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                    <div class="bg-indigo-50 p-6 rounded-xl border border-indigo-100">
                        <h3 class="font-bold text-indigo-900 mb-4 flex items-center">🏢 Corporate Leadership & Official</h3>
                        ${p.auth_official_name ? `
                            <div class="space-y-3">
                                <div>
                                    <div class="text-[10px] font-bold text-indigo-400 uppercase">Authorized Official</div>
                                    <div class="text-indigo-900 font-semibold">${p.auth_official_name}</div>
                                    <div class="text-xs text-indigo-600">${p.auth_official_title || 'Title Unknown'}</div>
                                </div>
                                ${p.auth_official_phone ? `
                                <div>
                                    <div class="text-[10px] font-bold text-indigo-400 uppercase">Contact</div>
                                    <div class="text-xs text-indigo-900">${p.auth_official_phone}</div>
                                </div>` : ''}
                                ${p.mailing_address ? `
                                <div>
                                    <div class="text-[10px] font-bold text-indigo-400 uppercase">Business Mailing Address</div>
                                    <div class="text-xs text-indigo-900">${p.mailing_address}<br>${p.mailing_city}, ${p.mailing_state} ${p.mailing_zip}</div>
                                </div>` : ''}
                            </div>
                        ` : '<p class="text-sm text-indigo-400 italic">No official details found in registry.</p>'}
                    </div>

                    <div class="bg-slate-50 p-6 rounded-xl border border-slate-200">
                        <h3 class="font-bold text-slate-800 mb-4 flex items-center">🔗 Research Links</h3>
                        <div class="space-y-2">
                             <a href="https://ccfs.sos.wa.gov/#/search" target="_blank" class="block w-full text-center py-2 bg-white border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50 transition-colors">
                                📋 WA SOS Business Search
                            </a>
                            <a href="https://npiregistry.cms.hhs.gov/registry-search-results?number=${p.npi}" target="_blank" class="block w-full text-center py-2 bg-white border border-slate-300 rounded-lg text-sm text-slate-700 hover:bg-slate-50 transition-colors">
                                🏛 Full NPPES Record
                            </a>
                        </div>
                    </div>
                </div>

                <div class="bg-slate-50 p-6 rounded-xl border border-slate-200">
                    <h3 class="font-bold text-slate-800 mb-2">Ethics & Stewardship Note</h3>
                    <p class="text-xs text-slate-500 italic leading-relaxed">
                        These flags represent statistical deviations from peer benchmarks (Specialty x HCPCS Code). They are hypotheses for professional investigation, not definitive declarations of wrongdoing. For civic groups: use these findings to request clarification or specific oversight from state agencies.
                    </p>
                </div>
            </div>
        `;
    } catch (err) {
        detail.innerHTML = `<div class="p-8 text-rose-500">Error loading details for ${npi}</div>`;
    }
}

document.addEventListener('DOMContentLoaded', init);
