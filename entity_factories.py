from components.ai import HostileEnemy
from components import consumable

from components.fighter import Fighter
from components.inventory import Inventory
from entity import Actor, Item


player = Actor(
	char='@',
	color=(255, 255, 255),
	name='Player',
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=30, defense=2, power=5),
	inventory=Inventory(capacity=26),
)


orc = Actor(
	char='o',
	color=(88, 220, 86),
	name='Orc',
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=10, defense=0, power=3),
	inventory=Inventory(capacity=0),
)

troll = Actor(
	char='T',
	color=(0, 255, 255),
	name='Troll',
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=16, defense=1, power=4),
	inventory=Inventory(capacity=0),
)

health_potion = Item(
	char='!',
	color=(127, 0, 255),
	name="Harboe Sport",
	consumable=consumable.HealingConsumable(amount=4),
)

lightning_scroll = Item(
	char='~',
	color=(152, 60, 20),
	name="Bottled Ligtning",
	consumable=consumable.LightningDamageConsumable(damage=20, maximum_range=5),
)