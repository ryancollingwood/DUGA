import math
from consts.geom import DEGREES_0, DEGREES_90, DEGREES_180, DEGREES_270, DEGREES_360
from consts.geom import DEGREES_EPSILON 

#pre_calc_tan_radians = {}
pre_calc_tan_radians = []

def calc_tan_radians(x):
    return math.tan(math.radians(x))

for x in range(0,int(90/DEGREES_EPSILON)):
    #pre_calc_tan_radians[x*DEGREES_EPSILON] = calc_tan_radians(x)
    pre_calc_tan_radians.append(calc_tan_radians(x))

#for x in [DEGREES_0, DEGREES_90, DEGREES_180, DEGREES_270, DEGREES_360]:
#    pre_calc_tan_radians[x] = calc_tan_radians(x)

   
def get_tan_radains(value):
    y = value
    x = value
    mod = 1
   
    if x > DEGREES_0 and x < DEGREES_90:
        pass
    if x > DEGREES_90 and x < DEGREES_180:
        x = (DEGREES_180 - DEGREES_90 - x) + DEGREES_90
        mod = -1
    elif x > DEGREES_180 and x < DEGREES_270:
        x = (x - DEGREES_180)
        mod = 1
    elif x > DEGREES_270 and x < DEGREES_360:
        x = (DEGREES_360 - DEGREES_270 - x) + DEGREES_270
        mod = -1
    else:
        print("default", x)
    
    #pre_calc_value = pre_calc_tan_radians[x] * mod
    x_index = int(x / DEGREES_EPSILON)
    print(x, x_index)
    pre_calc_value = pre_calc_tan_radians[x_index] * mod
    calc_value = calc_tan_radians(value)

    # check if equal to the decimal points of interest
    print(value, calc_value, pre_calc_value, x, round(calc_value, 5) == round(pre_calc_value, 5))
 
def do_test():
    get_tan_radains(DEGREES_EPSILON)
    get_tan_radains(0.1)
    get_tan_radains(38)
    get_tan_radains(55)
    get_tan_radains(90)
    get_tan_radains(100)
    get_tan_radains(148)
    get_tan_radains(167)
    get_tan_radains(190)
    get_tan_radains(223)
    get_tan_radains(249)
    get_tan_radains(261)
    get_tan_radains(285)
    get_tan_radains(305)
    get_tan_radains(319)
    get_tan_radains(339)
    get_tan_radains(340)


#do_test()
def test_cases():
    print(pre_calc_tan_radians[89])
    print(pre_calc_tan_radians[91])
    print(pre_calc_tan_radians[179])
    print(pre_calc_tan_radians[181])
    print(pre_calc_tan_radians[269])
    print(pre_calc_tan_radians[271])
    print(pre_calc_tan_radians[359])
    print(pre_calc_tan_radians[1])

do_test()