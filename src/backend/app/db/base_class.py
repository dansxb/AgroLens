"""SQLAlchemy declarative base with automatic table name derivation.

All ORM models should inherit from :class:`Base` defined here.
The ``__tablename__`` is automatically set to the snake_case version
of the class name (e.g. ``UserProfile`` → ``user_profiles``).
"""

from __future__ import annotations

import re

from sqlalchemy.orm import DeclarativeBase, declared_attr


def _to_snake_case(name: str) -> str:
    """Convert a CamelCase class name to snake_case table name.

    Appends a trailing ``s`` to pluralise the table name by convention.

    Args:
        name: CamelCase class name (e.g. ``SatelliteScene``).

    Returns:
        Pluralised snake_case string (e.g. ``satellite_scenes``).

    Examples:
        >>> _to_snake_case("User")
        'users'
        >>> _to_snake_case("SatelliteScene")
        'satellite_scenes'
        >>> _to_snake_case("VegetationIndex")
        'vegetation_indices'
    """
    # Insert underscore before each uppercase letter that follows a lowercase
    # letter or another uppercase letter followed by a lowercase letter.
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    # Naive pluralisation: handle common special cases
    if snake.endswith("_index"):
        return snake[:-6] + "_indices"
    if snake.endswith("_y"):
        return snake[:-2] + "ies"
    if snake.endswith(("s", "x", "z", "ch", "sh")):
        return snake + "es"
    return snake + "s"


class Base(DeclarativeBase):
    """Abstract declarative base for all AgroLens ORM models.

    Subclasses automatically receive a ``__tablename__`` derived from
    their class name in snake_case + pluralised.  Individual models may
    override ``__tablename__`` if the convention does not apply.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa: N805
        """Derive the table name automatically from the class name."""
        return _to_snake_case(cls.__name__)

    def __repr__(self) -> str:
        """Return a minimal string representation useful for debugging."""
        pk_cols = [
            col.name
            for col in self.__table__.columns  # type: ignore[attr-defined]
            if col.primary_key
        ]
        pk_values = {col: getattr(self, col, None) for col in pk_cols}
        return f"<{self.__class__.__name__} {pk_values}>"
