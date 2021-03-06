# Telemetry for aircraft

# requies FAR

import krpc
import argparse
from time import sleep
from datetime import timedelta
from math import radians

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--path", help="Path for export")
parser.add_argument("-i", "--interval", help="Interval between polls", type=int, default=1)
args = parser.parse_args()

interval = args.interval
outFile = args.path

print('Argument parsed:')
print('path set to: ' + str(outFile))
print('polling interval: ' + str(interval))
print('opening connection...')
conn = krpc.connect(name='Telemetry')
print('getting active vessel...')
vessel = conn.space_center.active_vessel
ref_frame = vessel.surface_reference_frame
ref_frame_vel = vessel.orbit.body.reference_frame
ref_frame_orbit = vessel.orbital_reference_frame
flight = vessel.flight
orbit = vessel.orbit
display = conn.ui
screen_size = display.stock_canvas.rect_transform.size
canvas = display.add_canvas()
panel = canvas.add_panel()
panel.rect_transform.size = (200, 100)
panel.rect_transform.position = (110-(screen_size[0]/2), 0)
gui_message = panel.add_text('Telemetry log active')
gui_message.color = (0, 255, 0)
gui_message.rect_transform.position = (0, -20)
stop_button = panel.add_button("Stop transmission")
stop_button.rect_transform.position = (0, 20)
stop_button_clicked = conn.add_stream(getattr, stop_button, "clicked")

# add streams
print('setting up datastreams...')
missionelapsedtime = conn.add_stream(getattr, vessel, 'met')
meanaltitude = conn.add_stream(getattr, flight(ref_frame), 'mean_altitude')
apoapsis = conn.add_stream(getattr, orbit, 'apoapsis_altitude')
time_to_ap = conn.add_stream(getattr, orbit, 'time_to_apoapsis')
periapsis = conn.add_stream(getattr, orbit, 'periapsis_altitude')
time_to_pe = conn.add_stream(getattr, orbit, 'time_to_periapsis')
inclination = conn.add_stream(getattr, orbit, 'inclination')
speed = conn.add_stream(getattr, flight(ref_frame_vel), 'speed')
pitch = conn.add_stream(getattr, flight(ref_frame), 'pitch')
aoa = conn.add_stream(getattr, flight(ref_frame), 'angle_of_attack')
sideslip = conn.add_stream(getattr, flight(ref_frame), 'sideslip_angle')
temp_stat = conn.add_stream(getattr, flight(ref_frame), 'static_air_temperature')
stall_fraction = conn.add_stream(getattr, flight(ref_frame), 'stall_fraction')
drag_coefficient = conn.add_stream(getattr, flight(ref_frame_orbit), 'drag_coefficient')
lift_coefficient = conn.add_stream(getattr, flight(ref_frame_orbit), 'lift_coefficient')
atmo_density = conn.add_stream(getattr, flight(ref_frame), 'atmosphere_density')
dynamic_pressure = conn.add_stream(getattr, flight(ref_frame), 'dynamic_pressure')
ballistic_coefficient = conn.add_stream(getattr, flight(ref_frame), 'ballistic_coefficient')
mass = conn.add_stream(getattr, vessel, 'mass')
dry_mass = conn.add_stream(getattr, vessel, 'dry_mass')

# open file for write
print('setting up export...')
filename = str(vessel.name) + "_" + str(missionelapsedtime()) + "_Telemetry.csv"
filename = str(outFile) + str(filename)

gui_message_path = panel.add_text(str(filename))
gui_message_path.color = (0, 255, 0)
gui_message_path.rect_transform.position = (0, -40)
gui_message_path.size = 10


# add header

try:
    print('writing file header...')
    with open(filename, mode='a+') as exportFile:
        exportFile.write('MET;')
        exportFile.write('ASL;')
        exportFile.write('Ap;')
        exportFile.write('ToA;')
        exportFile.write('Pe;')
        exportFile.write('ToP;')
        exportFile.write('Inc;')
        exportFile.write('Speed;')
        exportFile.write('Pitch;')
        exportFile.write('AoA;')
        exportFile.write('Sideslip;')
        exportFile.write('Static temp;')
        exportFile.write('Stall;')
        exportFile.write('Drag;')
        exportFile.write('Lift;')
        exportFile.write('Atmospheric Density;')
        exportFile.write('Dynamic Pressure;')
        exportFile.write('Ballistic Coefficient;')
        exportFile.write('Mass;')
        exportFile.write('Dry mass;')
        exportFile.write(';')
        exportFile.write("\n")

# write content
    print('sending data...')
    while True:
        if stop_button_clicked():
            print('STOP signal recieved.')
            print('Telementry stream interupted by user. (stop_button_clicked)')
            break
        line = ("{met};"
                "{asl};"
                "{ap};"
                "{toa};"
                "{pe};"
                "{top};"
                "{inc};"
                "{speed};"
                "{pitch};"
                "{aoa};"
                "{sideslip};"
                "{static_temp};"
                "{stall};"
                "{drag};"
                "{lift};"
                "{atmo_density};"
                "{dyn_pressure};"
                "{ball_coeff};"
                "{mass};"
                "{dry_mass};"
                "\n").format(met=str(timedelta(seconds=int(missionelapsedtime()))),
                             asl=int(meanaltitude()),
                             ap=int(apoapsis()),
                             toa=str(timedelta(seconds=int(time_to_ap()))),
                             pe=int(periapsis()),
                             top=str(timedelta(seconds=int(time_to_pe()))),
                             inc=radians(int(inclination())),
                             speed=int(speed()),
                             pitch=int(pitch()),
                             aoa=int(aoa()),
                             sideslip=int(sideslip()),
                             static_temp=int(temp_stat()),
                             stall=stall_fraction(),
                             drag=drag_coefficient(),
                             lift=lift_coefficient(),
                             atmo_density=atmo_density(),
                             dyn_pressure=dynamic_pressure(),
                             ball_coeff=ballistic_coefficient(),
                             mass=int(mass()),
                             dry_mass=int(dry_mass()),)
        with open(filename, mode='a+') as exportFile:
            exportFile.write(line)

        sleep(interval)
except KeyboardInterrupt:
    print('Telementry stream interupted by user. (keyboardinterupt)')
finally:
    print('ending dataloop...')
    # remove streams

    missionelapsedtime.remove()
    meanaltitude.remove()
    apoapsis.remove()
    time_to_ap.remove()
    periapsis.remove()
    time_to_pe.remove()
    inclination.remove()
    speed.remove()
    pitch.remove()
    aoa.remove()
    sideslip.remove()
    temp_stat.remove()
    stall_fraction.remove()
    drag_coefficient.remove()
    lift_coefficient.remove()
    ballistic_coefficient.remove()
    mass.remove()
    dry_mass.remove()
    canvas.remove()
    # close connection
    conn.close()

print('streams and connection closed.')
