from custom_components.vmi_ventilairsec import get_device_specs


def test_device_specs_cover_vmi_devices_and_entities():
    devices = get_device_specs()

    assert len(devices) == 4

    names = {device["name"] for device in devices}
    assert "CO2 Sensor" in names
    assert "Temperature/Humidity Sensor" in names
    assert "VMI Purevent" in names
    assert "VMI Assistant Ventilairsec" in names

    purevent = next(device for device in devices if device["name"] == "VMI Purevent")
    assert any(sensor["key"] == "mode" for sensor in purevent["sensors"])
    assert any(select["key"] == "mode" for select in purevent["selects"])
    assert any(number["key"] == "heating_setpoint" for number in purevent["numbers"])
