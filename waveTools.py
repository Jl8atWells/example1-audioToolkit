'''
Tools for reading/writing .wav files built on top of the built-in wave
module.
'''

import wave
import config
import struct

# Try to import simpleaudio but don't complain if it doesn't exist
try:
    import simpleaudio
except Exception:
    simpleaudio = None


class AudioFormatError(Exception):
    '''An error generated when loading an audio file that doesn't match
    the settings in config.py.'''
    pass


def openWaveFile(sourcePath):
    '''Opens a .wav file and returns the sample source (result of
    `wave.open`) paired with the number of samples in the file, after
    making sure that the sample width, sample rate, and number of
    channels agree with the values in `config.py`. Prints information on
    the file properties, and raises an AudioFormatError if those
    properties don't match the required values.'''
    print("Opening audio file: '{}'".format(sourcePath))
    source = wave.open(sourcePath, mode = 'rb')
    numChannels = source.getnchannels()
    sampleWidth = source.getsampwidth() # byte depth
    frameRate = source.getframerate()
    numFrames = source.getnframes()

    # Ensure 16-bit and 44100 sample Rate
    if sampleWidth != config.SAMPLE_WIDTH:
        raise AudioFormatError("Audio files must be 16-bit files")

    if frameRate != config.SAMPLE_RATE:
        raise AudioFormatError("Audio files must be 44100kHz")

    if numChannels != config.NUM_CHANNELS:
        raise AudioFormatError(
            "Audio files must be in stereo. Mono and multichannel audio"
          + "not allowed"
        )

    print("Number of channels for source:", numChannels)
    print("Bit Depth:", sampleWidth * 8)
    print("Frame Rate:", frameRate)
    print("Number of Frames", numFrames)
    print()

    return source, numFrames


def openDestinationFile(destinationPath, source):
    '''Opens a .wav file for writing to and configures it based on the
    properties of the given sample source (a `wave.open` result).'''
    destination = wave.open(destinationPath, mode = 'wb')

    destination.setnchannels(source.getnchannels())
    destination.setsampwidth(source.getsampwidth())
    destination.setframerate(source.getframerate())

    return destination


def getFrames(source, framePointer):
    '''Takes a source which is an open file descriptor to a wavefile and a
    frame position to read from in the wave file and reads FRAME_CHUNK_SIZE
    number of frames from the wave file.  The frames are returned as a tuple.
    Recall that .wav files are interleaved so the tuple will contain the
    a sample from the left channel followed by the right channel if a stereo
    file.  Additionally, samples will be 16-bit signed integers so will need to
    be scaled to +/- 1 before processing.'''
    source.setpos(framePointer)

    # equivalent to number of samples * num of channels * num of bytes/sample
    frames = source.readframes(config.FRAME_CHUNK_SIZE)

    # samples * num of channels
    numOfSamples = round(len(frames)/config.SAMPLE_WIDTH)
    fmt = "<" + "h" * numOfSamples
    return struct.unpack(fmt, frames), numOfSamples


def separateChannels(frames, numChannels):
    '''Given a sequence of frames as tuple of interleaved samples, this
    function creates a more usable sequences of frames by creating a list
    of channels. Therefore the frames are de-interleaved such that each
    channel is in its own list. The sequence of frames are returned as a
    list of channels.

    If for whatever reason the number of frames is not a multiple of the
    number of channels, then extra frames will be discarded so that the
    number of frames in each channel is the same.
    '''
    channels = []
    limit = numChannels * (len(frames) // numChannels)
    for channelNum in range(numChannels):
        channelData = [
            frames[i]/pow(2, 15)
            for i in range(limit)
            if i % numChannels == channelNum
        ]
        channels.append(channelData)
    return channels


def reconstructFrames(channels):
    '''Takes a list of channels constituting frames to be written to a
    new wave file and converts the data from samples of +/-1 to signed
    16-bit integers.

    If the channel lengths aren't equal, the result will only be as long
    as the shortest channel.'''
    reconstructedFrames = []
    for sampleNum in range(min(len(ch) for ch in channels)):
        for channelNum in range(len(channels)):
            sample = channels[channelNum][sampleNum] * pow(2, 15)
            sample = round(sample)
            reconstructedFrames.append(sample)
    return reconstructedFrames
