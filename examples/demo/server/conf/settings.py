r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "demo"


######################################################################
# evennia-survival
######################################################################

INSTALLED_APPS += ["evennia_survival"]

# The stages for each meter. Both required — there is no stage list the
# library could invent. They live under `libraries/` in this gamedir purely
# because that keeps consumer-declared config in one place; the library reads
# a module path and has no opinion about the layout.
#
# The folder name has to be a valid Python identifier, since the setting is a
# dotted path: `survival_service`, not `survival-service`.
SURVIVAL_HUNGER_STAGES = "libraries.survival_service.stages.HungerStage"
SURVIVAL_THIRST_STAGES = "libraries.survival_service.stages.ThirstStage"

# Deliberately fast, so a meter can be watched moving rather than waited on.
# A real game would use minutes and tens of minutes.
SURVIVAL_METER_INTERVAL = 30
SURVIVAL_REGEN_INTERVAL = 10


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
