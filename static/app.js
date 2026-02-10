let itemCount = 1;

function renderItemOptions() {
    const catalogo = window.CATALOGO_ITEMS || [];
    const options = ['<option value="">Seleccionar item...</option>'];
    for (const item of catalogo) {
        options.push(`<option value="${item}">${item}</option>`);
    }
    return options.join("");
}

function agregarItem() {
    const container = document.getElementById("items-container");
    if (!container) return;

    const div = document.createElement("div");
    div.className = "item-row";
    div.innerHTML = `
        <select name="items[${itemCount}][descripcion]" required>
            ${renderItemOptions()}
        </select>
        <input type="number" name="items[${itemCount}][cantidad]" placeholder="Cantidad" step="0.01" min="0.01" required>
        <button type="button" onclick="this.parentElement.remove()">X</button>
    `;
    container.appendChild(div);
    itemCount++;
}

function verDetalle(id) {
    fetch(`/api/requisiciones/${id}`)
        .then((r) => r.json())
        .then((data) => {
            const content = document.getElementById("modal-content");
            const modal = document.getElementById("modal-detalle");
            if (!content || !modal) return;

            content.innerHTML = `
                <p><strong>Folio:</strong> ${data.folio}</p>
                <p><strong>Justificacion:</strong> ${data.justificacion}</p>
                <ul>${(data.items || []).map((i) => `<li>${i.cantidad} - ${i.descripcion}</li>`).join("")}</ul>
            `;
            modal.showModal();
        });
}

function cerrarModal() {
    const modal = document.getElementById("modal-detalle");
    if (modal) modal.close();
}
