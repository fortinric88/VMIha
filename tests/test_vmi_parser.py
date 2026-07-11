from custom_components.vmi_ventilairsec.enocean_handler import parse_d1079_payload


def _set_bits(value: int, offset: int, size: int, n: int) -> int:
    mask = (1 << size) - 1
    return value | ((n & mask) << offset)


def test_parse_d1079_01_00_fields():
    bits = 0
    bits = _set_bits(bits, 4, 4, 0)
    bits = _set_bits(bits, 16, 8, 3)
    bits = _set_bits(bits, 26, 1, 1)
    bits = _set_bits(bits, 27, 1, 1)
    bits = _set_bits(bits, 28, 1, 0)
    bits = _set_bits(bits, 30, 1, 1)
    bits = _set_bits(bits, 31, 1, 0)
    bits = _set_bits(bits, 32, 8, 10)
    bits = _set_bits(bits, 40, 8, 20)
    bits = _set_bits(bits, 48, 8, 24)
    bits = _set_bits(bits, 56, 8, 28)

    payload = format(bits, "016x")
    result = parse_d1079_payload(payload, func="01", device_type="00")

    assert result["mode"] == "Confort"
    assert result["bypass"] is True
    assert result["time_slot_active"] is True
    assert result["boost_remaining"] == 10
    assert result["setpoint_electric"] == 20
    assert result["setpoint_hydror"] == 28


def test_parse_d1079_00_00_fields():
    bits = 0
    bits = _set_bits(bits, 16, 8, 4)
    bits = _set_bits(bits, 24, 16, 6100)
    bits = _set_bits(bits, 40, 8, 50)

    payload = format(bits, "016x")
    result = parse_d1079_payload(payload, func="00", device_type="00")

    assert result["battery_level"] == "Level 3"
    assert result["temperature"] == 21.0
    assert result["humidity"] == 50
