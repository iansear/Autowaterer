loaded_pumps = {}


def stop_all_pumps():
    for pump in list(loaded_pumps.values()):
        pump.interrupt()
        if pump.is_running():
            pump.turn_off()
