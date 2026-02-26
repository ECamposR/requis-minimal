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

function alertLabel(type) {
    const key = String(type || "").toUpperCase();
    const map = {
        ALERTA_FALTANTE: "Faltante",
        ALERTA_SOBRANTE: "Sobrante",
        ALERTA_RETORNO_EXTRA: "Retorno extra",
        ALERTA_SALIDA_SIN_SOPORTE: "Inconsistencia",
    };
    return map[key] || String(type || "Alerta");
}

function alertMessage(alert) {
    const type = String(alert?.type || "").toUpperCase();
    const data = alert?.data && typeof alert.data === "object" ? alert.data : {};
    if (type === "ALERTA_FALTANTE" || type === "ALERTA_SOBRANTE") {
        if (
            data.expected_return !== undefined &&
            data.returned !== undefined &&
            (data.diferencia !== undefined || data.difference !== undefined)
        ) {
            const diff = data.diferencia !== undefined ? data.diferencia : data.difference;
            return `Esperado regrese ${fmtQty(data.expected_return)}, regresó ${fmtQty(data.returned)}, dif ${fmtQty(diff)}`;
        }
        return "";
    }
    if (type === "ALERTA_RETORNO_EXTRA") {
        if (data.delivered !== undefined && data.returned !== undefined) {
            return `Regresó ${fmtQty(data.returned)}, entregado ${fmtQty(data.delivered)}`;
        }
        return "";
    }
    if (type === "ALERTA_SALIDA_SIN_SOPORTE") {
        if (data.total_out !== undefined && data.delivered !== undefined) {
            return `Salió ${fmtQty(data.total_out)}, entregado ${fmtQty(data.delivered)}`;
        }
        return "";
    }
    return "";
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
                    const difference = Number(i.difference ?? i.delta ?? 0);
                    const differenceCls = difference > 0 ? "dif dif--pos" : difference < 0 ? "dif dif--neg" : "dif dif--zero";
                    const alerts = Array.isArray(i.liquidation_alerts) ? i.liquidation_alerts : [];
                    const alertBadges = alerts.length
                        ? alerts
                              .map((a) => {
                                  const sev = a?.severity === "high" ? "high" : "warn";
                                  const code = escapeHtml(a?.type || "ALERTA");
                                  const label = escapeHtml(alertLabel(a?.type));
                                  const detail = alertMessage(a);
                                  const detailText = detail ? `${escapeHtml(detail)} · ` : "";
                                  const title = `${label}: ${detailText}(interno: ${code})`;
                                  return `<span class="liq-alert-badge ${sev}" title="${title}">${label}</span>`;
                              })
                              .join("")
                        : '<span class="liq-alert-empty">Sin alertas</span>';
                    const noteAttentionClass = alerts.length ? "item-note--attention" : "";
                    const noteHtml = i.item_liquidation_note
                        ? `<div class="liq-item-note item-note ${noteAttentionClass}">${escapeHtml(i.item_liquidation_note)}</div>`
                        : "";
                    const mode = (i.mode || "RETORNABLE").toUpperCase();
                    const ingresoPk = mode === "RETORNABLE" ? fmtQty(i.pk_ingreso_qty) : "0";
                    return `<tr>
                        <td><strong>${escapeHtml(i.descripcion || "-")}</strong>${noteHtml}</td>
                        <td class="qty-col">${fmtQty(i.cantidad_entregada)}</td>
                        <td class="qty-col">${escapeHtml(mode)}</td>
                        <td class="qty-col">${fmtQty(i.used ?? i.qty_used)}</td>
                        <td class="qty-col">${fmtQty(i.not_used ?? i.qty_left_at_client)}</td>
                        <td class="qty-col">${fmtQty(i.returned ?? i.qty_returned_to_warehouse)}</td>
                        <td class="qty-col ${differenceCls}">${fmtQty(difference)}</td>
                        <td class="qty-col">
                            <span class="pk-help" title="Pendiente de ingresar en Prokey por bodega (solo retornables)">${ingresoPk}</span>
                        </td>
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
            const topAlertEntries = Object.entries(
                allAlerts.reduce((acc, current) => {
                    const key = alertLabel(current?.type);
                    acc[key] = (acc[key] || 0) + 1;
                    return acc;
                }, {})
            )
                .sort((a, b) => b[1] - a[1])
                .slice(0, 3);
            const topAlertTypes = topAlertEntries.length
                ? topAlertEntries.map(([label, count]) => `${escapeHtml(label)} (${count})`).join(", ")
                : "Ninguno";
            const prokeyRefHtml = data.prokey_ref
                ? escapeHtml(data.prokey_ref)
                : `Pendiente <span class="badge warning prokey-pending-badge">Prokey pendiente</span>
                   <a href="/requisiciones/${data.id}/prokey-ref" class="prokey-add-link">Agregar referencia Prokey</a>`;
            const liquidationComment = data.liquidation_comment
                ? escapeHtml(data.liquidation_comment)
                : "—";
            const itemsSection = isLiquidada
                ? `<section class="detalle-items-section">
                    <h4><span class="icon-items">\u2299</span> Items Liquidados</h4>
                    <div class="detalle-items-wrap liquidacion-paper-wrap">
                        <table class="detalle-items-table liquidacion-paper-table">
                            <thead><tr>
                                <th>Descripcion</th>
                                <th class="qty-col">Entregado</th>
                                <th class="qty-col">Tipo</th>
                                <th class="qty-col">Usado</th>
                                <th class="qty-col">No usado</th>
                                <th class="qty-col">Regresa</th>
                                <th class="qty-col" title="Diferencia (Esperado - Regresa)">DIF</th>
                                <th class="qty-col" title="Pendiente de ingresar en Prokey por bodega (solo retornables)">Ingreso PK</th>
                                <th>Alertas</th>
                            </tr></thead>
                            <tbody>
                                ${liquidacionRows || '<tr><td colspan="9">Sin items</td></tr>'}
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
            const pdfAction = data.pdf_url
                ? `<a class="secondary" role="button" href="${escapeHtml(data.pdf_url)}" target="_blank" rel="noopener noreferrer">Ver PDF</a>`
                : `<button type="button" class="secondary" disabled title="En desarrollo">Ver PDF</button>`;
            const commentsToggleHtml = `
                <details class="detalle-collapsible">
                    <summary>Otros comentarios y proceso</summary>
                    <div class="comentarios-list">
                        <div class="comentario-item">
                            <span class="meta-label label-muted">APROBACIÓN</span>
                            <p>${escapeHtml(data.approval_comment || "-")}</p>
                        </div>
                        <div class="comentario-item">
                            <span class="meta-label label-muted">RAZÓN RECHAZO</span>
                            <p>${escapeHtml(data.rejection_reason || "-")}</p>
                        </div>
                        <div class="comentario-item">
                            <span class="meta-label label-muted">COMENTARIO RECHAZO</span>
                            <p>${escapeHtml(data.rejection_comment || "-")}</p>
                        </div>
                        <div class="comentario-item">
                            <span class="meta-label label-muted">COMENTARIO ENTREGA</span>
                            <p>${escapeHtml(data.delivery_comment || "-")}</p>
                        </div>
                    </div>
                </details>
            `;

            content.innerHTML = `
                <section class="detalle-dashboard-header">
                    <div>
                        <h4 class="detalle-dashboard-title">Requisición ${escapeHtml(data.folio || "-")}</h4>
                        <span class="badge info">Creada: ${fmtDateTime(data.created_at)}</span>
                    </div>
                    <div class="detalle-dashboard-actions">
                        ${pdfAction}
                    </div>
                </section>
                <section class="detalle-dashboard-grid">
                    <article class="detalle-block dashboard-card">
                        <h4>Información general</h4>
                        <div class="detalle-meta-grid">
                            <div class="meta-line">
                                <span class="meta-label label-blue">CLIENTE</span>
                                <strong>${escapeHtml(data.cliente_nombre || "-")}</strong>
                            </div>
                            <div class="meta-line">
                                <span class="meta-label label-green">COD. CLIENTE</span>
                                <strong>${escapeHtml(data.cliente_codigo || "-")}</strong>
                            </div>
                            <div class="meta-line">
                                <span class="meta-label label-blue">RUTA PRINCIPAL</span>
                                <strong>${escapeHtml(data.cliente_ruta_principal || "-")}</strong>
                            </div>
                            <div class="meta-line">
                                <span class="meta-label label-orange">SOLICITANTE</span>
                                <strong>${escapeHtml(data.solicitante || "-")}</strong>
                            </div>
                        </div>
                    </article>
                    <article class="detalle-block dashboard-card">
                        <h4>Estado liquidación</h4>
                        <div class="flujo-list">
                            <div class="flujo-item">
                                <span class="meta-label">Estado</span>
                                <div class="flujo-value">${escapeHtml(data.estado || "-")}</div>
                            </div>
                            <div class="flujo-item">
                                <span class="meta-label">Resultado entrega</span>
                                ${resultHtml}
                            </div>
                            <div class="flujo-item">
                                <span class="meta-label">Por</span>
                                <div class="flujo-value">${escapeHtml(data.liquidated_by_name || data.delivered_by || "-")}</div>
                            </div>
                            <div class="flujo-item">
                                <span class="meta-label">Ref Prokey</span>
                                <div class="flujo-value">${prokeyRefHtml}</div>
                            </div>
                        </div>
                    </article>
                    <article class="detalle-block dashboard-card">
                        <h4>Alertas de conciliación</h4>
                        <div class="liquidacion-summary-grid">
                            <div><span class="meta-label">Total</span><strong>${allAlerts.length} detectadas</strong></div>
                            <div><span class="meta-label">Severidad alta</span><strong>${highAlerts}</strong></div>
                        </div>
                        <p class="status-muted"><strong>Tipos frecuentes:</strong> ${topAlertTypes}</p>
                    </article>
                    <article class="detalle-block dashboard-card dashboard-timeline">
                        <h4>Línea de tiempo del flujo</h4>
                        <div class="timeline-list">
                            ${timelineRows || '<div class="timeline-item"><div class="timeline-main"><span class="timeline-event">Sin movimientos</span></div><div class="timeline-time">-</div></div>'}
                        </div>
                    </article>
                </section>
                ${itemsSection}
                <section class="detalle-bottom-grid">
                    <article class="detalle-block dashboard-card">
                        <h4>Comentario de liquidación</h4>
                        <p class="liquidation-comment">${liquidationComment}</p>
                    </article>
                    <article class="detalle-block dashboard-card">
                        <h4>Justificación</h4>
                        <p>${escapeHtml(data.justificacion || "-")}</p>
                    </article>
                </section>
                ${commentsToggleHtml}
            `;
            modal.showModal();
        });
}

function cerrarModal() {
    const modal = document.getElementById("modal-detalle");
    if (modal) modal.close();
}
