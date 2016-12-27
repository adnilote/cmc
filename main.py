import simpy
#from __future__ import print_function
import random

#from random import seed

env = simpy.Environment()

ONE_LVL_TIME = 3
LIFT_WAIT_TIME = 3
LIFTS_NUM = 2
LEVEL_NUM = 7
MAX_MAN_IN = 6

wait_time = 0
people_num = 0
whole_time = 0 # for transport

class Lift(object):
    def __init__(self, env, index, cur_level, dir, aims,  man_in):
        self.env = env
        self.lvl = cur_level
        # 0 - up; 1 - down; 2 - no matter; 3 - no matter, but it goes up, else - 4
        self.dir = 2
        self.aims = {-1}
        self.ind = index
        self.num_in = man_in

    def set_lvl(self, lvl):
        self.aims.add(lvl)

    def lifting(self):
        while self.lvl not in self.aims:
            if self.lvl == 0:
                self.dir = 0
            if self.lvl == LEVEL_NUM:
                self.dir = 1

            if self.dir == 0 or self.dir == 3:
                self.lvl += 1
                yield env.timeout(ONE_LVL_TIME)
            else:
                self.lvl -= 1
                yield env.timeout(ONE_LVL_TIME)

        print('lift%d stops at %d' % (self.ind, self.lvl))
        yield env.timeout(LIFT_WAIT_TIME)
        self.aims.discard(self.lvl)
        self.aims.add(-1)

        #if its not busy - dit = 2
        if self.aims == {-1}:
            if self.lvl == self.ind:
                self.dir = 2
                print('lift %d is free' % (self.ind))
            else:
            # if the lift is free, it comes to his index level
                self.aims.discard(-1)
                self.set_lvl(self.ind)
                print('lift %d goes to his place' % (self.ind))
                if self.lvl < self.ind:
                    self.dir = 3
                else:
                    self.dir = 4

    def run(self):
        while (True):
            if self.aims != {-1}:
                self.aims.discard(-1)
                yield env.process(self.lifting())
            else:
                yield env.timeout(1)


class Man(object):
    def __init__(self, index, cur_lvl, aim_lvl, env):
        self.ind = index
        self.lvl = cur_lvl
        self.aim_lvl = aim_lvl
        self.env = env

        if self.lvl < self.aim_lvl:
            self.dir = 0
        else:
            self.dir = 1

# choose a lift, wait for it, use it
    def transport(self, lifts):
        global wait_time, whole_time

        tarrive = self.env.now
        choose_lift = True
        my_lift = 0

        while choose_lift:
            nearest = -1
            lev = LEVEL_NUM + 1

            for j in range(LIFTS_NUM):
                if lifts[j].lvl == self.lvl and \
                 ((lifts[j].dir != 1 and self.dir == 0) or lifts[j].dir != 0 and self.dir == 1):
                    nearest = j
                    choose_lift = False

            # choose the nearest free lift
            if nearest == -1:
                for j in range(LIFTS_NUM):
                    if lifts[j].dir == 2 or lifts[j].dir == 3 or lifts[j].dir == 4:
                        if abs(self.lvl - lifts[j].lvl) < lev:
                            nearest = j
                            lev = abs(self.lvl - lifts[j].lvl)
                            choose_lift = False

                for i in range(LIFTS_NUM):
                    if ((lifts[i].dir == 0 or lifts[i].dir == 2 or lifts[i].dir == 3 \
                    and self.lvl >= lifts[i].lvl \
                    and lifts[i].num_in < MAX_MAN_IN  \
                    and self.dir == 0)
                    or (lifts[i].dir == 1 or lifts[i].dir == 2 or lifts[i].dir == 4 \
                    and self.lvl <= lifts[i].lvl \
                    and lifts[i].num_in < MAX_MAN_IN
                    and self.dir == 1)):
#   if -1
                        choose_lift = False
                        if abs(self.lvl - lifts[i].lvl) < lev:
                            nearest = i
                            lev = abs(self.lvl - lifts[i].lvl)
            #

            if nearest == -1:
                yield env.timeout(1)
            else:
                my_lift = nearest
                choose_lift = False

        lifts[my_lift].set_lvl(self.lvl)
        print('man%d is waiting for lift%d' % (self.ind, my_lift))
        while lifts[my_lift].lvl != self.lvl:
            yield env.timeout(1)


        get_in_lift_time = self.env.now
        wait_time += get_in_lift_time - tarrive

        lifts[my_lift].num_in += 1
        lifts[my_lift].set_lvl(self.aim_lvl)
        print('!man%d %d->%d is in lift %d' % (self.ind, self.lvl, self.aim_lvl, my_lift))

        while lifts[my_lift].lvl != self.aim_lvl:
            yield env.timeout(1)

        finish_time = self.env.now
        whole_time += finish_time - tarrive

        lifts[my_lift].num_in -= 1
        print('!!!man%d -->||%d in lift %d' % (self.ind, self.aim_lvl, my_lift))


        # Create lifts and people
def begin(env):
    print('Begin: ')
    global people_num

    lifts = []
    for i in range(LIFTS_NUM):
        new_lift = Lift(env, i, i, 2, 0, 0)
        lifts.append(new_lift)
        #print('Lift%d is in %d lvl' % (i, lifts[i].lvl))
        env.process(lifts[i].run())

    ind = 0
    while True:
        yield env.timeout(random.randint(25, 30))#
# a man appears

        ind += 1
        lvl = random.randint(0, LEVEL_NUM)
        aim_lvl = random.randint(0, LEVEL_NUM)
        while lvl == aim_lvl:
            aim_lvl = random.randint(1, LEVEL_NUM)

        man = Man(ind, lvl, aim_lvl, env)
        print('**man%d in %d -> %d' % (ind, lvl, aim_lvl))

        env.process(man.transport(lifts))
        people_num = ind

env.process(begin(env))

env.run(until=60*60)

print('Number of people who was served = %d, wait_time = %.2f, whole time they spend on transport = %d' %
      (people_num, wait_time/people_num, whole_time/people_num))











