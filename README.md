# M5StickV-People-Counter

https://github.com/warremkaw/M5StickV-People-Counter/assets/45612195/8cf65f7f-aaf1-4b3d-aea4-384aa92ae5d8

## Installing MaixPy onto M5StickV

### Requirements

#### Arch based distros

``` {.bash}
pacman -S python3 python-pyserial cmake
yay -S kendryte-toolchain-bin python-kflash
```

#### Debian based distros

``` {.bash}
apt install python3 python3-pip build-essential cmake
pip3 install pyserial kflash
```

Get kendryte toolchain from:
<https://github.com/kendryte/kendryte-gnu-toolchain/releases>

#### Macos

``` {.bash}
brew install python3 cmake
pip3 install pyserial kflash
```

Get kendryte toolchain from:
<https://github.com/kendryte/kendryte-gnu-toolchain/releases>

### Clone repo and submodules

``` {.bash}
git clone https://github.com/sipeed/MaixPy.git
cd MaixPy
git submodule update --recursive --init
git checkout v0.6.2
```

Since MaixPy uses an ancient version where ulab's dot multiply function
is broken you will need to apply a patch and compile the firmware
yourself.

Patching won't be necessary when [MaixPy pull
\#232](https://github.com/sipeed/MaixPy/pull/232) gets through.

``` {.bash}
cd MaixPy/components/micropython/port/src/ulab/micropython-ulab
git apply M5StickV-People-Counter/maixpy/linalg.patch
```

### Configure MaixPy

``` {.bash}
cd MaixPy/projects/maixpy_m5stickv
cp M5StickV-People-Counter/global_config.mk .
```

Check these variables in `M5StickV-People-Counter/maixpy/global_config.mk`
and edit if necessary.

``` {.make}
CONFIG_TOOLCHAIN_PATH="/opt/riscv-toolchain/bin/"
CONFIG_TOOLCHAIN_PREFIX="riscv64-unknown-elf-"
```

### Build and flash MaixPy

``` {.bash}
python project.py build --config_file global_config.mk
python project.py -B goE -p /dev/ttyUSB0 -b 115200 flash
```

### Flashing model

``` {.bash}
kflash -b 115200 -B goE -p /dev/ttyUSB0 M5StickV-People-Counter/model/face_model_at_0x300000.kfpkg
```

## Uploading code

Make sure the SD-card is formatted with mbr table and FAT32 filesystem.
Copy all files from `M5StickV-People-Counter/src/` to root of the SD-card.
Then you are good to go. Sometimes it requires a second reboot until the
M5stickV will want to read from the SD-card.

Following link explains which file will be executed first: [boot script](https://wiki.sipeed.com/soft/maixpy/en/get_started/get_started_boot.html)
It's possible to edit `/flash/boot.py` by changing `boot_py` in
`MaixPy/projects/maixpy_m5stickv/builtin_py/_boot.py` and re-flashing
firmware.

## Extra

Squeeze some extra performance out of the cpu and kpu by setting the
frequency of cpu and kpu higher.(max 600Mhz) These values get saved onto
flash.

``` {.python}
from Maix import freq
freq.set(<cpu>, <kpu>) # Mhz
```

## Sources

-   [MaixPy](https://github.com/sipeed/MaixPy/blob/master/build.md)
-   [sipeed maixpy wiki](https://wiki.sipeed.com/soft/maixpy/en/index.html)
-   [micropython](https://github.com/micropython/micropython)
-   [micropython docs](https://docs.micropython.org/en/latest/index.html)
-   [m5-docs repo](https://github.com/m5stack/m5-docs/blob/master/docs/en/core/m5stickv.md)
-   [face model source](http://dl.sipeed.com/shareURL/MAIX/MaixPy/model)
-   [ulab repo](https://github.com/v923z/micropython-ulab/)
