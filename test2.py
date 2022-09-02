# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 10:22:44 2022

@author: AlexGray
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import simpy
import random
from statistics import mean
import streamlit as st
#import numpy as np
#import pandas as pd
#import matplotlib.pyplot as plt
#import time

st.write("This is a DES model designed to estimate the time a patient spends in a system")


def patient_generator_reception(env, r_inter, mean_registration, 
                                mean_consult, mean_booktest, receptionist, gp):
    p_id = 0 
    while True:
        
        wp = activity_generator_reception(env, mean_registration, 
                                          mean_consult, mean_booktest, 
                                          receptionist, gp, p_id)

        env.process(wp)
        
        t = random.expovariate(1.0 / r_inter)

        yield env.timeout(t)
        
        p_id += 1
        

def activity_generator_reception(env, mean_registration, mean_consult, 
                                 mean_booktest, receptionist, gp, p_id):
    global list_of_queuing_times_reception 
    
    time_entered_queue_for_receptionist = env.now

    with receptionist.request() as req:

        yield req
        
        time_left_queue_for_receptionist = env.now
        time_in_queue_for_receptionist = (time_left_queue_for_receptionist -
                                   time_entered_queue_for_receptionist)
        list_of_queuing_times_reception.append(time_in_queue_for_receptionist)
        print (f"Patient {p_id} queued for the reception for {time_in_queue_for_receptionist:.1f} mins")
        
        sampled_registration_time = random.expovariate(1.0 / mean_registration)

        yield env.timeout(sampled_registration_time)
        
    time_entered_queue_for_consult = env.now

    with gp.request() as req:
        
        global list_of_queuing_times_consult

        yield req
        
        time_left_queue_for_consult = env.now
        time_in_queue_for_consult = (time_left_queue_for_consult -
                                    time_entered_queue_for_consult)
        list_of_queuing_times_consult.append(time_in_queue_for_consult)
        print (f"Patient {p_id} queued for consultation for",
               f"{time_in_queue_for_consult:.1f} minutes.")
        
        # Sample the time spent in triage
        sampled_consult_time = random.expovariate(1.0 / mean_consult)
        
        # Freeze until that time has elapsed
        yield env.timeout(sampled_consult_time)   
        
        percentagebooktest=random.uniform(0,1)
        if percentagebooktest<=0.25:
        
            time_entered_queue_for_booktest = env.now
                
            # Request a nurse
            with receptionist.request() as req:
                
                global list_of_queuing_times_booktest
                # Freeze until the request can be met
                yield req
                    
                time_left_queue_for_booktest = env.now
                time_in_queue_for_booktest = (time_left_queue_for_booktest -
                                                time_entered_queue_for_booktest)
                list_of_queuing_times_booktest.append(time_in_queue_for_booktest)
                print (f"Patient {p_id} queued for booking a test for",
                          f"{time_in_queue_for_booktest:.1f} minutes.")
                    
                # Sample the time spent in triage
                sampled_booktest_time = random.expovariate(1.0 / mean_booktest)
                    
                # Freeze until that time has elapsed
                yield env.timeout(sampled_booktest_time) 
        
        else:
            time_in_queue_for_booktest=0
            sampled_booktest_time=0
        
        timeinsystem=time_in_queue_for_booktest+time_in_queue_for_consult+time_in_queue_for_receptionist+sampled_booktest_time+sampled_consult_time+sampled_registration_time
        print (f"The total time the patient {p_id} spent in the system is {timeinsystem}")
        
        
env = simpy.Environment()

st.write("Please use the below slider to add the number of nurses avaiable in the system")
x = st.slider('nurses', min_value=1, max_value=20)  # 👈 this is a widget

st.write("Please use the below slider to add the number of nurses avaiable in the system")
y = st.slider('gp', min_value=1, max_value=20)  # 👈 this is a widget

receptionist = simpy.Resource(env, capacity=x)
gp = simpy.Resource(env, capacity=y)

r_inter = 3

st.write("Please use the input below to add the mean registration time")
registration_time=st.text_input("reg time", key="1")

st.write("Please use the input below to add the mean consultant time")
consultant_time=st.text_input("consultant time", key="2")

st.write("Please use the input below to add the mean time to book a test")
test_book_time=st.text_input("test book time", key="3")


mean_registration = float(registration_time)
mean_consult = float(consultant_time)
mean_booktest = float(test_book_time)

list_of_queuing_times_reception=[]
list_of_queuing_times_consult=[]
list_of_queuing_times_booktest=[]

env.process(patient_generator_reception(env, r_inter, mean_registration, 
                                mean_consult, mean_booktest, receptionist, gp))

env.run(until=480)

averagereception=mean(list_of_queuing_times_reception)

averageconsult=mean(list_of_queuing_times_consult)

averagebooktest=mean(list_of_queuing_times_booktest)

#receptionarray<-np.array(list_of_queuing_times_reception)
#consultarray<-np.asarray(list_of_queuing_times_consult)
#booktestarray<-np.asarray(list_of_queuing_times_booktest)
                                                    
st.line_chart(list_of_queuing_times_reception)
st.line_chart(list_of_queuing_times_consult)
st.line_chart(list_of_queuing_times_booktest)

st.write("The average queue time for the reception is", averagereception)

st.write("The average queue time for the consultation is", averageconsult)

st.write("The average queue time for booking a test is", averagebooktest)

