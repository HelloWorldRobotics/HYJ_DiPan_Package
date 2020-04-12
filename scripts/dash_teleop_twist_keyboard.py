#!/usr/bin/env python
#HelloBot1.0_teleop_twist_keyboard

# keyBoardFlag,stopFlag here is added by chen_ran, to accomplish 
# the switch between teleop and purepursuit. 

import roslib; roslib.load_manifest('HYJ_DiPan_Package')
import rospy

from geometry_msgs.msg import Twist, TwistStamped
import time
from std_msgs.msg import Int32

import sys, select, termios, tty

global velocity_linear
global velocity_angular

msg = """
Reading from the keyboard  and Publishing to Twist!
---------------------------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

For Holonomic mode (strafing), hold down the shift key:
---------------------------
   U    I    O
   J    K    L
   M    <    >

t : up (+z)
b : down (-z)

anything else : stop

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%

CTRL-C to quit

1 : from purepursuit mode to teleop mode
0 : to purepursuit mode 
9 : emergency mode, hellobot stop
"""

moveBindings = {
		'i':(1,0,0,0),
		'o':(1,0,0,-1),
		'j':(0,0,0,1),
		'l':(0,0,0,-1),
		'u':(1,0,0,1),
		',':(-1,0,0,0),
		'.':(-1,0,0,1),
		'm':(-1,0,0,-1),
		'O':(1,-1,0,0),
		'I':(1,0,0,0),
		'J':(0,1,0,0),
		'L':(0,-1,0,0),
		'U':(1,1,0,0),
		'<':(-1,0,0,0),
		'>':(-1,-1,0,0),
		'M':(-1,1,0,0),
		't':(0,0,1,0),
		'b':(0,0,-1,0),
	       }

speedBindings={
		'q':(1.1,1.1),
		'z':(.9,.9),
		'w':(1.1,1),
		'x':(.9,1),
		'e':(1,1.1),
		'c':(1,.9),
	      }

keyBoardFlag={
			    '1':(1)		
			 }
purePursuitFlag={
			'0':(1)
		}
stop_flag={
	  	'p':(1)
  	  }
emergencyFlag={
			'9':(1)
		}
def getKey():
	tty.setraw(sys.stdin.fileno())
	select.select([sys.stdin], [], [], 0)
	key = sys.stdin.read(1)
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
	return key


def vels(speed,turn):
	return "currently:\tspeed %s\tturn %s " % (speed,turn)

def velocity_msg(msg):
	global velocity_linear_x
	global velocity_linear_y
	global velocity_linear_z 
	global velocity_angular_x
	global velocity_angular_x
	global velocity_angular_y
	global velocity_angular_z
	velocity_linear_x = msg.twist.linear.x
	velocity_linear_y = msg.twist.linear.y
	velocity_linear_z = msg.twist.linear.z
	velocity_angular_x = msg.twist.angular.x
	velocity_angular_y = msg.twist.angular.y
	velocity_angular_z = msg.twist.angular.z
if __name__=="__main__":
    	settings = termios.tcgetattr(sys.stdin)
	
	#pub = rospy.Publisher('/planner/cmd_vel', Twist, queue_size = 1)
	pub = rospy.Publisher('/cmd_vel', Twist, queue_size = 1)
	keyFlagpub = rospy.Publisher('/keyBoardFlag', Int32, queue_size = 1)          
        sub = rospy.Subscriber('/twist_cmd', TwistStamped, velocity_msg)
	#pub = rospy.Publisher('/catvehicle/cmd_vel', Twist, queue_size = 1)	
	rospy.init_node('teleop_twist_keyboard')

	speed = rospy.get_param("~speed", 0.15)
	turn = rospy.get_param("~turn", 0.3)
	x = 0
	y = 0
	z = 0
	th = 0
	status = 0
	keyFlag = Int32()
        keyBoard_flag = 1
	twist = Twist()
	twist_teleop = Twist()
	try:
		print msg
		print vels(speed,turn)
		while(1):
			key = getKey()
			if key in moveBindings.keys():
				x = moveBindings[key][0]
				y = moveBindings[key][1]
				z = moveBindings[key][2]
				th = moveBindings[key][3]
               			stop_flag = 0
			elif key in speedBindings.keys():
				speed = speed * speedBindings[key][0]
				turn = turn * speedBindings[key][1]
				print vels(speed,turn)
				if (status == 14):
					print msg
				status = (status + 1) % 15
				stop_flag = 0
			elif key in keyBoardFlag.keys():                     
				keyBoard_flag = 1           
				print ("now controlling robot manually")
				stop_flag = 0
			elif key in emergencyFlag.keys():
				keyFlag.data = 1
				print("emergency mode")
				keyBoard_flag = 1
				stop_flag = 1			

			elif key in purePursuitFlag.keys():		     
				keyFlag.data = 0
				keyBoard_flag = 0
				print ("now robot moving automatically")
			else:
				x = 0
				y = 0
				z = 0
				th = 0
				if (key == '\x03'):
					break
			if keyBoard_flag == 1:         			     
				keyFlag.data = 1
				keyFlagpub.publish(keyFlag)
			else:
				print ("now robot moving automatically")			
				keyFlagpub.publish(keyFlag)
                        if stop_flag == 1:
				twist_teleop.linear.x = 0; twist_teleop.linear.y = 0; twist_teleop.linear.z = 0;
                                twist_teleop.angular.x = 0; twist_teleop.angular.y = 0; twist_teleop.angular.z = 0;
                            	keyFlagpub.publish(keyFlag)
                            	pub.publish(twist_teleop)
			else:
				twist_teleop.linear.x = x*speed; twist_teleop.linear.y = y*speed; twist_teleop.linear.z = z*speed;
                        	twist_teleop.angular.x = 0; twist_teleop.angular.y = 0; twist_teleop.angular.z = th*turn
                        	keyFlagpub.publish(keyFlag)
                        	pub.publish(twist_teleop)

	except:
                print("e")

	finally:
		print("finally")
		twist = Twist()
		twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
		twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
		pub.publish(twist)

    		termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

