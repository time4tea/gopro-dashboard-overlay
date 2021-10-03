import inspect
import sys
from functools import wraps
from pathlib import Path

from PIL import ImageChops, Image, ImageStat


def approve_image(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        function_name = f.__name__
        sourcefile = Path(inspect.getfile(f))

        approval_dir = sourcefile.parents[0].joinpath("approvals")

        approval_stem = f"{sourcefile.stem}_{function_name.replace('test_', '')}"
        approved_location = approval_dir.joinpath(f"{approval_stem}.approved.png")
        actual_location = approval_dir.joinpath(f"{approval_stem}.actual.png")
        diff_location = approval_dir.joinpath(f"{approval_stem}.diff.png")

        actual_image = f(*args, **kwargs)

        if actual_image is None:
            raise AssertionError(f"{function_name} needs to return the image it created")

        actual_image.save(actual_location, "PNG")
        if approved_location.exists():
            approved_image = Image.open(approved_location)
            difference = ImageChops.difference(actual_image, approved_image)
            total_difference = sum(ImageStat.Stat(difference).sum)
            diff_location.unlink(missing_ok=True)
            if total_difference > 0.0:
                difference.save(diff_location, "PNG")
                print(f"{function_name}: failed approval", file=sys.stderr)
                print(f"Approved {approved_location}", file=sys.stderr)
                print(f"Actual {actual_location}", file=sys.stderr)
                print(f"Diff {diff_location}", file=sys.stderr)
                print(f"If this is OK....", file=sys.stderr)
                print(f"cp {actual_location} {approved_location}", file=sys.stderr)
                raise AssertionError("Actual and Approved do not match")
        else:
            print(f"{function_name}: approved File does not exist, no assertion", file=sys.stderr)
            print(f"cp {actual_location} {approved_location}", file=sys.stderr)

    return wrapper
