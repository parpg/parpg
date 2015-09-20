from fife.extensions import pychan

from .inventorygui import EquipmentSlot, InventoryGrid
from .spinners import Spinner, IntSpinner
from .tabwidget import TabWidget

pychan.registerWidget(EquipmentSlot)
pychan.registerWidget(InventoryGrid)
pychan.registerWidget(Spinner)
pychan.registerWidget(IntSpinner)
pychan.registerWidget(TabWidget)