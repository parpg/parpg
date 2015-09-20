from character_statistics import CharacterStatistics
from containable import Containable
from container import Container
from description import Description
from dialogue import Dialogue
from fifeagent import FifeAgent
from lockable import Lockable
from usable import Usable
from change_map import ChangeMap
from equipable import Equipable
from equip import Equip
from general import General
from behaviour import Behaviour
from graphics import Graphics

components = {
        "general": General(),
        "characterstats": CharacterStatistics(),
        "containable": Containable(),
        "container": Container(),
        "description": Description(),
        "dialogue": Dialogue(),
        "fifeagent": FifeAgent(),
        "lockable": Lockable(),
        "usable": Usable(),
        "change_map": ChangeMap(),
        "equipable": Equipable(),
        "equip": Equip(),
        "behaviour": Behaviour(),
        "graphics": Graphics(),
    }