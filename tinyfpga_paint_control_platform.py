from nmigen import *
from nmigen_boards.tinyfpga_bx import *
from nmigen.build import Resource, Pins, Subsignal

def MotorSignalResource(index, enable_o, limit_top, limit_bottom):
    return Resource(
        "motor_signals",
        index,
        Subsignal("enable_o", Pins(enable_o, conn=("gpio", 0), dir="o")),
        Subsignal("limit_top", Pins(limit_top, conn=("gpio", 0), dir="i")),
        Subsignal("limit_bottom", Pins(limit_bottom, conn=("gpio", 0), dir="i")),
    )

motor_signal_pins = [
    # Pins for (enable_o, limit_top, limit_bottom) for each motor signal bundle
    ("5", "6", "7"),
    ("8", "9", "10"),  # pins 8, 9, 10
    ("11", "12", "13"),  # pins 11, 12, 13
    ("14", "15", "16"),  # pins 14, 15, 16
    ("17", "18", "19"),  # pins 17, 18, 19
]

motor_signal_resources = [
    MotorSignalResource(i, e, t, b) for
    i, (e, t, b) in enumerate(motor_signal_pins)
]

spi = Resource(
    "spi",
    0,
    Subsignal("clk", Pins("1", conn=("gpio", 0), dir="i")),
    Subsignal("ss", Pins("2", conn=("gpio", 0), dir="i")),
    Subsignal("mosi", Pins("3", conn=("gpio", 0), dir="i")),
    Subsignal("miso", Pins("4", conn=("gpio", 0), dir="o")),
)

class PaintControlPlatform(TinyFPGABXPlatform):
    resources = (
        TinyFPGABXPlatform.resources +
        motor_signal_resources +
        [
            spi,
            Resource("steps", 0, Pins("20", conn=("gpio", 0), dir="o")),
            Resource("direction", 0, Pins("21", conn=("gpio", 0), dir="o")),
        ]
    )
