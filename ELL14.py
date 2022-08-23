#!/usr/bin/python3 -u

from tango import AttrWriteType, DevState, DebugIt
from tango.server import Device, attribute, command, device_property
from thorlabs_elliptec import ELLx
from serial import SerialException

class ELL14(Device):
    """ELL14

    Tango Device Server for controlling a Thorlabs ELL14
    Rotation Mount
    """

    Port = device_property(dtype='str', doc='Serial port of the ELL14 controller')
    Address = device_property(dtype='int', doc='Address of the ELL14 axis')

    position = attribute(
        min_value=0.0,
        max_value=360.0,
        dtype='float',
        access=AttrWriteType.READ_WRITE,
        label='Position',
        unit='degree',
        format='%6.3f',
        doc='absolute position in degree',
    )

    num_operations = attribute(
        min_value=0,
        max_warning=10000,
        dtype='int',
        label='Number of Movements',
        format='%5.0f',
        doc='Number of movements since last Swipe operation',
        )

    def init_device(self):
        Device.init_device(self)
        self.set_state(DevState.INIT)
        self._counter = 0
        try:
            self.stage = ELLx(serial_port=self.Port, device_id=self.Address)
            self.info_stream('Connected to Port {:s}'.format(self.Port))
            self.set_state(DevState.ON)
        except SerialException:
            self.error_stream('Cannot connect on Port {:s}'.format(self.Port))
            self.set_state(DevState.FAULT)

    def delete_device(self):
        self.stage.close()
        self.info_stream('Closed connection on Port {:s}'.format(self.Port))

    def always_executed_hook(self):
        info = ""
        if self._counter > 10000:
            info = "PLEASE EXECUTE SWIPE OPERATION!!!"
        if self.stage.is_moving():
            self.set_state(DevState.MOVING)
            info += "\nThe device is MOVING"
        else:
            self.set_state(DevState.ON)
            info += "\nThe device is ON"
        self.set_status(info)

    def read_position(self):
        return self.stage.get_position()
        
    def write_position(self, value):
        self.stage.move_absolute(value)
        self.set_state(DevState.MOVING)
        self._counter +=1

    def read_num_operations(self):
        return self._counter   

    @command
    def homing(self):      
        self.stage.home()
        self.set_state(DevState.MOVING)
        self._counter +=1
    
    @command
    def swipe(self):
        """swipe
    
        Executes a swipe move over the full range of motion as 
        required every 10000 operations (see user manual section 4.4).
        """
        self.stage.move_absolute(0.)
        self.stage.move_absolute(359.)
        self.stage.move_absolute(0.)
        self._counter=0 


# start the server
if __name__ == '__main__':
    ELL14.run_server()
    
