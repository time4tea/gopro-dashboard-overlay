import itertools

from gopro_overlay.models import KineticEnergyModel
from gopro_overlay.point import Coordinate
from gopro_overlay.widgets import Composite, Text, simple_icon


class BigMetric:

    def __init__(self, at, title, value, font):
        self.widget = Composite(
            Text(at + Coordinate(0, 0), title, font),
            Text(at + Coordinate(0, 0), value, font.font_variant(size=160)),
        )

    def draw(self, image, draw):
        self.widget.draw(image, draw)


class RightInfoPanel:

    def __init__(self, at, icon, title, value, title_font, value_font):
        self.value = value
        self.widget = Composite(
            Text(at + Coordinate(-70, 0), title, title_font, align="right"),
            simple_icon(at + Coordinate(-64, 0), icon),
            Text(at + Coordinate(-70, 18), value, value_font, align="right"),
        )

    def draw(self, image, draw):
        self.widget.draw(image, draw)


class LeftInfoPanel:

    def __init__(self, at, icon, title, value, title_font, value_font):
        self.value = value
        self.widget = Composite(
            Text(at + Coordinate(70, 0), title, title_font),
            simple_icon(at + Coordinate(0, 0), icon),
            Text(at + Coordinate(70, 18), value, value_font),
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

        def thing(at, icon, thing, thing_model):
            multiplier = f"{ (thing / person).m:,.1f}x"
            return [
                simple_icon(at + Coordinate(230, 0), icon),
                Text(at + Coordinate(230 + 32, 70), lambda: mass(thing), small_font, fill=mass_colour, align="centre"),
                Text(at + Coordinate(200, 55), lambda: multiplier, small_font, align="right",
                     fill=multiplier_colour),
                Text(at + Coordinate(200, 5), lambda: model_output(thing_model), font, align="right"),
            ]

        self.widget = Composite(
            *itertools.chain(
                thing(at, "user.png", person, person_model),
                thing(at + Coordinate(300, 0), "bicycle.png", bike + person, bike_model),
                thing(at + Coordinate(600, 0), "car.png", car + person, car_model),
                thing(at + Coordinate(900, 0), "van-black-side-view.png", van + person, van_model),
            )
        )

    def draw(self, image, draw):
        self.widget.draw(image, draw)
