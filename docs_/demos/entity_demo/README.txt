Presentation Notes for (Entity Demo):

This presentation is used to demonstrate the entity abilities.

- show player entity which is a special entity of the base type Avatar

- show controlled entity:

In python console:
>>> $p.spawn( "Platform" )
will spawn a platform at the players position
>>> $B.entities.values()
pick the plaform and assing to platform
>>> $p.capturePlatform( platform )
will capture the platform and make it controllable. Now you can move it via the arrow keys and PgUp/PgDn.
>>> $p.releasePlatform()
will release the control on the platform

- show server controlled entities

In python console:
>>> $p.spawnAll("Avatar", 20, 50.0)
will spawn 20 avatars around a 50 meter circle
>>> $p.moveAll( 50.0, 5.0)
will move all avatars around a 50 meter circle with velocity 5.0
>>> $p.stopAll()
will stop all avatars
>>> $p.killAll()
will remove all entities

- show filters

Press NUM1 key to toggle the different filters (AvatarFilter, AvatarDropFilter, DumpFilter)

- show filter visualisation

Press NUM2 key to toggle filter visualisation (visualisation of the filter error region)

ToDos:

- show physics visualisation
- fix filter visualisation to show filter steps