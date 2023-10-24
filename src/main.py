import lcd
import time
import image
import sensor
import KPU as kpu
import ulab as ul
from centroidtracker import CentroidTracker, Zone, SchmittTrigger

TASK = 0
def free(full=False):
  F = gc.mem_free()
  A = gc.mem_alloc()
  T = F+A
  P = '{0:.2f}%'.format(F/T*100)
  if not full: return P
  else : return ('Total:{}, Free:{} ({})'.format(T,F,P))

def main():
    global TASK

    err_counter = 0
    while 1:
        try:
            print('[MAIXPY]: sensor.reset')
            sensor.reset(dual_buff=True) #Reset sensor may failed, let's try some times
            break
        except:
            err_counter = err_counter + 1
            if err_counter == 20:
                lcd.draw_string(lcd.width()//2-100,lcd.height()//2-4, "Error: Sensor Init Failed", lcd.WHITE, lcd.RED)
            time.sleep(0.1)
            continue

    sensor.set_pixformat(sensor.RGB565)
    #QVGA=320x240
    sensor.set_framesize(sensor.QVGA)
    sensor.run(1)

    # Load Model File from Flash
    TASK = kpu.load(0x300000)
    anchor = (1.889,  2.5245,    2.9465, 3.94056,  3.99987,
              5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
    kpu.init_yolo2(TASK, 0.5, 0.3, 5, anchor)
    but_stu = 1

    width  = sensor.width()
    height = sensor.height()

    valid_zone = Zone((0, 0), (width, height))

    ct = CentroidTracker()
    centroids = {}

    zones = []
    threshold = 30
    zones.append(Zone((0,                       0), (width//2 - threshold//2, height), True))
    zones.append(Zone((width//2 - threshold//2, 0), (threshold,               height), False))
    zones.append(Zone((width//2 + threshold//2, 0), (width//2 - threshold//2, height), True))
    st = SchmittTrigger(zones)

    count = 0
    fps   = 0
    f     = 0
    display = False

    but_a_cur  = 1
    but_a_prev = 1

    t0 = time.ticks_ms()
    centroids = {}
    while(True):
        if (time.ticks_ms() - t0) >= 1500:
            dt = (time.ticks_ms() - t0) / 1000
            fps = f/dt
            t0 = time.ticks_ms()
            status = "FPS: {}, Centroids: {}, Free: {}"
            print(status.format(fps, len(centroids), free()))
            f = 0

        but_a_cur = but_a.value()
        if but_a_cur == 0 and but_a_prev == 1:
            display = not display
            if display == False:
                lcd.clear()
                ct.pathc = False
            else:
                ct.pathc = True
        but_a_prev = but_a_cur

        img = sensor.snapshot()
        bboxs = kpu.run_yolo2(TASK, img)
        centroids = ct.update(bboxs)
        movement = st.update(centroids)

        for x in movement:
            if x[1][-1] == 2:
                count += 1
                ct.clr_path(x[0])
            elif x[1][-1] == 0:
                count -= 1
                ct.clr_path(x[0])

        if display:
            if bboxs:
                for bbox in bboxs:
                    img.draw_rectangle(bbox.rect(), thickness=2)

            for id, centroid in centroids.items():
                # deregister centroids that went off camera
                if valid_zone.inmeis(centroid) == False:
                    ct.deregister(id)
                xy = [x for x in centroid.xy.flatten()]
                img.draw_circle(xy[0], xy[1], 6, fill=True)
                img.draw_string(xy[0] + 10, xy[1] - 5, "ID " + str(id), scale=2)

                # draw path
                if len(centroid.path) > 1:
                    for i in range(1, len(centroid.path)):
                        start = [x for x in centroid.path[i - 1].flatten()]
                        end   = [x for x in centroid.path[i].flatten()]
                        img.draw_line(start[0], start[1], end[0], end[1],
                                      (255,255,255), thickness=2)

            # draw zones
            img.draw_rectangle(zones[0].get_rect(), (255,0,0), thickness = 3)
            img.draw_rectangle(zones[2].get_rect(), (0,255,0), thickness = 3)
            # img.draw_rectangle(zones[1].get_rect(), thickness = 2)

            # fit img to screen
            img = img.resize(lcd.width(), lcd.height())

            img.draw_string(2, 2, "# " + str(count), color=(0,255,0), scale=2)
            fpss = "fps: {}".format(int(ul.floor(fps)))
            img.draw_string(2, lcd.height() - 26, fpss, color=(0,255,0), scale=2)

            lcd.display(img)

        f += 1

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:
        a = kpu.deinit(TASK)
        sys.exit()
