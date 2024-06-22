import os
import sys
os.chdir('FlapPyBird')
import Bird

times = sys.argv[1:]
times = [float(time) for time in times]

bird = Bird.Bird()
bird.wait_times = times
bird.simulate()
