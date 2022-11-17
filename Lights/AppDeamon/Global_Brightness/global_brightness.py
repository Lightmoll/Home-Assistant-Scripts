import time
import math
import hassapi as hass

BRIGHTNESS_VAR = "input_number.global_brightness"
REMOTE_IDS = ["sensor.REMOTE"]
S_PER_STEP = .08 #s
UPDATE_TIME = .1 #s
MIN_LAMP_TRANSITION_TIME = 1 #s


class HASSDimmer(hass.Hass):

    def initialize(self):
        self.global_brightness = 0
        self.last_change_time = time.time()
        self.last_transition_call = time.time()
        self.brightness_direction = 0
        remote_ids = REMOTE_IDS
        for remote_id in remote_ids:
            self.listen_state(self.remote_listener, remote_id)

        self.listen_state(
                self.brightness_changed,
                BRIGHTNESS_VAR,
                namespace="global"
            )


    def update_lights(self, brightness, transition):
        """ ! CHANGE ME !
        Here the user can supply their own functions to map the
        global brightness variable to their individual lights

        Args:
            brightness (_type_): global brightness in percent
            transition (_type_): transition time to be passed to every light
        """
        #EXAMPLE:
        def clamp(n, minn, maxn):
            return max(min(maxn, n), minn)

        #functions: https://www.desmos.com/calculator/zzylhbqqdy
        x = brightness
        main_bright = clamp( math.atan(x/16.2 - 4.5) * 130/math.pi + 45 , 0, 100)
        ambient_bright = clamp( math.atan(x/23.2 - 1.1) * 150/math.pi + 42 , 1, 100)

        #args in: https://www.home-assistant.io/integrations/light/#service-lightturn_on
        self.turn_on("light.deckenlampe", brightness_pct=round(main_bright), transition=transition)
        self.turn_on("light.dekolampe_rattan", brightness_pct=round(ambient_bright), transition=transition)
        self.turn_on("light.lampe_schreibtisch", brightness_pct=round(ambient_bright), transition=transition)


    def remote_listener(self, entity, attr, old, new, kwargs):
        """callback function on every change of the used remotes
        to calculate the new brightness function, if neccesary
        or to stop the brightness change

        Args:
            for args description, please see AppDeamon documentation
            for callback functions
        """
        directions = {
            "brightness_move_up": 1,
            "brightness_move_down": -1,
            "brightness_stop": 0
        }
        if new in directions:
            self.brightness_direction = directions[new]
            self.last_change_time = time.time()
            self.calc_brightness(None)


    def calc_brightness(self, _):
        """recursively called function to continuisly
        update the global brightness variable untill
        the direction variable is set to 0.

        Args:
            _ (kwargs): required arg by AppDeamon for run_in func
        """
        if self.brightness_direction != 0:
            self.run_in(self.calc_brightness, UPDATE_TIME) #run func in x seconds after func call
        self.global_brightness += (time.time() - self.last_change_time) * self.brightness_direction / S_PER_STEP
        self.set_brightness(self.global_brightness)
        self.last_change_time = time.time()


    def brightness_changed(self, entity, attr, old, new, kwargs):
        """callback function on every change of the hass
        variable for the global brightness

        Args:
            for args description, please see AppDeamon documentation
            for callback functions
        """
        self.global_brightness = float(new)
        if time.time() > self.last_transition_call + MIN_LAMP_TRANSITION_TIME:
            t = max(UPDATE_TIME, MIN_LAMP_TRANSITION_TIME)
            self.update_lights(self.global_brightness, t)
            self.last_transition_call = time.time()


    def set_brightness(self, brightness:int):
        """sets brightness to hass variable and checks
        if bounderies are in check

        Args:
            brightness (int): desired global brightness
        """
        b = max(min(100, brightness), 0) #clamp brightness to 0 ... 100
        self.set_value(BRIGHTNESS_VAR, round(b, 1))