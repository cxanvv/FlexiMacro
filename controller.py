import pyautogui as pag
import time

screenWidth, screenHeight = pag.size()

pagkeys = pag.KEYBOARD_KEYS
pagkeys.remove('\t')
pagkeys.remove('\n')
pagkeys.remove('\r')
PAG_KEYS = pagkeys

Active = True
def Shortcut(action):
    global Active
    if action == 'Deactivate':
        Active = False

def run_task(flow,loop=False):
    global Active
    Active = True
    # make sure to receive "flow" as opened json file / "TaskStructure"
    i = 0
    Repeats = [] # index of 0 = repeat start index, 1 = repeat times
    while i < len(flow) and Active:
        task_dict = flow[i] # the dictionary
        action = list(task_dict.keys())[0] # key
        action_att = task_dict[action] # value
        if action == 'repeat':
            Repeats.append([i+1,action_att['t']])
        elif action == 'endrepeat' and len(Repeats) > 0:
            if Repeats[-1][1] > 0:
                Repeats[-1][1] -= 1
                if Repeats[-1][1] == 0: 
                    Repeats.pop(-1)
                    i += 1
                    continue
                i = Repeats[-1][0]
                continue
        elif action == 'wait':
            time.sleep(action_att['t']/1000)
        elif action == 'click':
            if action_att['pos'] == [-1,-1]:
                pag.click(button=action_att['lr'])
            else:
                pag.click(button=action_att['lr'],x=action_att['pos'][0],y=action_att['pos'][1])
        elif action == 'holdmousebutton':
            if action_att['ud'] == 'up':
                pag.mouseUp(button=action_att['lr'])
            else:
                pag.mouseDown(button=action_att['lr'])
        elif action == 'movecursor':
            pag.moveTo(x=action_att['pos'][0],y=action_att['pos'][1],duration=action_att['t']/1000)
        
        elif action == 'key':
            pag.press(action_att['key'])
        elif action == 'holdkey':
            if action_att['ud'] == 'up':
                pag.keyUp(action_att['key'])
            else:
                pag.keyDown(action_att['key'])
        elif action == 'combkey':
            pag.hotkey(action_att['keys'])
        elif action == 'write':
            pag.write(action_att['txt'])

        elif action == 'debug':
            print(action_att['txt'])
        i += 1
        if loop is True and i == len(flow) and Active:
            i = 0
