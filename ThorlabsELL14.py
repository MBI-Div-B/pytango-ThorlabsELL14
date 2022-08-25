#!/usr/bin/python3 -u

# PyTango imports

import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import DevState
from tango import AttrWriteType

# Additional import
# PROTECTED REGION ID(ThorlabsELL14.additionnal_import) ENABLED START #
from thorlabs_elliptec import ELLx
from serial import SerialException
# PROTECTED REGION END #    //  ThorlabsELL14.additionnal_import

__all__ = ["ThorlabsELL14", "main"]


class ThorlabsELL14(Device):
    """

    **Properties:**

    - Device Property
        Port
            - Serial port of the ThorlabsELL14 controller
            - Type:'DevString'
        Address
            - Address of the ThorlabsELL14 axis
            - Type:'DevShort'
    """
    # PROTECTED REGION ID(ThorlabsELL14.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  ThorlabsELL14.class_variable

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
        max_warning=10000,
        doc="Number of movements sice last swipe command",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the ThorlabsELL14."""
        Device.init_device(self)
        # PROTECTED REGION ID(ThorlabsELL14.init_device) ENABLED START #
        self.dev_name = self.get_name()
        self.db = tango.Database()
        self.set_state(DevState.INIT)
        self._num_operations = int(self.db.get_device_attribute_property(
                    self.dev_name,'num_operations')['num_operations']['__value'][0]
                )
        try:
            self.stage = ELLx(serial_port=self.Port, device_id=self.Address)
            self.info_stream('Connected to Port {:s}'.format(self.Port))
            self.set_state(DevState.ON)
        except SerialException:
            self.error_stream('Cannot connect on Port {:s}'.format(self.Port))
            self.set_state(DevState.FAULT)
        # PROTECTED REGION END #    //  ThorlabsELL14.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(ThorlabsELL14.always_executed_hook) ENABLED START #
        info = ""
        if self._num_operations > 10000:
            info = "PLEASE EXECUTE SWIPE OPERATION!!!"
        if self.stage.is_moving():
            self.set_state(DevState.MOVING)
            info += "\nThe device is MOVING"
        else:
            self.set_state(DevState.ON)
            info += "\nThe device is ON"
        self.set_status(info)
        # PROTECTED REGION END #    //  ThorlabsELL14.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(ThorlabsELL14.delete_device) ENABLED START #
        self.db.put_device_attribute_property(
            self.dev_name,{'num_operations':{'__value':str(self._num_operations)}}
        )
        self.stage.close()
        self.info_stream('Closed connection on Port {:s}'.format(self.Port))
        # PROTECTED REGION END #    //  ThorlabsELL14.delete_device
    # ------------------
    # Attributes methods
    # ------------------

    def read_position(self):
        # PROTECTED REGION ID(ThorlabsELL14.position_read) ENABLED START #
        """Return the position attribute."""
        return self.stage.get_position()
        # PROTECTED REGION END #    //  ThorlabsELL14.position_read

    def write_position(self, value):
        # PROTECTED REGION ID(ThorlabsELL14.position_write) ENABLED START #
        """Set the position attribute."""
        self.stage.move_absolute(value)
        self.set_state(DevState.MOVING)
        # writing to  db of device the device and increasing __value by one
        self._num_operations += 1
        # PROTECTED REGION END #    //  ThorlabsELL14.position_write

    def read_num_operations(self):
        # PROTECTED REGION ID(ThorlabsELL14.num_operations_read) ENABLED START #
        """Return the num_operations attribute."""
        return self._num_operations  # reads the value of __vlaue of attribue num_operations of the device
        # PROTECTED REGION END #    //  ThorlabsELL14.num_operations_read

    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def homing(self):
        # PROTECTED REGION ID(ThorlabsELL14.homing) ENABLED START #
        self.stage.home()
        self.set_state(DevState.MOVING)
        #writing to  db of the device and increasing __value by one
        self._num_operations += 1
        # PROTECTED REGION END #    //  ThorlabsELL14.homing

    @command()
    @DebugIt()
    def swipe(self):
        # PROTECTED REGION ID(ThorlabsELL14.swipe) ENABLED START #
        """
            swipe
                    Executes a swipe move over the full range of motion as
                    required every 10000 operations (see user manual section 4.4).

        :return:None
        """
        self.stage.move_absolute(0.)
        self.stage.move_absolute(359.)
        self.stage.move_absolute(0.)
        #writing to  db of the device
        self._num_operations = 0
            # PROTECTED REGION END #    //  ThorlabsELL14.swipe

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the ThorlabsELL14 module."""
    # PROTECTED REGION ID(ThorlabsELL14.main) ENABLED START #
    return run((ThorlabsELL14,), args=args, **kwargs)
    # PROTECTED REGION END #    //  ThorlabsELL14.main


if __name__ == '__main__':
    main()
