// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2016 Scott Shawcroft for Adafruit Industries
//
// SPDX-License-Identifier: MIT

#include <stdint.h>

#include "py/obj.h"
#include "py/runtime.h"

#include "shared-bindings/microcontroller/Pin.h"
#include "shared-bindings/rotaryio2/__init__.h"
#include "shared-bindings/rotaryio2/IncrementalEncoder2.h"

//| """Enhanced support for reading rotation sensors
//|
//| The `rotaryio2` module contains enhanced classes to read different rotation encoding schemes. See
//| `Wikipedia's Rotary Encoder page <https://en.wikipedia.org/wiki/Rotary_encoder>`_ for more
//| background.
//|
//| This module extends the standard rotaryio with additional features like direction detection
//| and revolution counting.
//|
//| All classes change hardware state and should be deinitialized when they
//| are no longer needed if the program continues after use. To do so, either
//| call :py:meth:`!deinit` or use a context manager. See
//| :ref:`lifetime-and-contextmanagers` for more info."""

static const mp_rom_map_elem_t rotaryio2_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_rotaryio2) },
    { MP_ROM_QSTR(MP_QSTR_IncrementalEncoder2), MP_ROM_PTR(&rotaryio2_incrementalencoder2_type) },
};

static MP_DEFINE_CONST_DICT(rotaryio2_module_globals, rotaryio2_module_globals_table);

const mp_obj_module_t rotaryio2_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&rotaryio2_module_globals,
};

MP_REGISTER_MODULE(MP_QSTR_rotaryio2, rotaryio2_module);
