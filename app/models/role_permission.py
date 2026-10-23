class RolePermission(SharedBase):
    __tablename__ = "role_permissions"
    role_id: Mapped[int] = mapped_column(
        ForeignKey("shared.roles.id"), primary_key=True
    )
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("shared.permissions.id"), primary_key=True
    )
