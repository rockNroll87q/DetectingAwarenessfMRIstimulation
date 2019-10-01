#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Wed Sep 18 15:39:44 2019

@author: Michele Svanera

University of Glasgow.

Stimulation code for the fMRI experiment "Detecting Awareness in the Vegetative State" Owen06.

Three blocks:
* One task involved imagining playing a game of tennis (supplementary motor area activity).
* the other involved imagining visiting all of the rooms of her house, 
  starting from the front door (parahippocampal gyrus, the posterior parietal cortex, and 
  the lateral premotor cortex activity).
* Don't think about faces.
 
"""

################################################################################################################
## Imports 

from __future__ import absolute_import, division, print_function


from psychopy import visual, core, event, logging
from psychopy import prefs as pyschopy_prefs
from psychopy import gui  #fetch default gui handler (qt if available)
from psychopy.hardware.emulator import launchScan
from psychopy import sound

import os, sys
from datetime import datetime as dt
from time import gmtime, strftime
import numpy as np


################################################################################################################
## Paths and Constants

Fullscreen = False
Screen_dimensions = (500,500)

Path_in_sounds = '../in/'
Root_dir='../'     #'D:/Mucklis_lab/MIB/stimulus_src/'
Dir_save = Root_dir + 'out/'
Log_name = 'myLogFile.log'
Frames_durations_name = 'frames_durations.npy'

# Messages
init_mess_1 = "Please follow displayed instructions. Press a key to continue.."
scanner_message = "Waiting for the scanner..."
final_message = "This is the end of the experiment."

# Block details
blocks_number = 4           # N blocks for condition "Tennis" and N "house"
inter_blocks_length = 5           # sec.
block_length = inter_blocks_length           # sec.

string_tennis = "imagine to play a game of tennis"
sounds_filename_tennis = 'tennis.ogg'

string_house = "imagine to visit all of the rooms of your house, starting from the front door"
sounds_filename_house = 'room.ogg'

string_faces = "don't think about faces"
sounds_filename_faces = 'faces.ogg'



################################################################################################################
## Functions


def createOutFolder(path_out):
    if not os.path.exists(path_out):
        try:
            os.makedirs(path_out)
        except Exception as e:
            print('Problem with creating an *out* folder, check permissions: ',e)    
    else:
        n_folder_name = 1
        path_out_new = path_out + "_" + str(n_folder_name)
        while(os.path.exists(path_out_new) is True):
            n_folder_name += 1
            path_out_new = path_out + "_" + str(n_folder_name)
        try:
            os.makedirs(path_out_new)
        except Exception as e:
            print('Problem with creating an *out* folder, check permissions: ',e)      
        path_out = path_out_new
    path_out += '/'
    
    return path_out


def initialBox():    
    dlg = gui.Dlg(title="Experiment")
    dlg.addText('Experiment detail', color='Blue')
    dlg.addField('Date (mm/dd/yy):', dt.today().strftime('%Y-%m-%d'))
    dlg.addField('Operator:', 'MS')
    
    dlg.addText('Subject Info', color='Blue')
    dlg.addField('Subject-code:', 'FFE21')
    dlg.addField('Age:', tip='18 to 00')
    dlg.addField('Gender:', choices=['male', 'female'])

    dlg.addText('Scanner', color='Blue')
    dlg.addField('Scanner:', True)    
    dlg.addField('TR:', '2.0')
    dlg.addField('Volumes:', '5')
    dlg.addField('skip:', '0')
    dlg.addField('sync:', 's')

    all_infos = dlg.show()  # you have to call show() for a Dlg (automatic with a DlgFromDict)
    if dlg.OK:
        return all_infos
    else:
        return None    
    

def main_block_design(win,globalClock):

    ############## Stimuli preparation ##############

    # Fixation cross preparation
    fixation = visual.Circle(win,radius=10,lineColor='white',fillColor='white',units='pix')

    subject_instructions = visual.TextStim(win,pos=[0,0],text='',alignVert='center',wrapWidth=1.5)

    tennis_sound = sound.Sound(Path_in_sounds + sounds_filename_tennis)
    house_sound = sound.Sound(Path_in_sounds + sounds_filename_house)
    faces_sound = sound.Sound(Path_in_sounds + sounds_filename_faces)
    
    tennis = [string_tennis, tennis_sound]
    house = [string_house, house_sound]
    faces = [string_faces, faces_sound]


    ############## Definitions/Functions ##############
    
    ## handle Rkey presses each frame
    def escapeCondition():              
        for key in event.getKeys():
            if key in ['escape', 'q']:
                return False
        return True
    
    
    ## Display just fixation
    def displayFixation(win,fixation_time=2,break_flag=True):

        timer_fixation = core.CountdownTimer(fixation_time)    
        while (timer_fixation.getTime() > 0 and break_flag==True):    

            fixation.draw()                                        
            win.flip()                  # Update screen
            break_flag = escapeCondition()                  
        return break_flag


    ## Display just a message
    def displayInstruction(win,string_instruction,sound,string_time=2,break_flag=True):

        timer_string = core.CountdownTimer(string_time)    
        sound.play()
        while (timer_string.getTime() > 0 and break_flag==True):    

            subject_instructions.text = string_instruction
            subject_instructions.draw()            
            win.flip()                  # Update screen
            break_flag = escapeCondition()                  
        return break_flag
 

    ## Initialise experiment: select trails and log them
    block_order = np.random.permutation([tennis, house, faces] * blocks_number)
    logging.data("Trails order:")
    logging.data(block_order)
    
    
    ############## Exp. begin ##############

    # Display first set of instructions and wait
    message1 = visual.TextStim(win, pos=[0,0],text=init_mess_1,alignVert='center',
                               wrapWidth=1.5)
    message1.size = .5
    message1.draw()
    win.flip()
    event.waitKeys()    #pause until there's a keypress

    # Waiting for the scanner
    if SCANNER:
        message3 = visual.TextStim(win,pos=[0,0.25],text=scanner_message,alignVert='center',
                                   wrapWidth=1.5)
        message3.size = .5
        message3.draw()
        win.flip()
        while 1:
            allKeys = event.getKeys()
            if MR_settings['sync'] in allKeys:
                break
            
    # Start run
    experiment_begin = dt.now()

    inizio = globalClock.getTime()
    logging.data('Begin of the experiment (trigger) at: %.6f' % (inizio))
    
    # Run experiment a 'run' at the time    
    for i_block in block_order:
        
        i_block_string = i_block[0]
        i_block_sound = i_block[1]

        logging.data('*** Run: ' + str(i_block_string) + ' ***')

        # Fixation
        if displayFixation(win,fixation_time=inter_blocks_length) == False: break
        
        # Show condition "tennis" or "house"
        if displayInstruction(win,string_instruction=i_block_string,
                              string_time=block_length,sound=i_block_sound) == False: break
            
    # Display final fixation
    if displayFixation(win,fixation_time=inter_blocks_length) == False: return
    
    # Display final message
    message4 = visual.TextStim(win,pos=[0,0.25],text=final_message,alignVert='center',
                               wrapWidth=1.5)
    message4.size = .5
    message4.draw()
    win.flip()
    core.wait(3)
    
    logging.data('***** End *****\n')
    
    logging.data('Total time spent: %s' % (dt.now() - experiment_begin))
    logging.data('Every frame duration saved in %s' % (path_out+Frames_durations_name))

    return



if __name__ == "__main__":  

    # Dialog box to setup initial info
    all_infos = initialBox()

    if all_infos == None:
        sys.exit(0)
    else:
        today_date, operator, subject_code, subject_age, subject_gender,\
                SCANNER, Tr, Volumes, Skip, Sync = all_infos
                          
    # Prepare out folder
    path_out = Dir_save + today_date + '_' + subject_code
    path_out = createOutFolder(path_out)
                
    # Set the log module to report warnings to the standard output window
    globalClock = core.Clock()
    logging.setDefaultClock(globalClock)
    logging.console.setLevel(logging.WARNING)
    lastLog=logging.LogFile(path_out+Log_name,level=logging.DATA,filemode='w',encoding='utf8')
    logging.data("------------- " + strftime("%Y-%m-%d %H:%M:%S", gmtime()) + " -------------")
    logging.data(pyschopy_prefs)
    logging.data("Saving in folder: " + path_out)
    logging.data("Operator: " + operator + "\n")    
    logging.data("Subject. Code: " + subject_code + " - Age: " + str(subject_age) + " - Gender: " + subject_gender) 
    logging.data("Scanner. TR: " + Tr + " - Volumes: " + Volumes + " - Skip: " + Skip + " - Sync: " + Sync + "\n") 
    logging.data("Using %s (with %s driver) for sounds" % (sound.audioLib, sound.audioDriver) + '\n')
    logging.data('***** Starting *****')
    

    # Start window
    win = visual.Window(Screen_dimensions, monitor="mon", units="norm", fullscr=Fullscreen,
                        color='black', allowStencil=True,screen=1)
    win.recordFrameIntervals = True
    resX,resY = win.size

    if SCANNER: 
        MR_settings = {'TR': Tr,     # duration (sec) per whole-brain volume
                    'volumes': Volumes,    # number of whole-brain 3D volumes per scanning run
                    'sync': Sync, # character to use as the sync timing event; assumed to come at start of a volume
                    'skip': Skip       # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
                    }
        vol = launchScan(win, MR_settings, globalClock=globalClock)
        logging.data('Volumes: ' + str(vol) + '\n')

    # Main stimulation    
    try:
        main_block_design(win,globalClock)
    except Exception as e:
        logging.log(e,level=logging.ERROR)
        
    logging.data('Overall, %i frames were dropped.' % win.nDroppedFrames)
    np.save(path_out+Frames_durations_name,win.frameIntervals[1:])
    
    win.close()
    core.quit()


