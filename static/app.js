let itemCount = 1;

function escapeHtml(text) {
    const value = String(text ?? "");
    return value
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function fmtQty(value) {
    if (value === null || value === undefined || Number.isNaN(Number(value))) return "-";
    return Number(value).toLocaleString("es-ES", { maximumFractionDigits: 2 });
}

function formatDate(value) {
    if (!value) return "-";
    const raw = String(value).trim();
    const match = raw.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})(?::\d{2}(?:\.\d+)?)?(?:Z|[+\-]\d{2}:\d{2})?$/);
    if (match) {
        const [, yyyy, mm, dd, hh, mi] = match;
        return `${dd}/${mm}/${yyyy} ${hh}:${mi}`;
    }
    return escapeHtml(raw);
}

function renderItemOptions() {
    const catalogo = window.CATALOGO_ITEMS || [];
    const options = ['<option value="">Seleccionar item...</option>'];
    for (const item of catalogo) {
        const safeItem = escapeHtml(item);
        options.push(`<option value="${safeItem}">${safeItem}</option>`);
    }
    return options.join("");
}

function getCurrentSelectedValues() {
    return Array.from(document.querySelectorAll("#items-container select[name*='[descripcion]']"))
        .map((s) => s.value)
        .filter((v) => v);
}

function handleItemSelectChange(select) {
    const selectedValue = select.value;
    if (!selectedValue) {
        syncItemSelectors();
        return;
    }

    const duplicate = Array.from(document.querySelectorAll("#items-container select[name*='[descripcion]']"))
        .some((other) => other !== select && other.value === selectedValue);

    if (duplicate) {
        select.value = "";
        select.setCustomValidity("Este item ya fue agregado en otra fila.");
        select.reportValidity();
        select.setCustomValidity("");
    }
    syncItemSelectors();
}

function syncItemSelectors() {
    const selects = Array.from(document.querySelectorAll("#items-container select[name*='[descripcion]']"));
    const selected = getCurrentSelectedValues();
    for (const select of selects) {
        const ownValue = select.value;
        for (const option of select.options) {
            if (!option.value) continue;
            option.disabled = option.value !== ownValue && selected.includes(option.value);
        }
    }
}

function eliminarItem(button) {
    const row = button.closest(".item-row");
    if (row) row.remove();
    syncItemSelectors();
}

function canAddItemRow(container) {
    const rows = Array.from(container.querySelectorAll(".item-row"));
    if (rows.length === 0) return true;

    const lastRow = rows[rows.length - 1];
    const select = lastRow.querySelector("select[name*='[descripcion]']");
    const qtyInput = lastRow.querySelector("input[name*='[cantidad]']");

    if (select && !select.value) {
        select.reportValidity();
        return false;
    }
    if (qtyInput) {
        const qty = Number(qtyInput.value);
        const qtyValida = qtyInput.value !== "" && !Number.isNaN(qty) && qty > 0;
        if (!qtyValida) {
            qtyInput.reportValidity();
            qtyInput.focus();
            return false;
        }
    }
    return true;
}

function agregarItem() {
    const container = document.getElementById("items-container");
    if (!container) return;
    if (!canAddItemRow(container)) return;

    const div = document.createElement("div");
    div.className = "item-row";
    div.innerHTML = `
        <select name="items[${itemCount}][descripcion]" required>
            ${renderItemOptions()}
        </select>
        <input type="number" name="items[${itemCount}][cantidad]" placeholder="Cantidad" step="0.01" min="0.01" required>
        <button type="button" onclick="eliminarItem(this)">X</button>
    `;
    container.appendChild(div);
    const select = div.querySelector("select");
    if (select) {
        select.addEventListener("change", () => handleItemSelectChange(select));
    }
    itemCount++;
    syncItemSelectors();
}

document.addEventListener("DOMContentLoaded", () => {
    const selects = document.querySelectorAll("#items-container select[name*='[descripcion]']");
    for (const select of selects) {
        select.addEventListener("change", () => handleItemSelectChange(select));
    }
    syncItemSelectors();
});

function verDetalle(id) {
    fetch(`/api/requisiciones/${id}`)
        .then((r) => r.json())
        .then((data) => {
            const content = document.getElementById("modal-content");
            const modal = document.getElementById("modal-detalle");
            if (!content || !modal) return;
            const headerTitle = modal.querySelector("header h3");
            if (headerTitle) {
                headerTitle.textContent = `Detalle de Requisici\u00f3n: ${data.folio || "-"}`;
            }

            const items = Array.isArray(data.items) ? data.items : [];
            const showDelivered = items.some(
                (i) => i.cantidad_entregada !== null && i.cantidad_entregada !== undefined
            );
            const itemRows = items
                .map((i) => {
                    const qe = i.cantidad_entregada;
                    const hasQe = qe !== null && qe !== undefined;
                    const isZero = hasQe && Number(qe) === 0;
                    const despCls = isZero
                        ? "qty-col qty-despachada qty-zero"
                        : "qty-col qty-despachada";
                    return `<tr>
                    <td>${escapeHtml(i.descripcion || "-")}</td>
                    <td class="qty-col qty-solicitada">${fmtQty(i.cantidad)}</td>
                    ${showDelivered ? `<td class="${despCls}">${fmtQty(qe)}</td>` : ""}
                </tr>`;
                })
                .join("");

            const timeline = Array.isArray(data.timeline) ? data.timeline : [];
            const deliveryChipCls =
                { completa: "resultado-completa", parcial: "resultado-parcial", no_entregada: "resultado-no-entregada" }[
                    data.delivery_result
                ] || "";

            function timelineExtra(evento) {
                const e = String(evento || "").toLowerCase();
                if (e.includes("aprobada") && data.approval_comment) {
                    return `<div class="timeline-extra">${escapeHtml(data.approval_comment)}</div>`;
                }
                if (e.includes("rechazada")) {
                    const parts = [];
                    if (data.rejection_reason) parts.push(`Razón: ${data.rejection_reason}`);
                    if (data.rejection_comment) parts.push(`Comentario: ${data.rejection_comment}`);
                    if (parts.length) return `<div class="timeline-extra">${escapeHtml(parts.join(" · "))}</div>`;
                }
                if (e.includes("preparacion/entrega")) {
                    const chip = data.delivery_result
                        ? `<span class="resultado-chip ${deliveryChipCls}">${escapeHtml(data.delivery_result)}</span>`
                        : "";
                    const comment = data.delivery_comment
                        ? `<div class="timeline-extra">${escapeHtml(data.delivery_comment)}</div>`
                        : "";
                    return `<div class="timeline-extra-wrap">${chip}${comment}</div>`;
                }
                if (e.includes("liquidada")) {
                    return `<div class="timeline-extra"><span class="badge success">Liquidada</span></div>`;
                }
                return "";
            }

            const timelineRows = timeline
                .map((event) => {
                    const tituloEvento = String(event.evento || "-");
                    const actor =
                        event.actor && !tituloEvento.toLowerCase().includes(" por ") ? `por ${event.actor}` : "";
                    const fechaHora = formatDate(event.fecha_hora);
                    const actorHtml = actor ? `<span class="timeline-actor">${escapeHtml(actor)}</span>` : "";
                    return `<div class="timeline-item">
                                <div class="timeline-main">
                                    <span class="timeline-event">${escapeHtml(tituloEvento)}</span>
                                    ${actorHtml}
                                    ${timelineExtra(event.evento)}
                                </div>
                                <div class="timeline-time">${fechaHora}</div>
                            </div>`;
                })
                .join("");
            const prokeySummary = Array.isArray(data.prokey_summary) ? data.prokey_summary : [];
            const showProkeySummary = data.estado === "liquidada";
            const prokeyRows = prokeySummary
                .map(
                    (item) =>
                        `<li><strong>${fmtQty(item.cantidad_usada)}</strong> x ${escapeHtml(item.descripcion || "-")}</li>`
                )
                .join("");
            const prokeyBlock = showProkeySummary
                ? `<section class="detalle-block prokey-summary-block prokey-summary">
                        <h4>RESUMEN PARA CARGA EN PROKEY</h4>
                        <div class="panel-content">
                            <ul class="prokey-summary-list">
                                ${prokeyRows || "<li>Sin items usados para cargar.</li>"}
                            </ul>
                        </div>
                   </section>`
                : "";

            content.innerHTML = `
                <section class="detalle-items-section items-table-container">
                    <h4><span class="icon-items">\u2299</span> Items Solicitados</h4>
                    <div class="detalle-items-wrap">
                        <table class="detalle-items-table">
                            <thead><tr>
                                <th>Item / Producto</th>
                                <th class="qty-col">Cant. Solicitada</th>
                                ${showDelivered ? '<th class="qty-col">Cant. Despachada</th>' : ""}
                            </tr></thead>
                            <tbody>
                                ${itemRows || '<tr><td colspan="3">Sin items</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </section>
                <section class="detalle-content-grid">
                    <section class="detalle-block detalle-main detalle-panel">
                        <h4>Informaci\u00f3n General</h4>
                        <div class="panel-content">
                            <div class="detalle-meta-grid">
                                <div class="meta-line">
                                    <span class="meta-label label-orange">\u25ce SOLICITANTE</span>
                                    <strong>${escapeHtml(data.solicitante || "-")}</strong>
                                </div>
                                <div class="meta-line">
                                    <span class="meta-label label-green">\u25c9 COD. CLIENTE</span>
                                    <strong>${escapeHtml(data.cliente_codigo || "-")}</strong>
                                </div>
                                <div class="meta-line">
                                    <span class="meta-label label-blue">\u25ce CLIENTE</span>
                                    <strong>${escapeHtml(data.cliente_nombre || "-")}</strong>
                                </div>
                                <div class="meta-line">
                                    <span class="meta-label label-blue">\u25c9 RUTA PRINCIPAL</span>
                                    <strong>${escapeHtml(data.cliente_ruta_principal || "-")}</strong>
                                </div>
                            </div>
                            <div class="detalle-justificacion">
                                <span class="meta-label label-orange">\u270e JUSTIFICACI\u00d3N</span>
                                <p>${escapeHtml(data.justificacion || "-")}</p>
                            </div>
                        </div>
                        ${prokeyBlock}
                    </section>
                    <aside class="detalle-side">
                        <section class="detalle-block timeline-container">
                            <h4>Historial del Flujo</h4>
                            <div class="panel-content">
                                <div class="timeline-list">
                                    ${timelineRows || '<div class="timeline-item"><div class="timeline-main"><span class="timeline-event">Sin movimientos</span></div><div class="timeline-time">-</div></div>'}
                                </div>
                            </div>
                        </section>
                        <section class="detalle-block comentarios-section">
                            <h4>Comentarios</h4>
                            <div class="panel-content">
                                <div class="comentarios-list">
                                    <div class="comentario-item">
                                        <span class="meta-label label-muted">APROBACI\u00d3N</span>
                                        <p>${escapeHtml(data.approval_comment || "-")}</p>
                                    </div>
                                    <div class="comentario-item">
                                        <span class="meta-label label-muted">RAZ\u00d3N RECHAZO</span>
                                        <p>${escapeHtml(data.rejection_reason || "-")}</p>
                                    </div>
                                    <div class="comentario-item">
                                        <span class="meta-label label-muted">COMENTARIO RECHAZO</span>
                                        <p>${escapeHtml(data.rejection_comment || "-")}</p>
                                    </div>
                                    <div class="comentario-item">
                                        <span class="meta-label label-muted">ENTREGA</span>
                                        <p>${escapeHtml(data.delivery_comment || "-")}</p>
                                    </div>
                                </div>
                            </div>
                        </section>
                    </aside>
                </section>
            `;
            modal.showModal();
        });
}

function cerrarModal() {
    const modal = document.getElementById("modal-detalle");
    if (modal) modal.close();
}
