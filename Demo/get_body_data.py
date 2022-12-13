import os
import sys
import time
from ctypes import *

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

# get body(id:0) component 0:x,1:y,2:z,3:rx,4:ry,5:rz,6:rw with time predict
# warning : When using this function, the 'frameCount' must increase with the number of calls
def CMTrackerExtern(host,bodyID,frameCount):
    bodyPos = (c_double * 3)()
    bodyRot = (c_double * 4)()
    trackerExtern = cmVrpn.CMTrackerExtern
    trackerExtern.restype = c_double

    bodyPos[0] = cmVrpn.CMTrackerExtern(host, bodyID, 0, frameCount)
    bodyPos[1] = cmVrpn.CMTrackerExtern(host, bodyID, 1, frameCount)
    bodyPos[2] = cmVrpn.CMTrackerExtern(host, bodyID, 2, frameCount)

    bodyRot[0] = cmVrpn.CMTrackerExtern(host, bodyID, 3, frameCount)
    bodyRot[1] = cmVrpn.CMTrackerExtern(host, bodyID, 4, frameCount)
    bodyRot[2] = cmVrpn.CMTrackerExtern(host, bodyID, 5, frameCount)
    bodyRot[3] = cmVrpn.CMTrackerExtern(host, bodyID, 6, frameCount)

    # check body detected, must call after CMTrackerExtern
    isBodyDetected = cmVrpn.CMTrackerExternIsDetected(host, bodyID, frameCount)
    if (isBodyDetected):
        print("pos: X:%f Y:%f Z:%f"%(bodyPos[0], bodyPos[1], bodyPos[2]))
        print("quaternion: rx:%f ry:%f rz:%f rw:%f"%(bodyRot[0], bodyRot[1], bodyRot[2], bodyRot[3]))
    else:
        print("Rigid body %d not detected"%(bodyID))
    return isBodyDetected

# get body(id:0) T(XYZ 3), body Quaternion(XYZR 4), timecode without time predict
def CMTrackerExternTC(host,bodyID,frameCount):
    bodyPos = (c_double * 3)()
    bodyRot = (c_double * 4)()
    timecodeData = (c_int * 1)()
    isBodyDetected = cmVrpn.CMTrackerExternTC(host, bodyID, timecodeData, bodyPos, bodyRot)

    if (isBodyDetected):
        timecode = timecodeData[0]
        valid = ((timecode & 0x80000000) >> 31)
        if (True == valid):
            PrintTimecode(timecode)
        else:
            print("server frame num: %d" % (timecode))

        print("pos: X:%f Y:%f Z:%f"%(bodyPos[0], bodyPos[1], bodyPos[2]))
        print("quaternion: rx:%f ry:%f rz:%f rw:%f"%(bodyRot[0], bodyRot[1], bodyRot[2], bodyRot[3]))
    else:
        print("Rigid body %d not detected" % (bodyID))
    return isBodyDetected

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
    bodyID = 0

    frameCount = 0

    getfailed = 0
    loopState = True
    while(loopState):
        if(frameCount > 10000):
            loopState = False

        # Control acquisition frequency.parameters can be customized.
        time.sleep(0.2)

        # Enable functions as required
        isDataDetected = CMTrackerExtern(host, bodyID, frameCount)
        # isDataDetected = CMTrackerExternTC(host, bodyID, frameCount)
        if(isDataDetected):
            getfailed = 0
        else:
            getfailed += 1

        if(getfailed > 10):
            print("Continuous acquisition failed, exit the program.")
            loopState = False

        frameCount += 1

    # quit vrpn thread
    cmVrpn.CMVrpnQuitExtern()
