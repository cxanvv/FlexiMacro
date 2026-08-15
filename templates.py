# lr = left/right
# ud = up/down
# t = time in seconds
APP_NAME = 'FlexiMacro'
TASK_TEMPLATE = {
    # misc
    'wait' : 'Wait for <t> ms',
    'repeat' : 'Repeat for <t> time(s)',
    'endrepeat' : 'End Repeat',

    # cursor/mouse
    'click' : 'Click <lr> mouse at <pos>', # pos = (-1,-1) means at current position
    'holdmousebutton' : 'Hold <lr> mouse button <ud>',
    'movecursor' : 'Move cursor to <pos> for <t> ms',

    # keyboard
    'key' : 'Press "<key>" key',
    'holdkey' : 'Hold "<key>" key <ud>',
    'combkey' : 'Press combination key "<keys>"',
    'write' : 'Write "<txt>"',
}

STRUCTURE_DEFAULT = {
    'wait' : {
        't' : 1
    },
    'repeat' : {
        't' : 1
    },
    'endrepeat' : {},

    'click' : {
        'lr' : 'left',
        'pos' : [0,0]
    },
    'holdmousebutton' : {
        'lr' : 'left',
        'ud' : 'down'
    },
    'movecursor' : {
        'pos' : [0,0],
        't' : 1
    },

    'key' : {
        'key' : 'a'
    },
    'holdkey' : {
        'key' : 'a',
        'ud' : 'down'
    },
    'combkey' : {
        'keys' : ['ctrl','c']
    },
    'write' : {
        'txt' : 'Hello world!'
    }
}

def SetTemplateToDefault(txt):
    txt = txt.replace('<t>','1')
    txt = txt.replace('<lr>','left')
    txt = txt.replace('<pos>','[0,0]')
    txt = txt.replace('<ud>','down')
    txt = txt.replace('<key>','a')
    txt = txt.replace('<keys>','ctrl + c')
    txt = txt.replace('<txt>','Hello world!')
    return txt

def GetTaskFrameTxtColor(action):
    if action == 'repeat' or action == 'endrepeat':
        return 'red'
    if action == 'wait':
        return 'orange'
    return 'black'