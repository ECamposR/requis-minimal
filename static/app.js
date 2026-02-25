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

function fmtDateTime(value) {
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return escapeHtml(value);
    const dd = String(date.getDate()).padStart(2, "0");
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const yyyy = String(date.getFullYear());
    const hh = String(date.getHours()).padStart(2, "0");
    const mi = String(date.getMinutes()).padStart(2, "0");
    const ss = String(date.getSeconds()).padStart(2, "0");
    return `${dd}/${mm}/${yyyy} ${hh}:${mi}:${ss}`;
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
            const isLiquidada = data.estado === "liquidada";
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
            const liquidacionRows = items
                .map((i) => {
                    const delta = Number(i.delta || 0);
                    const deltaCls = delta < 0 ? "delta-danger" : delta !== 0 ? "delta-warn" : "";
                    const alerts = Array.isArray(i.liquidation_alerts) ? i.liquidation_alerts : [];
                    const alertBadges = alerts.length
                        ? alerts
                              .map((a) => {
                                  const sev = a?.severity === "high" ? "high" : "warn";
                                  return `<span class="liq-alert-badge ${sev}">${escapeHtml(a?.type || "ALERTA")}</span>`;
                              })
                              .join("")
                        : '<span class="liq-alert-empty">Sin alertas</span>';
                    const noteHtml = i.item_liquidation_note
                        ? `<div class="liq-item-note">${escapeHtml(i.item_liquidation_note)}</div>`
                        : "";
                    return `<tr>
                        <td><strong>${escapeHtml(i.descripcion || "-")}</strong>${noteHtml}</td>
                        <td class="qty-col">${fmtQty(i.cantidad)}</td>
                        <td class="qty-col">${fmtQty(i.cantidad_entregada)}</td>
                        <td class="qty-col">${fmtQty(i.qty_returned_to_warehouse)}</td>
                        <td class="qty-col">${fmtQty(i.qty_ocupo)}</td>
                        <td class="qty-col">
                            <span class="pk-help" title="Pendiente de ingresar en Prokey por bodega">${fmtQty(i.pk_ingreso_qty)}</span>
                        </td>
                        <td class="qty-col ${deltaCls}">${fmtQty(delta)}</td>
                        <td>${alertBadges}</td>
                    </tr>`;
                })
                .join("");

            const resultVal = data.delivery_result || "-";
            const chipCls =
                { completa: "resultado-completa", parcial: "resultado-parcial", no_entregada: "resultado-no-entregada" }[
                    data.delivery_result
                ] || "";
            const resultHtml = data.delivery_result
                ? `<span class="resultado-chip ${chipCls}">${escapeHtml(resultVal)}</span>`
                : `<span class="flujo-value">${escapeHtml(resultVal)}</span>`;
            const timeline = Array.isArray(data.timeline) ? data.timeline : [];
            const timelineRows = timeline
                .map(
                    (event) => `<div class="timeline-item">
                                    <div class="timeline-main">
                                        <span class="timeline-event">${escapeHtml(event.evento || "-")}</span>
                                        <span class="timeline-actor">${escapeHtml(event.actor || "-")}</span>
                                    </div>
                                    <div class="timeline-time">${fmtDateTime(event.fecha_hora)}</div>
                                </div>`
                )
                .join("");
            const allAlerts = items.flatMap((i) => (Array.isArray(i.liquidation_alerts) ? i.liquidation_alerts : []));
            const highAlerts = allAlerts.filter((a) => a?.severity === "high").length;
            const resumenAlertas =
                allAlerts.length > 0
                    ? `${allAlerts.length} alertas (${highAlerts} de severidad alta)`
                    : "Sin alertas";
            const liquidacionHeader = isLiquidada
                ? `<section class="liquidacion-summary">
                    <h4>Resumen de Liquidacion</h4>
                    <div class="liquidacion-summary-grid">
                        <div><span class="meta-label">Referencia Prokey</span><strong>${escapeHtml(data.prokey_ref || "-")}</strong></div>
                        <div><span class="meta-label">Liquidado por</span><strong>${escapeHtml(data.liquidated_by_name || "-")}</strong></div>
                        <div><span class="meta-label">Fecha</span><strong>${fmtDateTime(data.liquidated_at)}</strong></div>
                        <div><span class="meta-label">Alertas</span><strong>${escapeHtml(resumenAlertas)}</strong></div>
                    </div>
                    ${
                        data.liquidation_comment
                            ? `<div class="liquidacion-summary-comment"><span class="meta-label">Comentario</span><p>${escapeHtml(data.liquidation_comment)}</p></div>`
                            : ""
                    }
                </section>`
                : "";
            const itemsSection = isLiquidada
                ? `<section class="detalle-items-section">
                    <h4><span class="icon-items">\u2299</span> Items Liquidados</h4>
                    <div class="detalle-items-wrap liquidacion-paper-wrap">
                        <table class="detalle-items-table liquidacion-paper-table">
                            <thead><tr>
                                <th>Descripcion</th>
                                <th class="qty-col">Solicitado</th>
                                <th class="qty-col">Lleva</th>
                                <th class="qty-col">Regresa</th>
                                <th class="qty-col">Ocupo</th>
                                <th class="qty-col">Ingreso PK</th>
                                <th class="qty-col">Delta</th>
                                <th>Alertas</th>
                            </tr></thead>
                            <tbody>
                                ${liquidacionRows || '<tr><td colspan="8">Sin items</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </section>`
                : `<section class="detalle-items-section">
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
                </section>`;

            content.innerHTML = `
                ${liquidacionHeader}
                ${itemsSection}
                <section class="detalle-content-grid">
                    <section class="detalle-block detalle-main">
                        <h4>Informaci\u00f3n General</h4>
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
                    </section>
                    <aside class="detalle-side">
                        <section class="detalle-block">
                            <h4>Estado del Flujo</h4>
                            <div class="flujo-list">
                                <div class="flujo-item flujo-item-card">
                                    <span class="meta-label label-orange">\u25ce APROBADO POR</span>
                                    <div class="flujo-value">${escapeHtml(data.approved_by || "-")}</div>
                                </div>
                                <div class="flujo-item">
                                    <span class="meta-label">RESULTADO ENTREGA</span>
                                    ${resultHtml}
                                </div>
                                <div class="flujo-item">
                                    <span class="meta-label label-orange">\u25c9 ENTREGADO POR</span>
                                    <div class="flujo-value">${escapeHtml(data.delivered_by || "-")}</div>
                                </div>
                                <div class="flujo-item">
                                    <span class="meta-label label-orange">\u25c9 RECIBIÓ</span>
                                    <div class="flujo-value">${escapeHtml(data.delivered_to || "-")}</div>
                                </div>
                                ${
                                    isLiquidada
                                        ? `<div class="flujo-item">
                                            <span class="meta-label label-orange">\u25c9 LIQUIDADO POR</span>
                                            <div class="flujo-value">${escapeHtml(data.liquidated_by_name || "-")}</div>
                                        </div>`
                                        : ""
                                }
                            </div>
                        </section>
                        <section class="detalle-block">
                            <h4>Comentarios</h4>
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
                        </section>
                        <section class="detalle-block">
                            <h4>Historial</h4>
                            <div class="timeline-list">
                                ${timelineRows || '<div class="timeline-item"><div class="timeline-main"><span class="timeline-event">Sin movimientos</span></div><div class="timeline-time">-</div></div>'}
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
