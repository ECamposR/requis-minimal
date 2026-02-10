let itemCount = 1;

function agregarItem() {
    const container = document.getElementById("items-container");
    if (!container) return;

    const div = document.createElement("div");
    div.className = "item-row";
    div.innerHTML = `
        <input type="text" name="items[${itemCount}][descripcion]" placeholder="Descripcion" required>
        <input type="number" name="items[${itemCount}][cantidad]" placeholder="Cantidad" step="0.01" min="0.01" required>
        <input type="text" name="items[${itemCount}][unidad]" placeholder="Unidad" required>
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
                <ul>${(data.items || []).map((i) => `<li>${i.cantidad} ${i.unidad} - ${i.descripcion}</li>`).join("")}</ul>
            `;
            modal.showModal();
        });
}

function cerrarModal() {
    const modal = document.getElementById("modal-detalle");
    if (modal) modal.close();
}
