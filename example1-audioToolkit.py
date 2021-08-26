# Your name: Juliette Lange 
# Your username: jl8
# CS111 PS04 Task 3
# audioToolkit.py
# Submission date: 11/20/20

# This currently assumes a 16-bit, 44100Hz .wav file
#Allow some time for audio to play!

import os
from waveTools import *
import config


def makeSofter(channel):  
    '''
this function will make the audio softer.
    '''
    softList = []
    
    for number in channel:
        
        number = number * 0.1
        final = round(number,2)
        softList.append(final)
    return(softList) 
        
   

def chipmunk(channel):
    '''
Chipmunk makes audio bites smaller by cutting them in half making a high pitch sound effect.
    '''
    chipList = []
    for number in channel[0::2]:
        chipList.append(number)
    return chipList
        
 

def removeVocals(leftChannel, rightChannel):
    '''
removeVocals isolates vocals in center stage by subtracting right Channel audio output from lefChannel. 
    '''
    vocalsList = []

    for number in range(len(leftChannel)):
        finalVocal = round(((leftChannel[number]  - rightChannel[number])/2),2)
        vocalsList.append(finalVocal)
    return vocalsList
        
    



def reverse(channel):
    '''
reverse prints the list in reverse.
    '''
    reverseList = []
    for number in range(len(channel)):
        newNum = (number + 1) * -1
        reverseList.append(channel[newNum])
    return reverseList

    
    
def twoSampleDelay(channel, oneSampleBack, twoSampleBack):
    '''
    twoSampleDelay returns a delay. 
    '''
    delayList = [twoSampleBack, oneSampleBack]
    finalList = []
    for number in range(len(channel)):
        delayList.append(channel[number])
        avgNum = (channel[number] + delayList[number])/2
        finalList.append(avgNum)
    return finalList
    
twoSampleDelay([0.1, -0.2, 0.5, 0.6], -0.9, -0.7)        
        
        
    


def ohYeah(channel, prevSample):
    '''
ohYeah makes the audio sound lower by lengthening the audio data. 
    '''
    prevList = [prevSample]
    morphList = []
    decayList = []
    #newAvgList = [avgNum,channel[number]]
    #ohYeahChannel = (prevSample + channel[0])/2
    for number in range(len(channel)):
#if num < (len(channel - 1))
#ohYeahChannel.append(channel[number])  
        prevList.append(channel[number])
        avgNum = (channel[number] + prevList[number])/2
        
       

        morphList.append(channel[number])
        morphList.append(avgNum)
    return morphList
        


def crescendo(channel, startVolume, endVolume):
    '''
crescendo creating a raising volume through multiplying increasing intervals by the original channel of audio. 
    '''
    # TODO: Write me
    cresList=[]
    if len(channel)>0:
       intervalInc= (endVolume - startVolume)/len(channel)
   
    intervalList = startVolume 
    for number in range(len(channel)):
        rollCres = channel[number] * intervalList 
        cresList.append(rollCres)
        intervalList += intervalInc    
    return cresList


def processEffect(frames, effect, source, prevTwoFrames, fadeStartPoint):
    '''
    Given some frames and an effect to apply, applies that affect to the
    given source audio. Also needs to know the last two frames from the
    previous chunk so that effects which use previous frames can work
    smoothly, and the fade start point so that crescendo can be applied
    smoothly across multiple chunks.
    '''
    newPrevTwoFrames = [
        (frames[0][-1], frames[1][-1]),
        (frames[0][-2], frames[1][-2])
    ]
    fadeEndPoint = fadeStartPoint
    
    if effect == "makeSofter":
        lc = makeSofter(frames[0])
        rc = makeSofter(frames[1])
        target_length = len(frames[0])
        processedFrames = lc, rc
    elif effect == "removeVocals":
        processedChannel = removeVocals(frames[0], frames[1])
        processedFrames = [processedChannel, processedChannel]
        target_length = len(frames[0])
    elif effect == "chipmunk":
        lc = chipmunk(frames[0])
        rc = chipmunk(frames[1])
        target_length = len(frames[0]) // 2
        processedFrames = lc, rc
    elif effect == "reverse":
        lc = reverse(frames[0])
        rc = reverse(frames[1])
        target_length = len(frames[0])
        processedFrames = lc, rc
    elif effect == "ohYeah":
        lc = ohYeah(frames[0], prevTwoFrames[0][0])
        rc = ohYeah(frames[1], prevTwoFrames[0][1])
        target_length = len(frames[0]) * 2
        processedFrames = lc, rc
    elif effect == "twoSampleDelay":
        processedFrames = []
        lc = twoSampleDelay(frames[0], prevTwoFrames[0][0], prevTwoFrames[1][0])
        rc = twoSampleDelay(frames[1], prevTwoFrames[0][1], prevTwoFrames[1][1])
        processedFrames = lc, rc
        prevTwoFrames = newPrevTwoFrames
        target_length = len(frames[0])
    elif effect == "crescendo":
        totalFadeTime = source.getnframes()
        # For certain duration: <time> * config.SAMPLE_RATE
        fadeEndPoint = len(frames[0])/(totalFadeTime) + fadeStartPoint
        if fadeEndPoint <= 1:
            lc = crescendo(frames[0], fadeStartPoint, fadeEndPoint)
            rc = crescendo(frames[1], fadeStartPoint, fadeEndPoint)
            processedFrames = lc, rc
        else:
            processedFrames = frames
        target_length = len(frames[0])
    elif effect == "custom":
        lc = custom(frames[0])
        rc = custom(frames[1])
        target_length = None
        processedFrames = lc, rc
    else:
        raise ValueError(
            "You have entered the name of an effect that is invalid.  " +
            "Please check your spelling."
        )
    # Error checking
    if any(item > 1.0 or item < -1.0 for frame in processedFrames for item in frame):
        raise ValueError(
            "Your effect returned a sample value that was too"
          + "large (> 1.0) or too small (< -1.0)."
        )
    if (
        target_length != None
    and len(processedFrames[0]) != target_length
    ):
        raise ValueError(
            (
                "Your effect returned a list of {} samples, when it"
              + "should have returned {} samples."
            ).format(
                len(processedFrames[0]),
                target_length
            )
        )
    return processedFrames, newPrevTwoFrames, fadeEndPoint


def processFile(sourcePath, destinationPath, effect):
    '''
    Loads data from the fie at the given source path, applies the given
    affect, and saves a processed file at the given destination path.
    Also, if the `simpleaudio` module is available, this will play the
    processed audio directly using the system's speakers; if not, it
    prints out a message indicating that `simpleaudio` could be
    installed.
    '''
    source, numFrames = openWaveFile(sourcePath)
    destination = openDestinationFile(destinationPath, source)
    wavedata = b""

    # necessary for "reverse"
    frameRange = range(0, numFrames, config.FRAME_CHUNK_SIZE)
    if effect == "reverse":
        frameRange = reversed(frameRange)

    # necessary for "crescendo"
    fadeStartPoint = 0
    
    # necessary for "twoSampleDelay" and "ohYeah"
    prevTwoFrames = [(0, 0), (0, 0)]
    # [(lc: n - 1), (rc: n - 1), (lc: n - 2, rc: n - 2)]

    # process each FRAME_CHUNK_SIZE window of data in the wave file
    for framePointer in frameRange:
        # Get config.FRAME_CHUNK_SIZE frames from wave file
        # Last window will be <= FRAME_CHUNK_SIZE
        frames, numOfSamples = getFrames(source, framePointer)
        if numOfSamples == 0 and numFrames != framePointer + numOfSamples:
            print(
                "Warning: Your .wav file appears to be corrupted! Are"
              + " you sure your download was completed without errors?"
            )
            print(
                (
                    "Your .wav file says it contains {} frames, but we"
                    " only found {}."
                ).format(numFrames, framePointer + numOfSamples)
            )
        splitFrames = separateChannels(frames, config.NUM_CHANNELS)

        # Get process effect on window
        data = processEffect(
            splitFrames,
            effect,
            source,
            prevTwoFrames,
            fadeStartPoint
        )
        processedFrames, newPrevTwoFrames, newStartPoint = data

        # Reconstruct window into list of interleaved samples
        outputFrames = reconstructFrames(processedFrames)

        # Write data
        fmt = "<" + "h" * len(outputFrames) # generally the same as numOfSamples
        coded = struct.pack(fmt, *outputFrames) # * is the unpacking operator
        destination.writeframes(coded)
        if simpleaudio is not None:
            wavedata += coded

        # Update data for twoSampleDelay and crescendo
        prevTwoFrames, fadeStartPoint = newPrevTwoFrames, newStartPoint

    destination.close()
    source.close()

    if simpleaudio is None:
        print(
            "Note: if you install the `simpleaudio` package via the"
          + " 'Manage packages' option in the 'Tools' menu, the"
          + " the processed result will be played directly in Python."
        )
    else:
        print("Playing the result directly using `simpleaudio`...")
        wo = simpleaudio.WaveObject(
            wavedata,
            config.NUM_CHANNELS,
            config.SAMPLE_WIDTH,
            config.SAMPLE_RATE
        )
        wo.play().wait_done()


###############################################
# TESTING CODE - COMMENT AND UNCOMMENT THINGS #
###############################################

def test():
    """
    Standard testing function: gets run when the file is
    run, but not when it's being graded.
    """
    # Soundfile sources and destinations
    soundsdir = os.path.join(os.getcwd(), "sounds")
    pokerSourcePath = os.path.join(soundsdir, "poker.wav");
    pokerDestinationPath = os.path.join(soundsdir, "poker_proc.wav");
    helloSourcePath = os.path.join(soundsdir, "hello.wav");
    helloDestinationPath = os.path.join(soundsdir, "hello_proc.wav");
    prayerSourcePath = os.path.join(soundsdir, "prayer.wav");
    prayerDestinationPath = os.path.join(soundsdir, "prayer_proc.wav");
    distanceSourcePath = os.path.join(soundsdir, "distance.wav");
    distanceDestinationPath = os.path.join(soundsdir, "distance_proc.wav");

    print("Start testing...")

    #Test makeSofter WORKS!
    #print(makeSofter([0, -0.2, 0.4, -0.6]))
    #print(makeSofter([]))
    #print(makeSofter([0.1, -0.4]))
    #processFile(pokerSourcePath, pokerDestinationPath, "makeSofter")
    #processFile(distanceSourcePath, distanceDestinationPath, "makeSofter")

    # Test chipmunk NOTworking
    #print(chipmunk([0, -0.2, 0.4, -0.6]))
    #print(chipmunk([-0.3, 0.2, 0.1]))
    #print(chipmunk([]))
    #processFile(prayerSourcePath, prayerDestinationPath, "chipmunk")
    #processFile(helloSourcePath, helloDestinationPath, "chipmunk")

    # Test removeVocals WORKS!
    #print(removeVocals([0.1, 0.5, -0.2, 0.3], [-0.1, -0.6, 0.3, 0.1]))
    #print(removeVocals([0.7, 0.2], [0.3, -0.4]))
    #print(removeVocals([], []))
    #processFile(distanceSourcePath, distanceDestinationPath, "removeVocals")
    #processFile(pokerSourcePath, pokerDestinationPath, "removeVocals")

    # Test reverse WORKS!!
    #print(reverse([0.1, -0.2, 0.5, 0.2]))
    #print(reverse([0.1, -0.9, 0.3]))
    #print(reverse([]))
    #processFile(pokerSourcePath, pokerDestinationPath, "reverse")
    #processFile(prayerSourcePath, prayerDestinationPath, "reverse")

    # Test twoSampleDelay #NOT working
    #print(twoSampleDelay([0.1, -0.2, 0.5, 0.6], -0.7, -0.9))
    #print(twoSampleDelay([0.1, 0.6, -0.2, 0.25, 0.3], -0.5, 0))
    #print(twoSampleDelay([], 0.1, 0.2))
    #processFile(prayerSourcePath, prayerDestinationPath, "twoSampleDelay")
    #processFile(pokerSourcePath, pokerDestinationPath, "twoSampleDelay")

    #Test ohYeah WORKING
    #print(ohYeah([0.5, -0.1, 0.4], -0.1))
    #print(ohYeah([0.1], 0.1))
    #print(ohYeah([], -0.9))
    #processFile(helloSourcePath, helloDestinationPath, "ohYeah")
    #processFile(pokerSourcePath, pokerDestinationPath, "ohYeah")

    # Test crescendo WORKING
    #print(crescendo([1.0, 1.0, 1.0], 0.2, 0.8))
    #print(crescendo([0.9, 0.4, 0.6, 0.2], 0, 1))
    #print(crescendo([], 0, 1))
    #processFile(helloSourcePath, helloDestinationPath, "crescendo")
    #processFile(prayerSourcePath, prayerDestinationPath, "crescendo")

    # Test custom
    # processFile(pokerSourcePath, pokerDestinationPath, "custom")
    # processFile(helloSourcePath, helloDestinationPath, "custom")

    print("...end testing.")

if __name__ == '__main__':
    test()
