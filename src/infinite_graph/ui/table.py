"""Table models used by the Qt GUI."""

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt


class ListTableModel(QAbstractTableModel):
    def __init__(self, headers: list[str], rows: list[list[object]] | None = None) -> None:
        super().__init__()
        self.headers = headers
        self.rows = rows or []

    def update_rows(self, rows: list[list[object]]) -> None:
        self.beginResetModel()
        self.rows = rows
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.rows)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return 0 if parent.isValid() else len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> object:
        if not index.isValid() or role != Qt.DisplayRole:
            return None
        return str(self.rows[index.row()][index.column()])

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.DisplayRole
    ) -> object:
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return self.headers[section]
        return str(section + 1)


class ContainsFilterProxyModel(QSortFilterProxyModel):
    """Case-insensitive substring filter across all table columns."""

    def __init__(self) -> None:
        super().__init__()
        self._filter_text = ""

    def set_filter_text(self, text: str) -> None:
        self._filter_text = text.strip().casefold()
        self.beginFilterChange()
        self.endFilterChange()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self._filter_text:
            return True

        source_model = self.sourceModel()
        if source_model is None:
            return True

        for column in range(source_model.columnCount(source_parent)):
            index = source_model.index(source_row, column, source_parent)
            value = source_model.data(index, Qt.DisplayRole)
            if value is not None and self._filter_text in str(value).casefold():
                return True
        return False
