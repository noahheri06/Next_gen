C = 3e8

B = 200e6
T = 0.1e-3
F_CARRIER = 2e9
F_SAMPLE = 500e6

FRAME_LENGTH = 25.6e-3


def task1():
    SamplesPerChirp = T*F_SAMPLE
    print(f"The amount of samples per chirp is {SamplesPerChirp}")

    TBetweenSamples = 1/F_SAMPLE
    print(f"The time between each sample is {TBetweenSamples}")

    ChirpsInFrame = FRAME_LENGTH/T
    print(f"The amount of chirps in one frame is {ChirpsInFrame}")


