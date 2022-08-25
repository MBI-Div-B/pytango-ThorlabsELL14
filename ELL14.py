# -*- coding: utf-8 -*-
#
# This file is part of the ELL14 project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" 

"""

# PyTango imports
from ast import Num
from contextlib import nullcontext
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import AttrQuality, DispLevel, DevState
from tango import AttrWriteType, PipeWriteType

# Additional import
# PROTECTED REGION ID(ELL14.additionnal_import) ENABLED START #
from thorlabs_elliptec import ELLx
from serial import SerialException
# PROTECTED REGION END #    //  ELL14.additionnal_import

__all__ = ["ELL14", "main"]


class ELL14(Device):
    """

    **Properties:**

    - Device Property
        Port
            - Serial port of the ELL14 controller
            - Type:'DevString'
        Address
            - Address of the ELL14 axis
            - Type:'DevShort'
    """
    # PROTECTED REGION ID(ELL14.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  ELL14.class_variable

    # -----------------
    # Device Properties
    # -----------------

    Port = device_property(
        dtype='DevString',
    )

    Address = device_property(
        dtype='DevShort',
    )

    # ----------
    # Attributes
    # ----------

    position = attribute(
        dtype='DevFloat',
        access=AttrWriteType.READ_WRITE,
        label="Position",
        unit="degree",
        format="%6.3f",
        max_value=360,
        min_value=0,
        doc="absolute position in degree",
    )

    num_operations = attribute(
        dtype='DevULong',
        label="Number of movements",
        format="%5.0f",
        min_value=0,
        max_warning=10,
        doc="Number of movements sice last swipe command",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the ELL14."""
        
        Device.init_device(self)
        # PROTECTED REGION ID(ELL14.init_device) ENABLED START #
        self.dev_name = self.get_name()
        self.db = tango.Database()
        self.set_state(DevState.INIT)
        
        try:
            self.stage = ELLx(serial_port=self.Port, device_id=self.Address)
            self.info_stream('Connected to Port {:s}'.format(self.Port))
            self.set_state(DevState.ON)     
        except SerialException:
            self.error_stream('Cannot connect on Port {:s}'.format(self.Port))
            self.set_state(DevState.FAULT)
        # PROTECTED REGION END #    //  ELL14.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(ELL14.always_executed_hook) ENABLED START #
        info = ""
        if self.read_num_operations() > 10:
            info = "PLEASE EXECUTE SWIPE OPERATION!!!"
        if self.stage.is_moving():
            self.set_state(DevState.MOVING)
            info += "\nThe device is MOVING"
        else:
            self.set_state(DevState.ON)
            info += "\nThe device is ON"
        self.set_status(info)
        # PROTECTED REGION END #    //  ELL14.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(ELL14.delete_device) ENABLED START #
        self.stage.close()
        self.info_stream('Closed connection on Port {:s}'.format(self.Port))
        # PROTECTED REGION END #    //  ELL14.delete_device
    # ------------------
    # Attributes methods
    # ------------------

    def read_position(self):
        # PROTECTED REGION ID(ELL14.position_read) ENABLED START #
        """Return the position attribute."""
        return self.stage.get_position()
        # PROTECTED REGION END #    //  ELL14.position_read

    def write_position(self, value):
        # PROTECTED REGION ID(ELL14.position_write) ENABLED START #
        """Set the position attribute."""
        self.stage.move_absolute(value)
        self.set_state(DevState.MOVING)
        self.db.put_device_attribute_property(self.dev_name,{'num_operations':{'__value':
            str(int(self.db.get_device_attribute_property(self.dev_name,'num_operations')['num_operations']['__value'][0])+1)}})  #writing to  db of device the device and increasing __value by one
        # PROTECTED REGION END #    //  ELL14.position_write

    def read_num_operations(self):
        # PROTECTED REGION ID(ELL14.num_operations_read) ENABLED START #
        """Return the num_operations attribute."""
        return  int(self.db.get_device_attribute_property(self.dev_name,'num_operations')['num_operations']['__value'][0]) # reads the value of __vlaue of attribue num_operations of the device
        # PROTECTED REGION END #    //  ELL14.num_operations_read

    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def homing(self):
        # PROTECTED REGION ID(ELL14.homing) ENABLED START #
        self.stage.home()
        self.set_state(DevState.MOVING)
        self.db.put_device_attribute_property(self.dev_name,{'num_operations':{'__value':
            str(int(self.db.get_device_attribute_property(self.dev_name,'num_operations')['num_operations']['__value'][0])+1)}})  #writing to  db of the device and increasing __value by one
        # PROTECTED REGION END #    //  ELL14.homing

    @command()
    @DebugIt()
    def swipe(self):
        # PROTECTED REGION ID(ELL14.swipe) ENABLED START #
        """
            swipe
                
                    Executes a swipe move over the full range of motion as 
                    required every 10000 operations (see user manual section 4.4).

        :return:None
        """
        self.stage.move_absolute(0.)
        self.stage.move_absolute(359.)
        self.stage.move_absolute(0.)
        self.db.put_device_attribute_property(self.dev_name,{'num_operations':{'__value':'0'}})  #writing to  db of the device
        # PROTECTED REGION END #    //  ELL14.swipe

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the ELL14 module."""
    # PROTECTED REGION ID(ELL14.main) ENABLED START #
    return run((ELL14,), args=args, **kwargs)
    # PROTECTED REGION END #    //  ELL14.main


if __name__ == '__main__':
    main()
