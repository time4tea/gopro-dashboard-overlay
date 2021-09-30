from gopro_overlay.models import KineticEnergyModel
from gopro_overlay.units import units


def test_kinetic():
    speed = units.Quantity(15, units.mps)

    mass = units.Quantity(10, units.kg)
    model = KineticEnergyModel(mass)

    result = model.evaluate(speed)

    assert result == units.Quantity(1125, units.joules)
