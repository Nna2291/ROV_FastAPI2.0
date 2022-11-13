def get_tds(potValue):
    voltageSensor = potValue * 3.3 / 4096
    tdsSensor = (133.42 * pow(voltageSensor, 3) - 255.86 * pow(voltageSensor,
                                                               2) + 857.39 * voltageSensor) * 0.5
    return round(tdsSensor, 2)


def command_engine(ap, wp, id, speed, config, reverse):
    engine = config['engines'][str(id)]
    wp.digitalWrite(engine['1'], False)
    wp.digitalWrite(engine['2'], True)
    if reverse:
        wp.digitalWrite(engine['1'], True)
        wp.digitalWrite(engine['2'], False)
    ap.analogWrite(engine['pwm'], speed)
