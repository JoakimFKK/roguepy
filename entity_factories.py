from entity import Actor
from components.ai import HostileEnemy
from components.fighter import Fighter


player = Actor(
	char='@',
	color=(255, 255, 255),
	name='Player',
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=30, defense=2, power=5),
)


orc = Actor(
	char='o',
	color=(88, 220, 86),
	name='Orc',
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=10, defense=0, power=3),
)

troll = Actor(
	char='T',
	color=(0, 255, 255),
	name='Troll',
	ai_cls=HostileEnemy,
	fighter=Fighter(hp=16, defense=1, power=4),
)