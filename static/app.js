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
            const items = Array.isArray(data.items) ? data.items : [];
            const showDelivered = items.some((i) => i.cantidad_entregada !== null && i.cantidad_entregada !== undefined);
            const rows = items.map((i) => `
                <tr>
                    <td>${escapeHtml(i.descripcion || "-")}</td>
                    <td class="qty-col">${fmtQty(i.cantidad)}</td>
                    ${showDelivered ? `<td class="qty-col">${fmtQty(i.cantidad_entregada)}</td>` : ""}
                </tr>
            `).join("");
            const emptyColspan = showDelivered ? 3 : 2;

            content.innerHTML = `
                <section class="detalle-grid">
                    <div class="kv"><span>Folio</span><strong>${escapeHtml(data.folio || "-")}</strong></div>
                    <div class="kv"><span>Solicitante</span><strong>${escapeHtml(data.solicitante || "-")}</strong></div>
                    <div class="kv"><span>Cod. cliente</span><strong>${escapeHtml(data.cliente_codigo || "-")}</strong></div>
                    <div class="kv"><span>Cliente</span><strong>${escapeHtml(data.cliente_nombre || "-")}</strong></div>
                    <div class="kv"><span>Ruta principal</span><strong>${escapeHtml(data.cliente_ruta_principal || "-")}</strong></div>
                    <div class="kv"><span>Aprobado por</span><strong>${escapeHtml(data.approved_by || "-")}</strong></div>
                    <div class="kv"><span>Rechazado por</span><strong>${escapeHtml(data.rejected_by || "-")}</strong></div>
                    <div class="kv"><span>Entregado por</span><strong>${escapeHtml(data.delivered_by || "-")}</strong></div>
                    <div class="kv"><span>Resultado entrega</span><strong>${escapeHtml(data.delivery_result || "-")}</strong></div>
                    <div class="kv"><span>Recibio</span><strong>${escapeHtml(data.delivered_to || "-")}</strong></div>
                </section>
                <section class="detalle-notes">
                    <div class="note"><span>Justificacion</span><p>${escapeHtml(data.justificacion || "-")}</p></div>
                    <div class="note"><span>Comentario aprobacion</span><p>${escapeHtml(data.approval_comment || "-")}</p></div>
                    <div class="note"><span>Razon rechazo</span><p>${escapeHtml(data.rejection_reason || "-")}</p></div>
                    <div class="note"><span>Comentario rechazo</span><p>${escapeHtml(data.rejection_comment || "-")}</p></div>
                    <div class="note"><span>Comentario entrega</span><p>${escapeHtml(data.delivery_comment || "-")}</p></div>
                </section>
                <h4>Items</h4>
                <div class="detalle-items-wrap">
                    <table class="detalle-items-table">
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th class="qty-col">Cant. solicitada</th>
                                ${showDelivered ? '<th class="qty-col">Cant. despachada</th>' : ""}
                            </tr>
                        </thead>
                        <tbody>
                            ${rows || `<tr><td colspan="${emptyColspan}">Sin items</td></tr>`}
                        </tbody>
                    </table>
                </div>
            `;
            modal.showModal();
        });
}

function cerrarModal() {
    const modal = document.getElementById("modal-detalle");
    if (modal) modal.close();
}
