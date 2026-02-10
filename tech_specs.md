# 📋 Especificación Técnica: Sistema de Requisiciones Digitales

## 1. VISIÓN GENERAL DEL PROYECTO

### 1.1 Propósito
Sistema web interno para digitalizar el proceso de requisiciones de inventario que no están cubiertas por el picking list del ERP. Proporciona trazabilidad básica, flujo de aprobación y elimina malos entendidos entre usuarios y bodega.

### 1.2 Usuarios y Roles
- **Solicitante (15 usuarios)**: Crea requisiciones
- **Aprobador (5-6 usuarios)**: Aprueba/rechaza requisiciones de su departamento
- **Bodega (9 usuarios)**: Procesa y entrega materiales
- **Administrador (1-2 usuarios)**: Gestión completa del sistema

### 1.3 Alcance
- Solo accesible en LAN (no exposición a internet)
- ~24 usuarios concurrentes máximo
- Estimado: 50-200 requisiciones/mes
- **Tiempo de desarrollo estimado: 1-2 semanas**

---

## 2. STACK TECNOLÓGICO

### 2.1 Backend
```yaml
Lenguaje: Python 3.11+
Framework: FastAPI 0.104+
ORM: SQLAlchemy 2.0+
Base de datos: SQLite
Autenticación: HTTP Basic Auth
Validación: Pydantic v2
```

### 2.2 Frontend
```yaml
Base: HTML5 + Jinja2 templates
CSS Framework: PicoCSS
JavaScript: Vanilla JS
```

### 2.3 Infraestructura
```yaml
Deployment: Python directo (Uvicorn)
Hosting: Servidor/PC en LAN
Backups: Manual (copiar archivo .db)
```

---

## 3. ESTRUCTURA DE DIRECTORIOS

```
requisiciones-system/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point FastAPI
│   ├── database.py             # Conexión SQLite
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── auth.py                 # Autenticación
│   └── crud.py                 # Operaciones DB
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── home.html
│   ├── crear_requisicion.html
│   ├── mis_requisiciones.html
│   ├── aprobar.html
│   └── bodega.html
│
├── static/
│   ├── style.css
│   └── app.js
│
├── .env
├── requirements.txt
├── init_db.py                  # Script para crear DB inicial
└── README.md
```

---

## 4. MODELO DE DATOS

### 4.1 Diagrama Relacional

```
┌─────────────────┐         ┌──────────────────┐
│     usuarios    │         │   requisiciones  │
├─────────────────┤         ├──────────────────┤
│ id (PK)         │◄───────┤│ id (PK)          │
│ username        │         │ folio            │
│ password        │         │ solicitante_id   │
│ nombre          │         │ estado           │
│ rol             │         │ departamento     │
│ departamento    │         │ justificacion    │
└─────────────────┘         │ created_at       │
                            │ approved_at      │
                            │ approved_by      │
                            │ delivered_at     │
                            │ delivered_by     │
                            │ delivered_to     │
                            │ rejection_reason │
                            └──────────────────┘
                                     │
                                     │
                            ┌────────▼─────────┐
                            │      items       │
                            ├──────────────────┤
                            │ id (PK)          │
                            │ requisicion_id   │
                            │ descripcion      │
                            │ cantidad         │
                            │ unidad           │
                            └──────────────────┘
```

### 4.2 Definición de Tablas SQL

```sql
-- usuarios
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,  -- Hash bcrypt
    nombre TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('user', 'aprobador', 'bodega', 'admin')),
    departamento TEXT NOT NULL
);

-- requisiciones
CREATE TABLE requisiciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folio TEXT UNIQUE NOT NULL,
    solicitante_id INTEGER NOT NULL,
    departamento TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'pendiente' 
        CHECK(estado IN ('pendiente', 'aprobada', 'rechazada', 'entregada')),
    justificacion TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by INTEGER,
    delivered_at TIMESTAMP,
    delivered_by INTEGER,
    delivered_to TEXT,  -- Nombre de quien recibe físicamente
    rejection_reason TEXT,
    
    FOREIGN KEY (solicitante_id) REFERENCES usuarios(id),
    FOREIGN KEY (approved_by) REFERENCES usuarios(id),
    FOREIGN KEY (delivered_by) REFERENCES usuarios(id)
);

-- items
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    requisicion_id INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    cantidad REAL NOT NULL CHECK(cantidad > 0),
    unidad TEXT NOT NULL,
    
    FOREIGN KEY (requisicion_id) REFERENCES requisiciones(id) ON DELETE CASCADE
);

-- Índices para performance
CREATE INDEX idx_requisiciones_estado ON requisiciones(estado);
CREATE INDEX idx_requisiciones_solicitante ON requisiciones(solicitante_id);
CREATE INDEX idx_requisiciones_departamento ON requisiciones(departamento);
```

---

## 5. MÁQUINA DE ESTADOS

### 5.1 Diagrama de Flujo

```
[PENDIENTE] 
     │
     ├─────aprobar────> [APROBADA] ────entregar────> [ENTREGADA]
     │
     └─────rechazar────> [RECHAZADA]
```

### 5.2 Transiciones Válidas

```python
ESTADO_TRANSICIONES = {
    'pendiente': ['aprobada', 'rechazada'],
    'aprobada': ['entregada'],
    'rechazada': [],  # Estado final
    'entregada': []   # Estado final
}
```

### 5.3 Permisos por Rol

```python
PERMISOS = {
    'user': {
        'crear_requisicion': True,
        'ver_propias': True,
        'ver_otras': False,
        'aprobar': False,
        'entregar': False
    },
    'aprobador': {
        'crear_requisicion': True,
        'ver_propias': True,
        'ver_otras': True,  # Solo de su departamento
        'aprobar': True,    # Solo de su departamento
        'rechazar': True,   # Solo de su departamento
        'entregar': False
    },
    'bodega': {
        'crear_requisicion': False,
        'ver_propias': False,
        'ver_aprobadas': True,
        'entregar': True,
        'aprobar': False
    },
    'admin': {
        'todo': True
    }
}
```

---

## 6. API ENDPOINTS

### 6.1 Autenticación

```
POST   /login       # Login (form)
GET    /logout      # Logout
```

### 6.2 Páginas (Server-side rendering)

```
GET    /                               # Home/dashboard
GET    /crear                          # Formulario crear requisición
POST   /crear                          # Procesar nueva requisición
GET    /mis-requisiciones              # Listar mis requisiciones
GET    /aprobar                        # Listar pendientes (solo aprobadores)
POST   /aprobar/{id}                   # Aprobar requisición
POST   /rechazar/{id}                  # Rechazar requisición
GET    /bodega                         # Listar aprobadas (solo bodega)
POST   /entregar/{id}                  # Marcar como entregada
GET    /api/requisiciones/{id}         # API: Obtener detalle (JSON)
```

### 6.3 Request/Response Examples

**POST /crear (form data)**
```
departamento=Operaciones
justificacion=Servicio urgente cliente ABC
items[0][descripcion]=Cable UTP Cat6
items[0][cantidad]=50
items[0][unidad]=m
items[1][descripcion]=Conectores RJ45
items[1][cantidad]=20
items[1][unidad]=pza
```

**Response**
```
302 Redirect → /mis-requisiciones
Flash message: "Requisición REQ-0001 creada exitosamente"
```

**GET /api/requisiciones/1 (JSON)**
```json
{
  "id": 1,
  "folio": "REQ-0001",
  "estado": "pendiente",
  "solicitante": {
    "id": 5,
    "nombre": "Juan Pérez"
  },
  "departamento": "Operaciones",
  "justificacion": "Servicio urgente cliente ABC",
  "items": [
    {
      "id": 1,
      "descripcion": "Cable UTP Cat6",
      "cantidad": 50.0,
      "unidad": "m"
    }
  ],
  "created_at": "2025-02-10T14:30:00",
  "approved_at": null,
  "delivered_at": null
}
```

---

## 7. LÓGICA DE NEGOCIO

### 7.1 Generación de Folio

```python
def generar_folio(db: Session) -> str:
    """
    Formato: REQ-NNNN
    Ejemplo: REQ-0001
    
    Lógica:
    - Buscar último folio
    - Incrementar contador
    """
    ultimo = db.query(Requisicion).order_by(Requisicion.id.desc()).first()
    numero = (ultimo.id + 1) if ultimo else 1
    return f"REQ-{numero:04d}"
```

### 7.2 Validaciones

```python
def puede_aprobar(requisicion: Requisicion, usuario: Usuario) -> bool:
    """
    Solo aprobadores del mismo departamento pueden aprobar.
    Admin puede aprobar cualquiera.
    """
    if usuario.rol == 'admin':
        return True
    if usuario.rol != 'aprobador':
        return False
    if requisicion.estado != 'pendiente':
        return False
    return requisicion.departamento == usuario.departamento

def puede_ver_requisicion(requisicion: Requisicion, usuario: Usuario) -> bool:
    """
    Determina si un usuario puede ver una requisición.
    """
    if usuario.rol == 'admin':
        return True
    
    # El solicitante puede ver sus propias requisiciones
    if usuario.id == requisicion.solicitante_id:
        return True
    
    # Aprobadores pueden ver las de su departamento
    if usuario.rol == 'aprobador' and usuario.departamento == requisicion.departamento:
        return True
    
    # Bodega puede ver aprobadas y entregadas
    if usuario.rol == 'bodega' and requisicion.estado in ['aprobada', 'entregada']:
        return True
    
    return False

def puede_entregar(requisicion: Requisicion, usuario: Usuario) -> bool:
    """
    Solo bodega y admin pueden marcar como entregada.
    La requisición debe estar aprobada.
    """
    if usuario.rol not in ['bodega', 'admin']:
        return False
    return requisicion.estado == 'aprobada'

def validar_transicion_estado(estado_actual: str, estado_nuevo: str) -> bool:
    """
    Verifica si la transición de estado es válida.
    """
    estados_validos = ESTADO_TRANSICIONES.get(estado_actual, [])
    return estado_nuevo in estados_validos
```

---

## 8. SEGURIDAD

### 8.1 Autenticación HTTP Basic

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import bcrypt

security = HTTPBasic()

def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Valida credenciales y retorna usuario autenticado.
    """
    user = db.query(Usuario).filter(Usuario.username == credentials.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Verificar password
    if not bcrypt.checkpw(
        credentials.password.encode('utf-8'), 
        user.password.encode('utf-8')
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    return user
```

### 8.2 Hash de Contraseñas

```python
import bcrypt

def hash_password(password: str) -> str:
    """
    Genera hash bcrypt de la contraseña.
    """
    return bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt()
    ).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si la contraseña coincide con el hash.
    """
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )
```

---

## 9. MODELOS SQLALCHEMY

### 9.1 app/models.py

```python
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    nombre = Column(String(150), nullable=False)
    rol = Column(String(20), nullable=False)
    departamento = Column(String(50), nullable=False)
    
    # Relaciones
    requisiciones_creadas = relationship("Requisicion", back_populates="solicitante", foreign_keys="Requisicion.solicitante_id")
    requisiciones_aprobadas = relationship("Requisicion", back_populates="aprobador", foreign_keys="Requisicion.approved_by")
    requisiciones_entregadas = relationship("Requisicion", back_populates="entregador", foreign_keys="Requisicion.delivered_by")

class Requisicion(Base):
    __tablename__ = "requisiciones"
    
    id = Column(Integer, primary_key=True, index=True)
    folio = Column(String(20), unique=True, nullable=False, index=True)
    solicitante_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    departamento = Column(String(50), nullable=False, index=True)
    estado = Column(String(20), nullable=False, default='pendiente', index=True)
    justificacion = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    approved_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    delivered_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    delivered_to = Column(String(150), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Relaciones
    solicitante = relationship("Usuario", back_populates="requisiciones_creadas", foreign_keys=[solicitante_id])
    aprobador = relationship("Usuario", back_populates="requisiciones_aprobadas", foreign_keys=[approved_by])
    entregador = relationship("Usuario", back_populates="requisiciones_entregadas", foreign_keys=[delivered_by])
    items = relationship("Item", back_populates="requisicion", cascade="all, delete-orphan")

class Item(Base):
    __tablename__ = "items"
    
    id = Column(Integer, primary_key=True, index=True)
    requisicion_id = Column(Integer, ForeignKey("requisiciones.id"), nullable=False)
    descripcion = Column(String(255), nullable=False)
    cantidad = Column(Float, nullable=False)
    unidad = Column(String(20), nullable=False)
    
    # Relaciones
    requisicion = relationship("Requisicion", back_populates="items")
```

---

## 10. SCHEMAS PYDANTIC

### 10.1 app/schemas.py

```python
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional

class ItemBase(BaseModel):
    descripcion: str = Field(..., min_length=3, max_length=255)
    cantidad: float = Field(..., gt=0)
    unidad: str = Field(..., min_length=1, max_length=20)

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    requisicion_id: int
    
    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    username: str
    nombre: str
    rol: str
    departamento: str

class Usuario(UsuarioBase):
    id: int
    
    class Config:
        from_attributes = True

class RequisicionBase(BaseModel):
    departamento: str = Field(..., min_length=2, max_length=50)
    justificacion: str = Field(..., min_length=10)

class RequisicionCreate(RequisicionBase):
    items: List[ItemCreate] = Field(..., min_length=1)
    
    @field_validator('items')
    def validar_items(cls, v):
        if not v:
            raise ValueError('Debe incluir al menos un item')
        return v

class Requisicion(RequisicionBase):
    id: int
    folio: str
    solicitante_id: int
    estado: str
    created_at: datetime
    approved_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    solicitante: Usuario
    items: List[Item]
    
    class Config:
        from_attributes = True
```

---

## 11. OPERACIONES CRUD

### 11.1 app/crud.py

```python
from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def crear_requisicion(
    db: Session,
    solicitante_id: int,
    departamento: str,
    justificacion: str
) -> models.Requisicion:
    """
    Crea una nueva requisición.
    """
    folio = generar_folio(db)
    
    requisicion = models.Requisicion(
        folio=folio,
        solicitante_id=solicitante_id,
        departamento=departamento,
        justificacion=justificacion,
        estado='pendiente'
    )
    
    db.add(requisicion)
    db.commit()
    db.refresh(requisicion)
    
    return requisicion

def agregar_item(
    db: Session,
    requisicion_id: int,
    descripcion: str,
    cantidad: float,
    unidad: str
) -> models.Item:
    """
    Agrega un item a una requisición.
    """
    item = models.Item(
        requisicion_id=requisicion_id,
        descripcion=descripcion,
        cantidad=cantidad,
        unidad=unidad
    )
    
    db.add(item)
    db.commit()
    db.refresh(item)
    
    return item

def aprobar_requisicion(
    db: Session,
    requisicion_id: int,
    aprobador_id: int
) -> models.Requisicion:
    """
    Aprueba una requisición.
    """
    requisicion = db.query(models.Requisicion).filter(
        models.Requisicion.id == requisicion_id
    ).first()
    
    if not requisicion:
        raise ValueError("Requisición no encontrada")
    
    if requisicion.estado != 'pendiente':
        raise ValueError("La requisición no está pendiente de aprobación")
    
    requisicion.estado = 'aprobada'
    requisicion.approved_at = datetime.utcnow()
    requisicion.approved_by = aprobador_id
    
    db.commit()
    db.refresh(requisicion)
    
    return requisicion

def rechazar_requisicion(
    db: Session,
    requisicion_id: int,
    razon: str
) -> models.Requisicion:
    """
    Rechaza una requisición.
    """
    requisicion = db.query(models.Requisicion).filter(
        models.Requisicion.id == requisicion_id
    ).first()
    
    if not requisicion:
        raise ValueError("Requisición no encontrada")
    
    if requisicion.estado != 'pendiente':
        raise ValueError("La requisición no está pendiente de aprobación")
    
    requisicion.estado = 'rechazada'
    requisicion.rejection_reason = razon
    
    db.commit()
    db.refresh(requisicion)
    
    return requisicion

def entregar_requisicion(
    db: Session,
    requisicion_id: int,
    entregador_id: int,
    receptor_nombre: str
) -> models.Requisicion:
    """
    Marca una requisición como entregada.
    """
    requisicion = db.query(models.Requisicion).filter(
        models.Requisicion.id == requisicion_id
    ).first()
    
    if not requisicion:
        raise ValueError("Requisición no encontrada")
    
    if requisicion.estado != 'aprobada':
        raise ValueError("La requisición no está aprobada")
    
    requisicion.estado = 'entregada'
    requisicion.delivered_at = datetime.utcnow()
    requisicion.delivered_by = entregador_id
    requisicion.delivered_to = receptor_nombre
    
    db.commit()
    db.refresh(requisicion)
    
    return requisicion

def generar_folio(db: Session) -> str:
    """
    Genera el siguiente folio disponible.
    """
    ultimo = db.query(models.Requisicion).order_by(
        models.Requisicion.id.desc()
    ).first()
    
    numero = (ultimo.id + 1) if ultimo else 1
    return f"REQ-{numero:04d}"
```

---

## 12. FRONTEND TEMPLATES

### 12.1 templates/base.html

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Sistema de Requisiciones{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css">
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    {% if current_user %}
    <nav class="container">
        <ul>
            <li><strong>Sistema de Requisiciones</strong></li>
        </ul>
        <ul>
            <li><a href="/">Inicio</a></li>
            {% if current_user.rol in ['user', 'aprobador', 'admin'] %}
            <li><a href="/crear">Nueva Requisición</a></li>
            <li><a href="/mis-requisiciones">Mis Requisiciones</a></li>
            {% endif %}
            {% if current_user.rol in ['aprobador', 'admin'] %}
            <li><a href="/aprobar">Aprobar</a></li>
            {% endif %}
            {% if current_user.rol in ['bodega', 'admin'] %}
            <li><a href="/bodega">Bodega</a></li>
            {% endif %}
            <li>{{ current_user.nombre }} | <a href="/logout">Salir</a></li>
        </ul>
    </nav>
    {% endif %}
    
    <main class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
    
    <script src="/static/app.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 12.2 templates/crear_requisicion.html

```html
{% extends "base.html" %}

{% block title %}Nueva Requisición{% endblock %}

{% block content %}
<article>
    <header>
        <h2>Nueva Requisición</h2>
    </header>
    
    <form method="POST" action="/crear">
        <label>
            Departamento
            <select name="departamento" required>
                <option value="">Seleccionar...</option>
                <option value="Ventas">Ventas</option>
                <option value="Operaciones">Operaciones</option>
                <option value="Mantenimiento">Mantenimiento</option>
                <option value="TI">TI</option>
            </select>
        </label>
        
        <label>
            Justificación
            <textarea name="justificacion" rows="4" required 
                      placeholder="Explica por qué necesitas estos materiales..."></textarea>
        </label>
        
        <fieldset id="items-container">
            <legend>Items Solicitados</legend>
            <div class="item-row" id="item-0">
                <input type="text" name="items[0][descripcion]" placeholder="Descripción del item" required>
                <input type="number" name="items[0][cantidad]" placeholder="Cantidad" step="0.01" required>
                <input type="text" name="items[0][unidad]" placeholder="Unidad (pza, m, kg, etc)" required>
            </div>
        </fieldset>
        
        <button type="button" onclick="agregarItem()" class="secondary">+ Agregar Item</button>
        <button type="submit">Crear y Enviar</button>
    </form>
</article>
{% endblock %}

{% block scripts %}
<script>
let itemCount = 1;

function agregarItem() {
    const container = document.getElementById('items-container');
    const div = document.createElement('div');
    div.className = 'item-row';
    div.id = `item-${itemCount}`;
    div.innerHTML = `
        <input type="text" name="items[${itemCount}][descripcion]" placeholder="Descripción del item" required>
        <input type="number" name="items[${itemCount}][cantidad]" placeholder="Cantidad" step="0.01" required>
        <input type="text" name="items[${itemCount}][unidad]" placeholder="Unidad" required>
        <button type="button" onclick="eliminarItem(${itemCount})" class="secondary outline">✕</button>
    `;
    container.appendChild(div);
    itemCount++;
}

function eliminarItem(id) {
    const item = document.getElementById(`item-${id}`);
    if (item) {
        item.remove();
    }
}
</script>
{% endblock %}
```

### 12.3 templates/mis_requisiciones.html

```html
{% extends "base.html" %}

{% block title %}Mis Requisiciones{% endblock %}

{% block content %}
<article>
    <header>
        <h2>Mis Requisiciones</h2>
    </header>
    
    {% if requisiciones %}
    <figure>
        <table role="grid">
            <thead>
                <tr>
                    <th>Folio</th>
                    <th>Departamento</th>
                    <th>Estado</th>
                    <th>Fecha Creación</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for req in requisiciones %}
                <tr>
                    <td><strong>{{ req.folio }}</strong></td>
                    <td>{{ req.departamento }}</td>
                    <td>
                        {% if req.estado == 'pendiente' %}
                            <span class="badge-warning">⏳ Pendiente</span>
                        {% elif req.estado == 'aprobada' %}
                            <span class="badge-success">✓ Aprobada</span>
                        {% elif req.estado == 'rechazada' %}
                            <span class="badge-error">✗ Rechazada</span>
                        {% elif req.estado == 'entregada' %}
                            <span class="badge-info">📦 Entregada</span>
                        {% endif %}
                    </td>
                    <td>{{ req.created_at.strftime('%d/%m/%Y %H:%M') }}</td>
                    <td>
                        <button onclick="verDetalle({{ req.id }})" class="secondary outline small">Ver Detalle</button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </figure>
    {% else %}
    <p>No tienes requisiciones creadas.</p>
    <a href="/crear" role="button">Crear Primera Requisición</a>
    {% endif %}
</article>

<dialog id="modal-detalle">
    <article>
        <header>
            <button aria-label="Close" rel="prev" onclick="cerrarModal()"></button>
            <h3>Detalle de Requisición</h3>
        </header>
        <div id="modal-content"></div>
    </article>
</dialog>
{% endblock %}

{% block scripts %}
<script>
async function verDetalle(id) {
    const response = await fetch(`/api/requisiciones/${id}`);
    const data = await response.json();
    
    let html = `
        <p><strong>Folio:</strong> ${data.folio}</p>
        <p><strong>Estado:</strong> ${data.estado}</p>
        <p><strong>Departamento:</strong> ${data.departamento}</p>
        <p><strong>Justificación:</strong> ${data.justificacion}</p>
        <p><strong>Fecha:</strong> ${new Date(data.created_at).toLocaleString('es-MX')}</p>
    `;
    
    if (data.approved_at) {
        html += `<p><strong>Aprobada:</strong> ${new Date(data.approved_at).toLocaleString('es-MX')}</p>`;
    }
    
    if (data.delivered_at) {
        html += `
            <p><strong>Entregada:</strong> ${new Date(data.delivered_at).toLocaleString('es-MX')}</p>
            <p><strong>Recibió:</strong> ${data.delivered_to}</p>
        `;
    }
    
    if (data.rejection_reason) {
        html += `<p><strong>Razón de rechazo:</strong> ${data.rejection_reason}</p>`;
    }
    
    html += '<h4>Items:</h4><ul>';
    data.items.forEach(item => {
        html += `<li>${item.cantidad} ${item.unidad} - ${item.descripcion}</li>`;
    });
    html += '</ul>';
    
    document.getElementById('modal-content').innerHTML = html;
    document.getElementById('modal-detalle').showModal();
}

function cerrarModal() {
    document.getElementById('modal-detalle').close();
}
</script>
{% endblock %}
```

### 12.4 templates/aprobar.html

```html
{% extends "base.html" %}

{% block title %}Aprobar Requisiciones{% endblock %}

{% block content %}
<article>
    <header>
        <h2>Requisiciones Pendientes de Aprobación</h2>
        <p>Departamento: {{ current_user.departamento }}</p>
    </header>
    
    {% if pendientes %}
    <figure>
        <table role="grid">
            <thead>
                <tr>
                    <th>Folio</th>
                    <th>Solicitante</th>
                    <th>Fecha</th>
                    <th>Justificación</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for req in pendientes %}
                <tr>
                    <td><strong>{{ req.folio }}</strong></td>
                    <td>{{ req.solicitante.nombre }}</td>
                    <td>{{ req.created_at.strftime('%d/%m/%Y %H:%M') }}</td>
                    <td>{{ req.justificacion[:50] }}...</td>
                    <td>
                        <button onclick="verParaAprobar({{ req.id }})" class="small">Ver y Decidir</button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </figure>
    {% else %}
    <p>No hay requisiciones pendientes de aprobación.</p>
    {% endif %}
</article>

<dialog id="modal-aprobar">
    <article>
        <header>
            <button aria-label="Close" rel="prev" onclick="cerrarModalAprobar()"></button>
            <h3>Revisar Requisición</h3>
        </header>
        <div id="modal-aprobar-content"></div>
        <footer>
            <div id="modal-aprobar-actions"></div>
        </footer>
    </article>
</dialog>
{% endblock %}

{% block scripts %}
<script>
let requisicionActual = null;

async function verParaAprobar(id) {
    const response = await fetch(`/api/requisiciones/${id}`);
    const data = await response.json();
    requisicionActual = id;
    
    let html = `
        <p><strong>Folio:</strong> ${data.folio}</p>
        <p><strong>Solicitante:</strong> ${data.solicitante.nombre}</p>
        <p><strong>Departamento:</strong> ${data.departamento}</p>
        <p><strong>Fecha:</strong> ${new Date(data.created_at).toLocaleString('es-MX')}</p>
        <p><strong>Justificación:</strong></p>
        <p>${data.justificacion}</p>
        <h4>Items Solicitados:</h4>
        <ul>
    `;
    
    data.items.forEach(item => {
        html += `<li><strong>${item.cantidad} ${item.unidad}</strong> - ${item.descripcion}</li>`;
    });
    
    html += '</ul>';
    
    document.getElementById('modal-aprobar-content').innerHTML = html;
    document.getElementById('modal-aprobar-actions').innerHTML = `
        <form method="POST" action="/aprobar/${id}" style="display: inline;">
            <button type="submit" class="success">✓ Aprobar</button>
        </form>
        <button onclick="mostrarFormRechazo()" class="secondary">✗ Rechazar</button>
        <div id="form-rechazo" style="display:none; margin-top: 1rem;">
            <form method="POST" action="/rechazar/${id}">
                <label>
                    Razón del rechazo:
                    <textarea name="razon" required rows="3" placeholder="Explica por qué se rechaza esta requisición..."></textarea>
                </label>
                <button type="submit">Confirmar Rechazo</button>
            </form>
        </div>
    `;
    
    document.getElementById('modal-aprobar').showModal();
}

function mostrarFormRechazo() {
    document.getElementById('form-rechazo').style.display = 'block';
}

function cerrarModalAprobar() {
    document.getElementById('modal-aprobar').close();
}
</script>
{% endblock %}
```

### 12.5 templates/bodega.html

```html
{% extends "base.html" %}

{% block title %}Bodega - Requisiciones{% endblock %}

{% block content %}
<article>
    <header>
        <h2>Requisiciones Aprobadas</h2>
        <p>Pendientes de preparar y entregar</p>
    </header>
    
    {% if aprobadas %}
    <figure>
        <table role="grid">
            <thead>
                <tr>
                    <th>Folio</th>
                    <th>Solicitante</th>
                    <th>Departamento</th>
                    <th>Fecha Aprobación</th>
                    <th>Acciones</th>
                </tr>
            </thead>
            <tbody>
                {% for req in aprobadas %}
                <tr>
                    <td><strong>{{ req.folio }}</strong></td>
                    <td>{{ req.solicitante.nombre }}</td>
                    <td>{{ req.departamento }}</td>
                    <td>{{ req.approved_at.strftime('%d/%m/%Y %H:%M') }}</td>
                    <td>
                        <button onclick="verParaEntregar({{ req.id }})" class="small">Ver y Entregar</button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </figure>
    {% else %}
    <p>No hay requisiciones aprobadas pendientes de entregar.</p>
    {% endif %}
</article>

<dialog id="modal-entregar">
    <article>
        <header>
            <button aria-label="Close" rel="prev" onclick="cerrarModalEntregar()"></button>
            <h3>Entregar Requisición</h3>
        </header>
        <div id="modal-entregar-content"></div>
        <footer>
            <div id="modal-entregar-form"></div>
        </footer>
    </article>
</dialog>
{% endblock %}

{% block scripts %}
<script>
async function verParaEntregar(id) {
    const response = await fetch(`/api/requisiciones/${id}`);
    const data = await response.json();
    
    let html = `
        <p><strong>Folio:</strong> ${data.folio}</p>
        <p><strong>Solicitante:</strong> ${data.solicitante.nombre}</p>
        <p><strong>Departamento:</strong> ${data.departamento}</p>
        <p><strong>Justificación:</strong> ${data.justificacion}</p>
        <h4>Items a Entregar:</h4>
        <ul>
    `;
    
    data.items.forEach(item => {
        html += `<li><strong>${item.cantidad} ${item.unidad}</strong> - ${item.descripcion}</li>`;
    });
    
    html += '</ul>';
    
    document.getElementById('modal-entregar-content').innerHTML = html;
    document.getElementById('modal-entregar-form').innerHTML = `
        <form method="POST" action="/entregar/${id}">
            <label>
                Nombre completo de quien recibe:
                <input type="text" name="receptor" required placeholder="Ej: Juan Pérez Gómez">
            </label>
            <button type="submit">✓ Marcar como Entregada</button>
        </form>
    `;
    
    document.getElementById('modal-entregar').showModal();
}

function cerrarModalEntregar() {
    document.getElementById('modal-entregar').close();
}
</script>
{% endblock %}
```

---

## 13. CONFIGURACIÓN Y DEPLOYMENT

### 13.1 app/database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./requisiciones.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """
    Dependency para obtener sesión de base de datos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 13.2 app/main.py (estructura principal)

```python
from fastapi import FastAPI, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .database import get_db, engine
from .models import Base, Requisicion, Item, Usuario
from .schemas import Requisicion as RequisicionSchema
from .auth import get_current_user, hash_password
from . import crud

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Requisiciones")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ==================== RUTAS HTML ====================

@app.get("/", response_class=HTMLResponse)
def home(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Página de inicio con resumen."""
    mis_requisiciones_count = db.query(Requisicion).filter(
        Requisicion.solicitante_id == current_user.id
    ).count()
    
    pendientes_aprobar_count = 0
    if current_user.rol in ['aprobador', 'admin']:
        pendientes_aprobar_count = db.query(Requisicion).filter(
            Requisicion.estado == 'pendiente',
            Requisicion.departamento == current_user.departamento
        ).count()
    
    pendientes_bodega_count = 0
    if current_user.rol in ['bodega', 'admin']:
        pendientes_bodega_count = db.query(Requisicion).filter(
            Requisicion.estado == 'aprobada'
        ).count()
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "current_user": current_user,
        "mis_requisiciones": mis_requisiciones_count,
        "pendientes_aprobar": pendientes_aprobar_count,
        "pendientes_bodega": pendientes_bodega_count
    })

@app.get("/crear", response_class=HTMLResponse)
def form_crear_requisicion(
    request: Request,
    current_user: Usuario = Depends(get_current_user)
):
    """Formulario para crear nueva requisición."""
    if current_user.rol not in ['user', 'aprobador', 'admin']:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    return templates.TemplateResponse("crear_requisicion.html", {
        "request": request,
        "current_user": current_user
    })

@app.post("/crear")
async def crear_requisicion(
    request: Request,
    departamento: str = Form(...),
    justificacion: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Procesa la creación de una nueva requisición."""
    if current_user.rol not in ['user', 'aprobador', 'admin']:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    # Crear requisición
    req = crud.crear_requisicion(
        db=db,
        solicitante_id=current_user.id,
        departamento=departamento,
        justificacion=justificacion
    )
    
    # Procesar items del formulario
    form_data = await request.form()
    
    # Los items vienen como items[0][descripcion], items[0][cantidad], etc
    items_dict = {}
    for key, value in form_data.items():
        if key.startswith('items['):
            # Extraer índice y campo
            parts = key.split('[')
            idx = int(parts[1].rstrip(']'))
            campo = parts[2].rstrip(']')
            
            if idx not in items_dict:
                items_dict[idx] = {}
            items_dict[idx][campo] = value
    
    # Crear items
    for item_data in items_dict.values():
        crud.agregar_item(
            db=db,
            requisicion_id=req.id,
            descripcion=item_data['descripcion'],
            cantidad=float(item_data['cantidad']),
            unidad=item_data['unidad']
        )
    
    return RedirectResponse(
        url="/mis-requisiciones",
        status_code=303
    )

@app.get("/mis-requisiciones", response_class=HTMLResponse)
def mis_requisiciones(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista las requisiciones del usuario actual."""
    requisiciones = db.query(Requisicion).filter(
        Requisicion.solicitante_id == current_user.id
    ).order_by(Requisicion.created_at.desc()).all()
    
    return templates.TemplateResponse("mis_requisiciones.html", {
        "request": request,
        "current_user": current_user,
        "requisiciones": requisiciones
    })

@app.get("/aprobar", response_class=HTMLResponse)
def form_aprobar(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista requisiciones pendientes de aprobación."""
    if current_user.rol not in ['aprobador', 'admin']:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    query = db.query(Requisicion).filter(Requisicion.estado == 'pendiente')
    
    if current_user.rol == 'aprobador':
        query = query.filter(Requisicion.departamento == current_user.departamento)
    
    pendientes = query.order_by(Requisicion.created_at).all()
    
    return templates.TemplateResponse("aprobar.html", {
        "request": request,
        "current_user": current_user,
        "pendientes": pendientes
    })

@app.post("/aprobar/{req_id}")
def aprobar_requisicion(
    req_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Aprueba una requisición."""
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Requisición no encontrada")
    
    if not crud.puede_aprobar(req, current_user):
        raise HTTPException(status_code=403, detail="No autorizado")
    
    crud.aprobar_requisicion(db, req_id, current_user.id)
    
    return RedirectResponse(url="/aprobar", status_code=303)

@app.post("/rechazar/{req_id}")
def rechazar_requisicion(
    req_id: int,
    razon: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rechaza una requisición."""
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Requisición no encontrada")
    
    if not crud.puede_aprobar(req, current_user):
        raise HTTPException(status_code=403, detail="No autorizado")
    
    crud.rechazar_requisicion(db, req_id, razon)
    
    return RedirectResponse(url="/aprobar", status_code=303)

@app.get("/bodega", response_class=HTMLResponse)
def bodega_view(
    request: Request,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista requisiciones aprobadas para bodega."""
    if current_user.rol not in ['bodega', 'admin']:
        raise HTTPException(status_code=403, detail="No autorizado")
    
    aprobadas = db.query(Requisicion).filter(
        Requisicion.estado == 'aprobada'
    ).order_by(Requisicion.approved_at).all()
    
    return templates.TemplateResponse("bodega.html", {
        "request": request,
        "current_user": current_user,
        "aprobadas": aprobadas
    })

@app.post("/entregar/{req_id}")
def entregar_requisicion(
    req_id: int,
    receptor: str = Form(...),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Marca una requisición como entregada."""
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Requisición no encontrada")
    
    if not crud.puede_entregar(req, current_user):
        raise HTTPException(status_code=403, detail="No autorizado")
    
    crud.entregar_requisicion(db, req_id, current_user.id, receptor)
    
    return RedirectResponse(url="/bodega", status_code=303)

@app.get("/logout")
def logout():
    """Cierra sesión."""
    return RedirectResponse(url="/", status_code=303)

# ==================== API JSON ====================

@app.get("/api/requisiciones/{req_id}", response_model=RequisicionSchema)
def get_requisicion_api(
    req_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene detalle de una requisición en formato JSON."""
    req = db.query(Requisicion).filter(Requisicion.id == req_id).first()
    
    if not req:
        raise HTTPException(status_code=404, detail="Requisición no encontrada")
    
    if not crud.puede_ver_requisicion(req, current_user):
        raise HTTPException(status_code=403, detail="No autorizado")
    
    return req

@app.get("/health")
def health_check():
    """Health check para monitoreo."""
    return {"status": "ok"}
```

### 13.3 .env

```bash
# Base de datos
DATABASE_URL=sqlite:///./requisiciones.db

# Seguridad
SECRET_KEY=cambiar-en-produccion-por-algo-aleatorio-y-seguro

# Aplicación
APP_NAME=Sistema de Requisiciones
DEBUG=False
```

### 13.4 requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
jinja2==3.1.2
bcrypt==4.1.2
python-dotenv==1.0.0
```

### 13.5 init_db.py

```python
"""
Script para inicializar la base de datos con usuarios de prueba.

Ejecutar: python init_db.py
"""

from app.database import engine, SessionLocal
from app.models import Base, Usuario
from app.auth import hash_password

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

# Crear sesión
db = SessionLocal()

# Verificar si ya hay usuarios
usuarios_existentes = db.query(Usuario).count()

if usuarios_existentes > 0:
    print(f"⚠️  Ya existen {usuarios_existentes} usuarios en la base de datos.")
    respuesta = input("¿Deseas crear usuarios de prueba de todas formas? (s/n): ")
    if respuesta.lower() != 's':
        print("Operación cancelada.")
        db.close()
        exit()

# Crear usuarios de prueba
usuarios = [
    Usuario(
        username="admin",
        password=hash_password("admin123"),
        nombre="Administrador",
        rol="admin",
        departamento="TI"
    ),
    Usuario(
        username="juan.perez",
        password=hash_password("password"),
        nombre="Juan Pérez",
        rol="user",
        departamento="Operaciones"
    ),
    Usuario(
        username="maria.lopez",
        password=hash_password("password"),
        nombre="María López",
        rol="user",
        departamento="Ventas"
    ),
    Usuario(
        username="carlos.rodriguez",
        password=hash_password("password"),
        nombre="Carlos Rodríguez",
        rol="aprobador",
        departamento="Operaciones"
    ),
    Usuario(
        username="ana.martinez",
        password=hash_password("password"),
        nombre="Ana Martínez",
        rol="aprobador",
        departamento="Ventas"
    ),
    Usuario(
        username="jose.bodega",
        password=hash_password("password"),
        nombre="José Ramírez",
        rol="bodega",
        departamento="Bodega"
    )
]

for usuario in usuarios:
    # Verificar si el usuario ya existe
    existe = db.query(Usuario).filter(Usuario.username == usuario.username).first()
    if not existe:
        db.add(usuario)
        print(f"✓ Usuario creado: {usuario.username} ({usuario.rol})")
    else:
        print(f"⊘ Usuario ya existe: {usuario.username}")

db.commit()
db.close()

print("\n✅ Base de datos inicializada correctamente")
print("\n📋 Usuarios de prueba:")
print("   admin / admin123 (Administrador)")
print("   juan.perez / password (Usuario - Operaciones)")
print("   maria.lopez / password (Usuario - Ventas)")
print("   carlos.rodriguez / password (Aprobador - Operaciones)")
print("   ana.martinez / password (Aprobador - Ventas)")
print("   jose.bodega / password (Bodega)")
```

### 13.6 static/style.css

```css
/* Estilos personalizados */

:root {
    --pico-font-family: system-ui, -apple-system, "Segoe UI", "Roboto", sans-serif;
}

.badge-warning {
    background-color: #ffc107;
    color: #000;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-weight: 600;
}

.badge-success {
    background-color: #28a745;
    color: #fff;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-weight: 600;
}

.badge-error {
    background-color: #dc3545;
    color: #fff;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-weight: 600;
}

.badge-info {
    background-color: #17a2b8;
    color: #fff;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.875rem;
    font-weight: 600;
}

.item-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr auto;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
}

button.small {
    padding: 0.25rem 0.5rem;
    font-size: 0.875rem;
}

.alert {
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 0.25rem;
    border: 1px solid;
}

.alert-success {
    background-color: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
}

.alert-error {
    background-color: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
}

.alert-warning {
    background-color: #fff3cd;
    border-color: #ffeeba;
    color: #856404;
}
```

### 13.7 static/app.js

```javascript
// Funciones globales de JavaScript

// Función para formatear fechas
function formatearFecha(fecha) {
    const d = new Date(fecha);
    return d.toLocaleString('es-MX', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Auto-cerrar alertas después de 5 segundos
document.addEventListener('DOMContentLoaded', function() {
    const alertas = document.querySelectorAll('.alert');
    alertas.forEach(alerta => {
        setTimeout(() => {
            alerta.style.transition = 'opacity 0.5s';
            alerta.style.opacity = '0';
            setTimeout(() => alerta.remove(), 500);
        }, 5000);
    });
});
```

---

## 14. COMANDOS DE DEPLOYMENT

### 14.1 Instalación

```bash
# Clonar o crear proyecto
mkdir requisiciones-system
cd requisiciones-system

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
python init_db.py

# Correr aplicación
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 14.2 Acceso desde LAN

```bash
# Encontrar IP local
# Linux:
ip addr show | grep inet

# El sistema estará disponible en:
http://192.168.1.XXX:8000

# Usuarios de prueba:
# admin / admin123
# juan.perez / password
# carlos.rodriguez / password (aprobador)
# jose.bodega / password (bodega)
```

### 14.3 Backups

```bash
# Backup manual
cp requisiciones.db requisiciones_backup_$(date +%Y%m%d).db

# Script de backup diario (agregar a crontab)
0 2 * * * cp /ruta/requisiciones.db /ruta/backups/requisiciones_$(date +\%Y\%m\%d).db
```

---

## 15. TESTING BÁSICO

### 15.1 Pruebas Manuales

**Checklist de funcionalidad:**

- [ ] Login con diferentes usuarios
- [ ] Crear requisición con múltiples items
- [ ] Ver mis requisiciones
- [ ] Aprobar requisición (como aprobador)
- [ ] Rechazar requisición con razón
- [ ] Entregar requisición (como bodega)
- [ ] Verificar permisos (usuario normal no puede aprobar)
- [ ] Verificar trazabilidad (fechas, nombres)

---

## 16. ROADMAP DE DESARROLLO

### Semana 1
**Días 1-2: Fundamentos**
- [ ] Setup proyecto y estructura de directorios
- [ ] Configurar base de datos SQLite
- [ ] Crear modelos SQLAlchemy
- [ ] Script init_db.py

**Días 3-4: Backend**
- [ ] Implementar autenticación
- [ ] Crear operaciones CRUD
- [ ] Endpoints API básicos
- [ ] Testing con Postman/curl

**Día 5: Frontend Base**
- [ ] Templates base y login
- [ ] Formulario crear requisición
- [ ] Vista mis requisiciones

### Semana 2
**Días 1-2: Flujo de Aprobación**
- [ ] Vista aprobar requisiciones
- [ ] Implementar aprobación/rechazo
- [ ] Validaciones de permisos

**Día 3: Bodega**
- [ ] Vista bodega
- [ ] Implementar entrega
- [ ] Modal de detalles

**Día 4: Refinamiento**
- [ ] CSS personalizado
- [ ] JavaScript para interactividad
- [ ] Testing manual completo
- [ ] Fixes de bugs

**Día 5: Deployment**
- [ ] Deploy en servidor LAN
- [ ] Documentación de usuario
- [ ] Capacitación usuarios piloto
- [ ] Monitoreo primeras requisiciones

---

## 17. PROMPTS PARA LLMs

### 17.1 Prompt Inicial para Desarrollo

```
Estoy desarrollando un sistema de requisiciones siguiendo esta especificación técnica.

STACK:
- FastAPI + SQLAlchemy + SQLite
- Jinja2 + PicoCSS + Vanilla JS
- HTTP Basic Auth

CONTEXTO:
Ver sección [número] de la documentación técnica: [nombre de sección]

TAREA:
[Descripción específica de lo que necesitas]

REQUISITOS:
- Seguir estructura de directorios establecida
- Respetar máquina de estados (4 estados)
- Validar permisos según rol
- Código en español (comentarios y docstrings)
- Type hints en funciones

ENTREGABLES:
- Código funcional
- Comentarios explicativos
- Código probado
```

### 17.2 Prompt para Debugging

```
PROBLEMA:
[Descripción del error]

CONTEXTO:
- Archivo: [nombre de archivo]
- Función: [nombre de función]
- Error: [mensaje de error o traceback]

DOCUMENTACIÓN RELEVANTE:
Ver sección [número]: [tema]

VERIFICAR:
- Permisos según tabla de PERMISOS
- Transición válida según ESTADO_TRANSICIONES
- Relaciones SQLAlchemy correctas
```

### 17.3 Prompt para Nuevas Features

```
NUEVA FUNCIONALIDAD:
[Descripción de la feature]

ARQUITECTURA ACTUAL:
Ver documento de especificación técnica completo

REQUISITOS:
- Mantener consistencia con patrones existentes
- No romper funcionalidad actual
- Seguir convenciones de nombres
- Actualizar documentación si es necesario

ARCHIVOS A MODIFICAR:
[Lista de archivos que probablemente necesiten cambios]
```

---

## 18. GLOSARIO Y CONVENCIONES

### 18.1 Nomenclatura

```python
# Variables y funciones: snake_case
requisicion_activa = True
def crear_requisicion():
    pass

# Clases: PascalCase
class Requisicion:
    pass

# Constantes: UPPER_SNAKE_CASE
ESTADO_PENDIENTE = "pendiente"

# Templates HTML: snake_case.html
crear_requisicion.html
mis_requisiciones.html
```

### 18.2 Comentarios

Todos los comentarios y docstrings en español:

```python
def aprobar_requisicion(req_id: int, user: Usuario, db: Session) -> Requisicion:
    """
    Aprueba una requisición si el usuario tiene permisos.
    
    Args:
        req_id: ID de la requisición
        user: Usuario que aprueba
        db: Sesión de base de datos
        
    Returns:
        Requisicion actualizada
        
    Raises:
        HTTPException: Si no tiene permisos o estado inválido
    """
    pass
```

---

## 19. CHECKLIST DE PRODUCCIÓN

**Antes de desplegar:**
- [ ] Cambiar SECRET_KEY en .env (generar uno aleatorio)
- [ ] Eliminar usuarios de prueba y crear usuarios reales
- [ ] Configurar firewall (permitir solo IPs de LAN)
- [ ] Hacer backup inicial vacío
- [ ] Documentar credenciales de admin en lugar seguro
- [ ] Preparar guía rápida de usuario (1 página)
- [ ] Capacitar a 2-3 usuarios piloto

**Primera semana:**
- [ ] Monitorear logs diariamente
- [ ] Backup manual diario
- [ ] Recopilar feedback de usuarios
- [ ] Documentar problemas y soluciones
- [ ] Estar disponible para soporte

**Mantenimiento continuo:**
- [ ] Backup semanal
- [ ] Revisar logs de errores
- [ ] Atender solicitudes de usuarios
- [ ] Documentar mejoras sugeridas

---

**DOCUMENTO VIVO**  
**Última actualización:** 2025-02-10  
**Versión:** 1.0  
**Propósito:** Especificación técnica completa para desarrollo del sistema de requisiciones
