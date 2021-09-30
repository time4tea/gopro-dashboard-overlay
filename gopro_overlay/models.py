from gopro_overlay.units import units


class KineticEnergyModel:

    def __init__(self, mass):
        self.mass = mass.to("kg").m

    def evaluate(self, speed):

        if speed is None:
            return None

        v = speed.to("mps").m

        return units.Quantity(0.5 * self.mass * (v ** 2), units.joules)


# Other models to investigate: https://arxiv.org/vc/arxiv/papers/0803/0803.2402v1.pdf
# http://www.tara.tcd.ie/bitstream/handle/2262/41170/Vehicle%20pedestrian%20collisions.pdf?sequence=1
# https://www.researchgate.net/publication/329075219_Mathematical_Model_for_Velocity_Calculation_of_three_types_of_Vehicles_in_case_of_pedestrian_Crash
# http://www.ircobi.org/wordpress/downloads/irc0111/2002/Session4/4.1.pdf
