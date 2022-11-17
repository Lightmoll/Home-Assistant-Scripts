![brightness_gauge](https://i.imgur.com/K0cpKqK.png)

# What?
The script provides a global_brightness variable, which can be controlled
via the HA-UI or a remote, to simultaniously dim many lights using user-defined
functions for e.g. brightness, color temprature and more.

This allows to e.g. firstly start ramping up ambient lights, before using
the main lights with one handy variable.
# How?
**Setup:**
To use the script you need to create a number Helper in Home Assistant called `global_dimming`.
You may then create any light effects using the `brightness` and `transition` variable.
To use with a remote, like the [IKEA Tradfri Switch](https://www.zigbee2mqtt.io/devices/E1743.html), add your
remote to the `REMOTE_IDS` array. You may add multiple remotes.

**Configuration:** 
You may change all capitalized variables (constants) in the script to suit your needs.
