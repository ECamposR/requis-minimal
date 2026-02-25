from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False)
    departamento: Mapped[str] = mapped_column(String(80), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    requisiciones: Mapped[list["Requisicion"]] = relationship(
        "Requisicion",
        back_populates="solicitante",
        foreign_keys="Requisicion.solicitante_id",
    )
    aprobaciones_realizadas: Mapped[list["Requisicion"]] = relationship(
        "Requisicion",
        foreign_keys="Requisicion.approved_by",
        back_populates="aprobador",
    )
    rechazos_realizados: Mapped[list["Requisicion"]] = relationship(
        "Requisicion",
        foreign_keys="Requisicion.rejected_by",
        back_populates="rechazador",
    )
    entregas_realizadas: Mapped[list["Requisicion"]] = relationship(
        "Requisicion",
        foreign_keys="Requisicion.delivered_by",
        back_populates="entregador",
    )


class Requisicion(Base):
    __tablename__ = "requisiciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    folio: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    departamento: Mapped[str] = mapped_column(String(80), nullable=False)
    cliente_codigo: Mapped[str | None] = mapped_column(String(40), nullable=True)
    cliente_nombre: Mapped[str | None] = mapped_column(String(160), nullable=True)
    cliente_ruta_principal: Mapped[str | None] = mapped_column(String(4), nullable=True)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)
    justificacion: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())
    approved_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    approval_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivered_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    delivered_by: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    delivered_to: Mapped[str | None] = mapped_column(String(120), nullable=True)
    delivery_result: Mapped[str | None] = mapped_column(String(20), nullable=True)
    delivery_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    prokey_ref: Mapped[str | None] = mapped_column(String, nullable=True)
    liquidation_comment: Mapped[str | None] = mapped_column(String, nullable=True)
    liquidated_by: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    liquidated_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    rejected_at: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    rejected_by: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    solicitante: Mapped["Usuario"] = relationship(
        "Usuario",
        back_populates="requisiciones",
        foreign_keys=[solicitante_id],
    )
    aprobador: Mapped["Usuario | None"] = relationship(
        "Usuario",
        foreign_keys=[approved_by],
        back_populates="aprobaciones_realizadas",
    )
    rechazador: Mapped["Usuario | None"] = relationship(
        "Usuario",
        foreign_keys=[rejected_by],
        back_populates="rechazos_realizados",
    )
    entregador: Mapped["Usuario | None"] = relationship(
        "Usuario",
        foreign_keys=[delivered_by],
        back_populates="entregas_realizadas",
    )
    liquidator: Mapped["Usuario | None"] = relationship(
        "Usuario",
        foreign_keys=[liquidated_by],
    )
    items: Mapped[list["Item"]] = relationship(
        "Item",
        back_populates="requisicion",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "estado in ('pendiente', 'aprobada', 'rechazada', 'entregada', 'liquidada')",
            name="ck_requisiciones_estado",
        ),
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    requisicion_id: Mapped[int] = mapped_column(
        ForeignKey("requisiciones.id", ondelete="CASCADE"),
        nullable=False,
    )
    descripcion: Mapped[str] = mapped_column(Text, nullable=False)
    cantidad: Mapped[float] = mapped_column(Float, nullable=False)
    cantidad_entregada: Mapped[float | None] = mapped_column(Float, nullable=True)
    qty_returned_to_warehouse: Mapped[int | None] = mapped_column(Integer, nullable=True)
    qty_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    qty_left_at_client: Mapped[int | None] = mapped_column(Integer, nullable=True)
    item_liquidation_note: Mapped[str | None] = mapped_column(String, nullable=True)
    liquidation_alerts: Mapped[str | None] = mapped_column(String, nullable=True)
    unidad: Mapped[str] = mapped_column(String(40), nullable=False)

    requisicion: Mapped["Requisicion"] = relationship("Requisicion", back_populates="items")

    __table_args__ = (CheckConstraint("cantidad > 0", name="ck_items_cantidad_positive"),)


class CatalogoItem(Base):
    __tablename__ = "catalogo_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nombre: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
