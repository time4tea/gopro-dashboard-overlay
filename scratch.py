from time import sleep

from overlayer import PoorTimer

if __name__ == "__main__":
    t = PoorTimer()

    t.time(lambda: sleep(1))

    print(f"Took {t.seconds()} seconds")
