from gopro_overlay.gpmd import GPSFix


class GPSLock:

    def __init__(self, fix, lock_no, lock_unknown, lock_2d, lock_3d):
        self.w = {
            GPSFix.UNKNOWN.value: lock_unknown,
            GPSFix.NO.value: lock_no,
            GPSFix.LOCK_2D.value: lock_2d,
            GPSFix.LOCK_3D.value: lock_3d,
        }
        self.fix = fix

    def draw(self, image, draw):
        self.w[self.fix()].draw(image, draw)
