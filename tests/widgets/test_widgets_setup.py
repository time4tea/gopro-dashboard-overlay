import random
from datetime import timedelta

from gopro_overlay import fake
from tests.font import load_test_font

font = load_test_font().font_variant(size=18)
title_font = font.font_variant(size=16)

# Need reproducible results for approval tests
rng = random.Random()
rng.seed(12345)

ts = fake.fake_framemeta(timedelta(minutes=10), step=timedelta(seconds=1), rng=rng)
