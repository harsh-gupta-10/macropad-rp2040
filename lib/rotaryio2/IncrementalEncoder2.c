// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2018 Scott Shawcroft for Adafruit Industries
//
// SPDX-License-Identifier: MIT

#include <stdint.h>

#include "shared/runtime/context_manager_helpers.h"
#include "py/objproperty.h"
#include "py/runtime.h"
#include "py/runtime0.h"
#include "shared-bindings/microcontroller/Pin.h"
#include "shared-bindings/rotaryio/IncrementalEncoder2.h"
#include "shared-bindings/util.h"

//| class IncrementalEncoder:
//|     """IncrementalEncoder determines the relative rotational position based on two series of pulses.
//|     It assumes that the encoder's common pin(s) are connected to ground,and enables pull-ups on
//|     pin_a and pin_b."""
//|
//|     def __init__(
//|         self, pin_a: microcontroller.Pin, pin_b: microcontroller.Pin, divisor: int = 4
//|     ) -> None:
//|         """Create an IncrementalEncoder object associated with the given pins. It tracks the positional
//|         state of an incremental rotary encoder (also known as a quadrature encoder.) Position is
//|         relative to the position when the object is constructed.
//|
//|         :param ~microcontroller.Pin pin_a: First pin to read pulses from.
//|         :param ~microcontroller.Pin pin_b: Second pin to read pulses from.
//|         :param int divisor: The divisor of the quadrature signal.
//|
//|         For example::
//|
//|           import rotaryio
//|           import time
//|           from board import *
//|
//|           enc = rotaryio.IncrementalEncoder(D1, D2)
//|           last_position = None
//|           while True:
//|               position = enc.position
//|               if last_position == None or position != last_position:
//|                   print(position)
//|               last_position = position"""
//|         ...
//|
static mp_obj_t rotaryio_incrementalencoder_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    enum { ARG_pin_a, ARG_pin_b, ARG_divisor };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_pin_a, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_pin_b, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_divisor, MP_ARG_INT, { .u_int = 4 } },
    };
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    const mcu_pin_obj_t *pin_a = validate_obj_is_free_pin(args[ARG_pin_a].u_obj, MP_QSTR_pin_a);
    const mcu_pin_obj_t *pin_b = validate_obj_is_free_pin(args[ARG_pin_b].u_obj, MP_QSTR_pin_b);

    rotaryio_incrementalencoder_obj_t *self = mp_obj_malloc_with_finaliser(rotaryio_incrementalencoder_obj_t, &rotaryio_incrementalencoder_type);

    common_hal_rotaryio_incrementalencoder_construct(self, pin_a, pin_b);
    common_hal_rotaryio_incrementalencoder_set_divisor(self, args[ARG_divisor].u_int);

    return MP_OBJ_FROM_PTR(self);
}

//|     def deinit(self) -> None:
//|         """Deinitializes the IncrementalEncoder and releases any hardware resources for reuse."""
//|         ...
//|
static mp_obj_t rotaryio_incrementalencoder_deinit(mp_obj_t self_in) {
    rotaryio_incrementalencoder_obj_t *self = MP_OBJ_TO_PTR(self_in);
    common_hal_rotaryio_incrementalencoder_deinit(self);
    return mp_const_none;
}
static MP_DEFINE_CONST_FUN_OBJ_1(rotaryio_incrementalencoder_deinit_obj, rotaryio_incrementalencoder_deinit);

static void check_for_deinit(rotaryio_incrementalencoder_obj_t *self) {
    if (common_hal_rotaryio_incrementalencoder_deinited(self)) {
        raise_deinited_error();
    }
}

//|     def __enter__(self) -> IncrementalEncoder:
//|         """No-op used by Context Managers."""
//|         ...
//|
//  Provided by context manager helper.

//|     def __exit__(self) -> None:
//|         """Automatically deinitializes the hardware when exiting a context. See
//|         :ref:`lifetime-and-contextmanagers` for more info."""
//|         ...
//|
//  Provided by context manager helper.


//|     divisor: int
//|     """The divisor of the quadrature signal.  Use 1 for encoders without
//|     detents, or encoders with 4 detents per cycle.  Use 2 for encoders with 2
//|     detents per cycle.  Use 4 for encoders with 1 detent per cycle."""
static mp_obj_t rotaryio_incrementalencoder_obj_get_divisor(mp_obj_t self_in) {
    rotaryio_incrementalencoder_obj_t *self = MP_OBJ_TO_PTR(self_in);
    check_for_deinit(self);

    return mp_obj_new_int(common_hal_rotaryio_incrementalencoder_get_divisor(self));
}
MP_DEFINE_CONST_FUN_OBJ_1(rotaryio_incrementalencoder_get_divisor_obj, rotaryio_incrementalencoder_obj_get_divisor);

static mp_obj_t rotaryio_incrementalencoder_obj_set_divisor(mp_obj_t self_in, mp_obj_t new_divisor) {
    rotaryio_incrementalencoder_obj_t *self = MP_OBJ_TO_PTR(self_in);
    check_for_deinit(self);

    common_hal_rotaryio_incrementalencoder_set_divisor(self, mp_obj_get_int(new_divisor));
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(rotaryio_incrementalencoder_set_divisor_obj, rotaryio_incrementalencoder_obj_set_divisor);

MP_PROPERTY_GETSET(rotaryio_incrementalencoder_divisor_obj,
    (mp_obj_t)&rotaryio_incrementalencoder_get_divisor_obj,
    (mp_obj_t)&rotaryio_incrementalencoder_set_divisor_obj);

//|     position: int
//|     """The current position in terms of pulses. The number of pulses per rotation is defined by the
//|     specific hardware and by the divisor."""
//|
//|
static mp_obj_t rotaryio_incrementalencoder_obj_get_position(mp_obj_t self_in) {
    rotaryio_incrementalencoder_obj_t *self = MP_OBJ_TO_PTR(self_in);
    check_for_deinit(self);

    return mp_obj_new_int(common_hal_rotaryio_incrementalencoder_get_position(self));
}
MP_DEFINE_CONST_FUN_OBJ_1(rotaryio_incrementalencoder_get_position_obj, rotaryio_incrementalencoder_obj_get_position);

static mp_obj_t rotaryio_incrementalencoder_obj_set_position(mp_obj_t self_in, mp_obj_t new_position) {
    rotaryio_incrementalencoder_obj_t *self = MP_OBJ_TO_PTR(self_in);
    check_for_deinit(self);

    common_hal_rotaryio_incrementalencoder_set_position(self, mp_obj_get_int(new_position));
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(rotaryio_incrementalencoder_set_position_obj, rotaryio_incrementalencoder_obj_set_position);

MP_PROPERTY_GETSET(rotaryio_incrementalencoder_position_obj,
    (mp_obj_t)&rotaryio_incrementalencoder_get_position_obj,
    (mp_obj_t)&rotaryio_incrementalencoder_set_position_obj);

static const mp_rom_map_elem_t rotaryio_incrementalencoder_locals_dict_table[] = {
    // Methods
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&rotaryio_incrementalencoder_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR___del__), MP_ROM_PTR(&rotaryio_incrementalencoder_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR___enter__), MP_ROM_PTR(&default___enter___obj) },
    { MP_ROM_QSTR(MP_QSTR___exit__), MP_ROM_PTR(&default___exit___obj) },
    { MP_ROM_QSTR(MP_QSTR_position), MP_ROM_PTR(&rotaryio_incrementalencoder_position_obj) },
    { MP_ROM_QSTR(MP_QSTR_divisor), MP_ROM_PTR(&rotaryio_incrementalencoder_divisor_obj) },
};
static MP_DEFINE_CONST_DICT(rotaryio_incrementalencoder_locals_dict, rotaryio_incrementalencoder_locals_dict_table);

MP_DEFINE_CONST_OBJ_TYPE(
    rotaryio_incrementalencoder_type,
    MP_QSTR_IncrementalEncoder,
    MP_TYPE_FLAG_HAS_SPECIAL_ACCESSORS,
    make_new, rotaryio_incrementalencoder_make_new,
    locals_dict, &rotaryio_incrementalencoder_locals_dict
    );

// This file is part of the CircuitPython project: https://circuitpython.org
//
// SPDX-FileCopyrightText: Copyright (c) 2018 Scott Shawcroft for Adafruit Industries
//
// SPDX-License-Identifier: MIT

#include <stdint.h>

#include "shared/runtime/context_manager_helpers.h"
#include "py/objproperty.h"
#include "py/runtime.h"
#include "py/runtime0.h"
#include "shared-bindings/microcontroller/Pin.h"
#include "shared-bindings/rotaryio2/IncrementalEncoder2.h"
#include "shared-bindings/util.h"

//| class IncrementalEncoder2:
//|     """Enhanced IncrementalEncoder that determines the relative rotational position based on two series of pulses.
//|     It assumes that the encoder's common pin(s) are connected to ground, and enables pull-ups on
//|     pin_a and pin_b. Adds features for direction detection and revolution counting."""
//|
//|     def __init__(
//|         self, pin_a: microcontroller.Pin, pin_b: microcontroller.Pin, divisor: int = 4, 
//|         counts_per_revolution: int = 24
//|     ) -> None:
//|         """Create an IncrementalEncoder2 object associated with the given pins. It tracks the positional
//|         state of an incremental rotary encoder (also known as a quadrature encoder.) Position is
//|         relative to the position when the object is constructed.
//|
//|         :param ~microcontroller.Pin pin_a: First pin to read pulses from.
//|         :param ~microcontroller.Pin pin_b: Second pin to read pulses from.
//|         :param int divisor: The divisor of the quadrature signal.
//|         :param int counts_per_revolution: The number of counts that make up a full revolution.
//|
//|         For example::
//|
//|           import rotaryio2
//|           import time
//|           from board import *
//|
//|           enc = rotaryio2.IncrementalEncoder2(D1, D2)
//|           last_position = None
//|           while True:
//|               position = enc.position
//|               if last_position == None or position != last_position:
//|                   print(f"Position: {position}, Direction: {enc.direction}, Revolutions: {enc.revolutions}")
//|               last_position = position"""
//|         ...
//|
static mp_obj_t rotaryio2_incrementalencoder2_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *all_args) {
    enum { ARG_pin_a, ARG_pin_b, ARG_divisor, ARG_counts_per_revolution };
    static const mp_arg_t allowed_args[] = {
        { MP_QSTR_pin_a, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_pin_b, MP_ARG_REQUIRED | MP_ARG_OBJ },
        { MP_QSTR_divisor, MP_ARG_INT, { .u_int = 4 } },
        { MP_QSTR_counts_per_revolution, MP_ARG_INT, { .u_int = 24 } },
    };
    mp_arg_val_t args[MP_ARRAY_SIZE(allowed_args)];
    mp_arg_parse_all_kw_array(n_args, n_kw, all_args, MP_ARRAY_SIZE(allowed_args), allowed_args, args);

    const mcu_pin_obj_t *pin_a = validate_obj_is_free_pin(args[ARG_pin_a].u_obj, MP_QSTR_pin_a);
    const mcu_pin_obj_t *pin_b = validate_obj_is_free_pin(args[ARG_pin_b].u_obj, MP_QSTR_pin_b);

    rotaryio_incrementalencoder_obj_t *self = mp_obj_malloc_with_finaliser(rotaryio_incrementalencoder_obj_t, &rotaryio2_incrementalencoder2_type);

    common_hal_rotaryio2_incrementalencoder2_construct(self, pin_a, pin_b);
    common_hal_rotaryio2_incrementalencoder2_set_divisor(self, args[ARG_divisor].u_int);
    common_hal_rotaryio2_incrementalencoder2_set_counts_per_revolution(self, args[ARG_counts_per_revolution].u_int);

    return MP_OBJ_FROM_PTR(self);
}

//|     direction: int
//|     """The direction of the last movement. 1 for clockwise, -1 for counter-clockwise, 0 for no movement."""
static mp_obj_t rotaryio2_incrementalencoder2_obj_get_direction(mp_obj_t self_in) {
    rotaryio_incrementalencoder_obj_t *self = MP_OBJ_TO_PTR(self_in);
    check_for_deinit(self);

    return mp_obj_new_int(common_hal_rotaryio2_incrementalencoder2_get_direction(self));
}
MP_DEFINE_CONST_FUN_OBJ_1(rotaryio2_incrementalencoder2_get_direction_obj, rotaryio2_incrementalencoder2_obj_get_direction);

MP_PROPERTY_GETTER(rotaryio2_incrementalencoder2_direction_obj, 
    (mp_obj_t)&rotaryio2_incrementalencoder2_get_direction_obj);

//|     revolutions: int
//|     """The number of full revolutions tracked according to counts_per_revolution."""
static mp_obj_t rotaryio2_incrementalencoder2_obj_get_revolutions(mp_obj_t self_in) {
    rotaryio_incrementalencoder_obj_t *self = MP_OBJ_TO_PTR(self_in);
    check_for_deinit(self);

    return mp_obj_new_int(common_hal_rotaryio2_incrementalencoder2_get_revolutions(self));
}
MP_DEFINE_CONST_FUN_OBJ_1(rotaryio2_incrementalencoder2_get_revolutions_obj, rotaryio2_incrementalencoder2_obj_get_revolutions);

MP_PROPERTY_GETTER(rotaryio2_incrementalencoder2_revolutions_obj,
    (mp_obj_t)&rotaryio2_incrementalencoder2_get_revolutions_obj);

//|     counts_per_revolution: int
//|     """The number of counts that make up a full revolution."""
static mp_obj_t rotaryio2_incrementalencoder2_obj_get_counts_per_revolution(mp_obj_t self_in) {
    rotaryio_incrementalencoder_obj_t *self = MP_OBJ_TO_PTR(self_in);
    check_for_deinit(self);

    return mp_obj_new_int(common_hal_rotaryio2_incrementalencoder2_get_counts_per_revolution(self));
}
MP_DEFINE_CONST_FUN_OBJ_1(rotaryio2_incrementalencoder2_get_counts_per_revolution_obj, rotaryio2_incrementalencoder2_obj_get_counts_per_revolution);

static mp_obj_t rotaryio2_incrementalencoder2_obj_set_counts_per_revolution(mp_obj_t self_in, mp_obj_t new_counts) {
    rotaryio_incrementalencoder_obj_t *self = MP_OBJ_TO_PTR(self_in);
    check_for_deinit(self);

    common_hal_rotaryio2_incrementalencoder2_set_counts_per_revolution(self, mp_obj_get_int(new_counts));
    return mp_const_none;
}
MP_DEFINE_CONST_FUN_OBJ_2(rotaryio2_incrementalencoder2_set_counts_per_revolution_obj, rotaryio2_incrementalencoder2_obj_set_counts_per_revolution);

MP_PROPERTY_GETSET(rotaryio2_incrementalencoder2_counts_per_revolution_obj,
    (mp_obj_t)&rotaryio2_incrementalencoder2_get_counts_per_revolution_obj,
    (mp_obj_t)&rotaryio2_incrementalencoder2_set_counts_per_revolution_obj);

static const mp_rom_map_elem_t rotaryio2_incrementalencoder2_locals_dict_table[] = {
    // Methods
    { MP_ROM_QSTR(MP_QSTR_deinit), MP_ROM_PTR(&rotaryio_incrementalencoder_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR___del__), MP_ROM_PTR(&rotaryio_incrementalencoder_deinit_obj) },
    { MP_ROM_QSTR(MP_QSTR___enter__), MP_ROM_PTR(&default___enter___obj) },
    { MP_ROM_QSTR(MP_QSTR___exit__), MP_ROM_PTR(&default___exit___obj) },
    { MP_ROM_QSTR(MP_QSTR_position), MP_ROM_PTR(&rotaryio_incrementalencoder_position_obj) },
    { MP_ROM_QSTR(MP_QSTR_divisor), MP_ROM_PTR(&rotaryio_incrementalencoder_divisor_obj) },
    // New properties
    { MP_ROM_QSTR(MP_QSTR_direction), MP_ROM_PTR(&rotaryio2_incrementalencoder2_direction_obj) },
    { MP_ROM_QSTR(MP_QSTR_revolutions), MP_ROM_PTR(&rotaryio2_incrementalencoder2_revolutions_obj) },
    { MP_ROM_QSTR(MP_QSTR_counts_per_revolution), MP_ROM_PTR(&rotaryio2_incrementalencoder2_counts_per_revolution_obj) },
};
static MP_DEFINE_CONST_DICT(rotaryio2_incrementalencoder2_locals_dict, rotaryio2_incrementalencoder2_locals_dict_table);

MP_DEFINE_CONST_OBJ_TYPE(
    rotaryio2_incrementalencoder2_type,
    MP_QSTR_IncrementalEncoder2,
    MP_TYPE_FLAG_HAS_SPECIAL_ACCESSORS,
    make_new, rotaryio2_incrementalencoder2_make_new,
    locals_dict, &rotaryio2_incrementalencoder2_locals_dict
    );
