from gopro_overlay.models import KineticEnergyModel
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets import Composite, simple_icon, CachingText, Translate


class BigMetric:

    def __init__(self, at, title, value, font_title, font_metric=None):
        self.widget = Translate(
            at,
            Composite(
                CachingText(Coordinate(0, 0), title, font_title),
                CachingText(Coordinate(0, 0), value, font_metric),
            )
        )

    def draw(self, image, draw):
        self.widget.draw(image, draw)


class ComparativeEnergy:

    def __init__(self, at, font, speed, person, bike, car, van):
        font = font.font_variant(size=48)
        small_font = font.font_variant(size=24)

        multiplier_colour = (255, 91, 78)
        mass_colour = (185, 185, 185)

        person_model = KineticEnergyModel(person)
        bike_model = KineticEnergyModel(person + bike)
        car_model = KineticEnergyModel(person + car)
        van_model = KineticEnergyModel(person + van)

        def model_output(model):
            v = speed()
            if v:
                kJ = model.evaluate(v).magnitude / 1000.0
                if kJ > 10:
                    return f"{kJ :,.0f} kJ"
                else:
                    return f"{kJ :,.1f} kJ"
            else:
                return "-"

        def mass(thing):
            return f"{thing.to('kg').m:,} kg"

        def thing(icon, thing, thing_model):
            multiplier = f"{(thing / person).m:,.1f}x"
            return Composite(
                simple_icon(Coordinate(230, 0), icon, invert=True),
                CachingText(Coordinate(230 + 32, 70), lambda: mass(thing), small_font, fill=mass_colour,
                            align="centre"),
                CachingText(Coordinate(200, 55), lambda: multiplier, small_font, align="right",
                            fill=multiplier_colour),
                CachingText(Coordinate(200, 5), lambda: model_output(thing_model), font, align="right"),
            )

        self.widget = Composite(
            Translate(at + Coordinate(0, 0), thing("user.png", person, person_model)),
            Translate(at + Coordinate(300, 0), thing("bicycle.png", bike + person, bike_model)),
            Translate(at + Coordinate(600, 0), thing("car.png", car + person, car_model)),
            Translate(at + Coordinate(900, 0), thing("van-black-side-view.png", van + person, van_model)),
        )

    def draw(self, image, draw):
        self.widget.draw(image, draw)
