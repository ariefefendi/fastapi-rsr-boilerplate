from app.models.units import Units
from app.repositories.base import BaseRepository


class UnitsRepository(BaseRepository[Units]):
    model = Units
    search_fields = ("code", "name", "description")

    # Tambahkan query khusus Units di sini bila diperlukan.
