def ascend_to_ap(target_ap, target_heading):
    import krpc

    conn = krpc.connect(name='ascend_procedure')
    vessel = conn.space_center.active_vessel
    orbit = vessel.orbit
    ref_frame = vessel.surface_reference_frame
    ref_frame_vel = vessel.orbit.body.reference_frame
    ref_frame_orbit = vessel.orbital_reference_frame
    flight = vessel.flight

    ground_clearance_altitude = 500
    ap_vector_clearance_altitude = 750

    meanaltitude = conn.add_stream(getattr, flight(ref_frame), 'mean_altitude')
    apoapsis = conn.add_stream(getattr, orbit, 'apoapsis_altitude')
    time_to_ap = conn.add_stream(getattr, orbit, 'time_to_apoapsis')
    speed = conn.add_stream(getattr, flight(ref_frame_vel), 'speed')

    ap = vessel.auto_pilot
    ap.reference_frame = vessel.orbital_reference_frame

    ap.target_pitch = 0
    ap.target_heading = target_heading

    print('Script initialized.')
    print('-------------------')
    print('Pitch set to: ' + str(ap.target_pitch))
    print('Headng set to: ' + str(ap.target_heading))

    ap.engage()

    print('-------------------')
    print('Autopilot engaged')
    print('-------------------')

    while meanaltitude < ground_clearance_altitude:
        vessel.control.throttle = 1
        print('Throttle set to maximum')
        print('handling thrust to match 40s ToA')
        if time_to_ap < 40 and vessel.control.throttle != 1:
            vessel.control.throttle += 0.01
        elif time_to_ap > 40:
            vessel.control.throttle -= 0.01

    print('---------------------------------')
    print('Ground clearence altitude reached')
    print('---------------------------------')
    while meanaltitude < ap_vector_clearance_altitude:
        ap.target_pitch = 45
        if time_to_ap < 40 and vessel.control.throttle != 1:
            vessel.control.throttle += 0.01
        elif time_to_ap > 40:
            vessel.control.throttle -= 0.01

    print('---------------------------------')
    print('Vector clearence altitude reached')
    print('---------------------------------')

    while apoapsis < target_ap:
        ap.target_direction = (0, 1, 0)
        if time_to_ap < 40 and vessel.control.throttle != 1:
            vessel.control.throttle += 0.01
        elif time_to_ap > 40:
            vessel.control.throttle -= 0.01

    ap.disengage()
    vessel.auto_pilot.sas = True
