// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2017 Scott Shawcroft for Adafruit Industries
//
// SPDX-License-Identifier: MIT

#pragma once

#include "common-hal/microcontroller/Pin.h"
#include "common-hal/rotaryio2/IncrementalEncoder2.h"

extern const mp_obj_type_t rotaryio2_incrementalencoder2_type;

extern void common_hal_rotaryio2_incrementalencoder2_construct(rotaryio_incrementalencoder_obj_t *self,
    const mcu_pin_obj_t *pin_a, const mcu_pin_obj_t *pin_b);
extern void common_hal_rotaryio2_incrementalencoder2_deinit(rotaryio_incrementalencoder_obj_t *self);
extern bool common_hal_rotaryio2_incrementalencoder2_deinited(rotaryio_incrementalencoder_obj_t *self);
extern mp_int_t common_hal_rotaryio2_incrementalencoder2_get_position(rotaryio_incrementalencoder_obj_t *self);
extern void common_hal_rotaryio2_incrementalencoder2_set_position(rotaryio_incrementalencoder_obj_t *self,
    mp_int_t new_position);
extern mp_int_t common_hal_rotaryio2_incrementalencoder2_get_divisor(rotaryio_incrementalencoder_obj_t *self);
extern void common_hal_rotaryio2_incrementalencoder2_set_divisor(rotaryio_incrementalencoder_obj_t *self,
    mp_int_t new_divisor);
// New functionality
extern mp_int_t common_hal_rotaryio2_incrementalencoder2_get_direction(rotaryio_incrementalencoder_obj_t *self);
extern mp_int_t common_hal_rotaryio2_incrementalencoder2_get_revolutions(rotaryio_incrementalencoder_obj_t *self);
extern void common_hal_rotaryio2_incrementalencoder2_set_counts_per_revolution(rotaryio_incrementalencoder_obj_t *self,
    mp_int_t counts_per_rev);
extern mp_int_t common_hal_rotaryio2_incrementalencoder2_get_counts_per_revolution(rotaryio_incrementalencoder_obj_t *self);
