// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2024 for CircuitPython Contributors
//
// SPDX-License-Identifier: MIT

#pragma once

#include "py/obj.h"
#include "common-hal/microcontroller/Pin.h"

typedef struct {
    mp_obj_base_t base;
    const mcu_pin_obj_t *pin_a;
    const mcu_pin_obj_t *pin_b;
    mp_int_t position;
    mp_int_t divisor;
    bool first_read;
    
    // New fields for enhanced functionality
    mp_int_t last_position;
    mp_int_t direction;
    mp_int_t counts_per_revolution;
    mp_int_t revolutions;
} rotaryio_incrementalencoder_obj_t;
