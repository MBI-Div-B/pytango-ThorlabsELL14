#!/usr/bin/env python3
#

import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import DevState
from tango import AttrWriteType

#from thorlabs_elliptec import ELLx
from ELL14 import ELL14
from serial import SerialException
import serial
import time

__all__ = ["ThorlabsELL14", "main"]


class ThorlabsELL14(Device):
    """
    This is a Tango device server for a Thorlabs ELL14 rotation stage.
    """

    # -----------------
    # Device Properties
    # -----------------

    SerialNum = device_property(
        dtype='DevString',
    )

    # ----------
    # Attributes
    # ----------

    position = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ_WRITE,
        label="Position",
        unit="degree",
        format="%5.2f",
        doc="absolute position in degree",
        fget = "read_position",
        fset = "write_position",
    )

    velocity = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ_WRITE,
        label="Velocity",
        unit="arb. u.",
        doc="velocity between 0 and 64",
        min_value=0,
        fget = "get_vel",
        fset = "set_vel",
    )

    home = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ_WRITE,
        label="Home",
        unit="degree",
        format="%5.2f",
        doc="home position in degree",
        fget = "get_homeoffset",
        fset = "set_homeoffset",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        
        self._pp = 143360 #Number of steps per revolution (see manual Ch. 6)
        """Initialises the attributes and properties of the ThorlabsELL14."""
        Device.init_device(self)
        self._serial = self.SerialNum
        self.db = tango.Database()
        self.set_state(DevState.INIT)
        try:
            self.stage = ELL14(serial_number = self._serial)
            self.info_stream('Connected to Device {:s}'.format(self._serial))
            print(self._serial)
            self.init_params()
            self.set_state(DevState.ON)
        except SerialException:
            self.error_stream('Cannot connect to Device {:s}'.format(self._serial))
            self.set_state(DevState.FAULT)

    def init_params(self):
        time.sleep(1)
        self.swipe()
        
    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        info = ""
        if self.stage.is_moving():
            self.set_state(DevState.MOVING)
            info += "\nThe device is MOVING"
        else:
            self.set_state(DevState.ON)
            info += "\nThe device is ON"
        self.set_status(info)

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        self.stage.close()
        self.info_stream('Closed connection to Device {:s}'.format(serial))

    # ------------------
    # Attributes methods
    # ------------------

    def read_position(self):
        #get the position attribute.
        return round(self.stage.get_position(),2)

    def write_position(self, value):
        #Set the position attribute.
        self.stage.move_absolute((value)%360.0, blocking = True)
        self.set_state(DevState.MOVING)

    def get_homeoffset(self):
        #get home attribute.
        return self.stage.get_home()
    
    def set_homeoffset(self,value):
        #set home attribute.
        value = value%360
        self.stage._updatequeue.append(f"so{int(143360*value/360.0) & 0xffffffff:08X}")

    def get_vel(self):
        #get velocity attribute.
        return self.stage.get_velocity()

    def set_vel(self, value):
        #Set the velocity attribute.
        value = int(value)
        if value <= 64:
            self.stage._updatequeue.append('sv'+str(value))
        else:
            self.comm('sv64')

    # --------
    # Commands
    # --------

    @command()
    @DebugIt()
    def homing(self):
        self.stage.home(blocking = True)
        self.set_state(DevState.MOVING)

    @command()
    @DebugIt()
    def swipe(self):
        pos = self.read_position()
        self.stage.move_absolute(0.)
        self.stage.move_absolute(359.)
        self.stage.move_absolute(0.)
        self.write_position(pos)

    @command(dtype_in = str, dtype_out = str)
    def comm(self, comman):
        return_data = str(self.stage._write_command(comman))
        return return_data

    @command(dtype_in = float)
    def ShiftOffset(self, shift):
        co = self.get_homeoffset()
        self.set_homeoffset(co+shift)
# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the ThorlabsELL14 module."""
    return run((ThorlabsELL14,), args=args, **kwargs)


if __name__ == '__main__':
    main()
