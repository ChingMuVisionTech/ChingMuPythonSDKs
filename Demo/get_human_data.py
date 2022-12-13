import os
import sys
import time
from ctypes import *

MAX_SEGMENT_NUM = 150

# Load dynamic Library
def LoadDll(dllPath):
    if(os.path.exists(dllPath)):
        return CDLL(dllPath)
    else:
        print("Chingmu's dynamic Library  does not exist \n")
        sys.exit()


def PrintTimecode(timecode):
    standard = ((timecode & 0x60000000) >> 29)
    hours = ((timecode & 0x1f000000) >> 24)
    minutes = ((timecode & 0x00fc0000) >> 18)
    seconds = ((timecode & 0x0003f000) >> 12)
    frames = ((timecode & 0x00000fe0) >> 5)
    subframes = (timecode & 0x0000001f)
    print("Time code: %d:%d:%d:%d" % (hours, minutes, seconds, frames))

# get human(id:0) attitude(hips pos XYZ(3) + segments quaternion XYZW(segmentNum * 4)), segmentIsDetected(segmentNum)
def CMHumanExtern(host,humanID,frameCount):
    attitude = (c_double * (3 + MAX_SEGMENT_NUM * 4))()
    isDetected = (c_int * MAX_SEGMENT_NUM)()
    isHumanDetected = cmVrpn.CMHumanExtern(host, humanID, frameCount, attitude, isDetected)
    if(True == isHumanDetected):
        print("pos: X:%f Y:%f Z:%f"%(attitude[0], attitude[1], attitude[2]))
        print("quaternion: rx:%f ry:%f rz:%f rw:%f"%(attitude[3], attitude[4], attitude[5], attitude[6]))
    else:
        print("Human %d not detected" % (humanID))
    return isHumanDetected

# get human(id: 0) T(segmentNum * 3), localR(segmentNum * 4), segmentIsDetected(segmentNum), timecode
def CMHumanGlobalTLocalRTC(host,humanID,frameCount):
    humanT = (c_double * (MAX_SEGMENT_NUM * 3))()
    humanLocalR = (c_double * (MAX_SEGMENT_NUM * 4))()
    segmentIsDetected = (c_int * MAX_SEGMENT_NUM)()
    timecodeData = (c_int * 1)()
    isHumanDetected = cmVrpn.CMHumanGlobalTLocalRTC(host, humanID, timecodeData, humanT, humanLocalR, segmentIsDetected)

    if (True == isHumanDetected):
        timecode = timecodeData[0]
        valid = ((timecode & 0x80000000) >> 31)
        if(True == valid):
            PrintTimecode(timecode)
        else:
            print("server frame num: %d"%(timecode))

        print("pos: X:%f Y:%f Z:%f" % (humanT[0], humanT[1], humanT[2]))
        print("quaternion: rx:%f ry:%f rz:%f rw:%f" % (humanLocalR[0], humanLocalR[1], humanLocalR[2], humanLocalR[3]))
    else:
        print("Human %d not detected" % (humanID))
    return isHumanDetected

# get human(id:0) humanT XYZ(segmentNum * 3), humanLocalR XYZW(segmentNum * 4), segmentIsDetected(segmentNum), timecode
# humanT[0:3] is root node position, humanLocalR[0:4] is root node rotation.
def CMRetargetHumanExternTC(host,humanID,frameCount):
    humanT = (c_double * (MAX_SEGMENT_NUM * 3))()
    humanLocalR = (c_double * (MAX_SEGMENT_NUM * 4))()
    segmentIsDetected = (c_int * MAX_SEGMENT_NUM)()
    timecodeData = (c_int * 1)()
    isHumanDetected = cmVrpn.CMRetargetHumanExternTC(host, humanID, frameCount, timecodeData, humanT, humanLocalR,segmentIsDetected)

    if (True == isHumanDetected):
        timecode = timecodeData[0]
        valid = ((timecode & 0x80000000) >> 31)
        if (True == valid):
            PrintTimecode(timecode)
        else:
            print("server frame num: %d" % (timecode))

        index = 1
        print("pos: X:%f Y:%f Z:%f" % (humanT[index * 3], humanT[index * 3 +1], humanT[index * 3 + 2]))
        print("quaternion: rx:%f ry:%f rz:%f rw:%f" % (humanLocalR[index * 4], humanLocalR[index * 4 + 1], humanLocalR[index * 4 + 2], humanLocalR[index * 4 + 3]))
    else:
        pass
        #print("Human %d not detected" % (humanID))
    return isHumanDetected

if __name__ == '__main__':
    # Set dynamic Library path
    dllPath = os.path.dirname(os.path.dirname(__file__)) + "\\ChingmuDLL\\CMVrpn.dll"

    # Load dynamic Library
    cmVrpn = LoadDll(dllPath)

    # set server address
    host = bytes("MCAvatar@127.0.0.1", "gbk")

    # start vrpn thread
    cmVrpn.CMVrpnStartExtern()

    # enable write trace_log.txt
    cmVrpn.CMVrpnEnableLog(True)

    # Person ID displayed on the server
    humanID = 0

    frameCount = 0
    getfailed = 0
    loopState = True
    while(loopState):
        # Control acquisition frequency.parameters can be customized.
        time.sleep(0.2)

        if(frameCount > 1000):
            loopState = False

        # Enable functions as required
        # isDataDetected = CMHumanGlobalTLocalRTC(host,humanID,frameCount)
        isDataDetected = CMRetargetHumanExternTC(host,humanID,frameCount)
        # isDataDetected = CMHumanExtern(host, humanID, frameCount)

        if(isDataDetected):
            getfailed = 0
            frameCount += 1
        else:
            getfailed += 1

        # if(getfailed > 10):
        #     print("Continuous acquisition failed, exit the program.")
        #     loopState = False

    # quit vrpn thread
    cmVrpn.CMVrpnQuitExtern()
