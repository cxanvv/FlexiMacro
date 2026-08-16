import tkinter as t
import tkinter.font as tkFont
from tkinter import ttk, filedialog, messagebox as msgbox
import time
import json
import keyboard

import controller
import templates
import copy


Selected_Save = None
Saved = True
TaskStructure = []
Properties = []
PropsLB = None

w = t.Tk()
w.title(templates.APP_NAME)
w.iconbitmap('Icon.ico')
w.geometry('900x750')
w.resizable(False,False)

def Validate_Entry(P,numb_only=False,max_chars=-1):
    if P == "":
        return True

    if numb_only and not P.isdigit():
        return False

    if max_chars != -1 and len(P) > max_chars:
        return False

    return True
Validate_Reg = w.register(Validate_Entry)

def SetDefaultOnEntryFocusOut(event,entry,value='...'):
    cur_value = entry.get()
    if not cur_value.strip():
        entry.delete(0, t.END)
        entry.insert(0, value)

def NewFile():
    global taskframe
    global Selected_Save
    global Saved
    global TaskStructure
    if Saved:
        TaskStructure.clear()
        taskframe.delete(0,t.END)
        Selected_Save = None
        w.title(templates.APP_NAME)
    else:
        savemsg = msgbox.askyesnocancel(message='Do you want to save this task?')
        if savemsg is True:
            NewSave()
        elif savemsg is False:
            Saved = True
            NewFile()

def OpenFile():
    global taskframe
    global TaskStructure
    global Selected_Save
    NewFile()
    filepath = filedialog.askopenfilename(
        title="Open a JSON File",
        initialdir="/",
        filetypes=[("JSON files", "*.json"), ("All Files", "*.*")]
    )
    if filepath:
        try:
            with open(filepath, 'r') as file:
                TaskStructure = json.load(file)
                w.title(f'{templates.APP_NAME} ({file.name})')
                Selected_Save = file
                for i in TaskStructure:
                    action = list(i.keys())[0]
                    action_display = templates.TASK_TEMPLATE[action]
                    for prop_key in i[action]:
                        if prop_key == 'pos':
                            if i[action][prop_key] == [-1,-1]:
                                action_display = action_display.replace(f'<{prop_key}>','current cursor position')
                                continue
                        action_display = action_display.replace(f'<{prop_key}>',str(i[action][prop_key]))
                    taskframe.insert(t.END,action_display)
                    taskframe.itemconfig(t.END,foreground=templates.GetTaskFrameTxtColor(action))
                lines_label.config(text=f'Ln: {taskframe.size()}')
        except json.JSONDecodeError:
            msgbox.showerror("Error", 'JSON decode error')
        except Exception as e:
            msgbox.showerror("Error", e)

def Save():
    global Selected_Save
    global TaskStructure
    if Selected_Save:
        with open(Selected_Save.name, 'w') as f:
            json.dump(TaskStructure, f, indent=4)
    else:
        NewSave()

def NewSave():
    global TaskStructure
    global Selected_Save
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json"), ("All Files", "*.*")],
        initialfile='MyMacro'
    )
    if file_path:
        try:
            with open(file_path, 'w') as f:
                json.dump(TaskStructure, f, indent=4)
                Selected_Save = f
                w.title(f'{templates.APP_NAME} ({f.name})')
            msgbox.showinfo("Success", f"Data successfully saved to {file_path}")
        except Exception as e:
            msgbox.showerror("Error", e)

def AddAction(action):
    global taskframe
    global TaskStructure
    global lines_label
    global Saved
    Saved = False
    tasktxt = templates.TASK_TEMPLATE[action]
    taskframe.insert(t.END,templates.SetTemplateToDefault(tasktxt))
    TaskStructure.append({action : copy.deepcopy(templates.STRUCTURE_DEFAULT[action])})
    taskframe.itemconfig(t.END,foreground=templates.GetTaskFrameTxtColor(action))
    lines_label.config(text=f'Ln: {taskframe.size()}')

def ModifyAction():
    global PropsLB
    global taskframe
    global TaskStructure
    global Properties
    Properties.clear()
    selections = taskframe.curselection()
    if len(selections) == 0:
        msgbox.showerror('Error','Please select a line of action first.')
        return
    elif len(selections) > 1:
        msgbox.showerror('Error','Cannot select more than one line of task to modify.')
        return
    selected_index = selections[0]
    action = list(TaskStructure[selected_index].keys())[0]
    if len(TaskStructure[selected_index][action]) == 0:
        msgbox.showerror('Error','Selected action does not have any properties.')
        return
    w_props = t.Toplevel(master=w)
    w_props.iconbitmap('Icon.ico')
    w_props.title('Properties')
    w_props.resizable(False,False)
    w_props.geometry('300x300')
    PropsLB = t.Listbox(
        master=w_props,
        font=("Cascadia Code",9)
    )
    PropsLB.place(relx=0.5,rely=0.45,anchor='center',width=250,height=200)
    Properties = list(TaskStructure[selected_index][action].keys())
    for prop in Properties:
        PropsLB.insert(t.END,f'{prop} = {TaskStructure[selected_index][action][prop]}')

    b_edit = t.Button(
        master=w_props,
        text='Edit...',
        font=("Cascadia Code",8),
        command=lambda:EditProp(PropsLB,selected_index,action)
    )
    b_edit.place(relx=0.5,rely=0.9,anchor='center',width=100,height=35)

def SwapAction():
    global taskframe
    global TaskStructure
    selections = taskframe.curselection()
    if len(selections) != 2:
        msgbox.showerror('Error','Please select 2 actions.')
        return
    ind1 = selections[0]
    ind2 = selections[1]
    txt1 = taskframe.get(ind1)
    txt2 = taskframe.get(ind2)
    act1 = TaskStructure[ind1]
    act2 = TaskStructure[ind2]
    TaskStructure[ind1] = act2
    TaskStructure[ind2] = act1
    taskframe.delete(ind1)
    taskframe.insert(ind1,txt2)
    taskframe.delete(ind2)
    taskframe.insert(ind2,txt1)
    taskframe.itemconfig(ind1,foreground=templates.GetTaskFrameTxtColor(list(act2.keys())[0]))
    taskframe.itemconfig(ind2,foreground=templates.GetTaskFrameTxtColor(list(act1.keys())[0]))

def PropChange(action_selected_index,action,prop,cmdtype=None,change=None,inpobj=None):
    global PropsLB
    global TaskStructure
    global taskframe
    global Saved
    Saved = False
    ActionTask = TaskStructure[action_selected_index][action]
    match prop:
        case 't':
            if change.isdigit():
                ActionTask[prop] = int(change)
            else:
                inpobj.delete(0,t.END)
                inpobj.insert(0,'0')
        case 'pos':
            if cmdtype == 'x' or cmdtype == 'y':
                if change.isdigit():
                    ActionTask[prop][0 if cmdtype == 'x' else 1] = int(change)
                else:
                    inpobj.delete(0,t.END)
                    inpobj.insert(0,'0')
        case 'lr' | 'ud' | 'txt' | 'key':
            ActionTask[prop] = change
        case 'keys':
            if cmdtype == 'add':
                if change in ActionTask[prop]:
                    msgbox.showerror('Error','Cannot insert the same key.')
                    return
                ActionTask[prop].append(change)
                inpobj.insert(t.END,change)
            elif cmdtype == 'remove':
                keyselection = inpobj.curselection()
                if len(keyselection) == 0:
                    msgbox.showerror('Error','Selection not found.')
                    return
                selected_key_index = keyselection[0]
                selected_key = inpobj.get(selected_key_index)
                if inpobj.size() == 1:
                    msgbox.showerror('Error','Combination key must have at least 1 key.')
                    return
                ActionTask[prop].remove(selected_key)
                inpobj.delete(selected_key_index)
    propslb_index = Properties.index(prop)
    action_display = templates.TASK_TEMPLATE[action]
    for prop_key in ActionTask:
        if prop_key == 'pos':
            if ActionTask[prop_key] == [-1,-1]:
                action_display = action_display.replace(f'<{prop_key}>','current cursor position')
                continue
        elif prop_key == 'keys':
            keys_display = ''
            for i,key in enumerate(ActionTask[prop_key]):
                if i < len(ActionTask[prop_key])-1:
                    keys_display += key + ' + '
                    continue
                keys_display += key
            action_display = action_display.replace(f'<{prop_key}>',keys_display)
            continue
        action_display = action_display.replace(f'<{prop_key}>',str(ActionTask[prop_key]))
    taskframe.delete(action_selected_index)
    taskframe.insert(action_selected_index,action_display)
    PropsLB.delete(propslb_index)
    PropsLB.insert(propslb_index,f'{prop} = {ActionTask[prop]}')
    taskframe.itemconfig(action_selected_index,foreground=templates.GetTaskFrameTxtColor(action))

def EditProp(propslist,action_selected_index,action):
    global Validate_Reg
    global TaskStructure
    selections = propslist.curselection()
    if len(selections) == 0:
        msgbox.showerror('Error','Selection not found.')
        return
    prop_selected_index = selections[0]
    prop = Properties[prop_selected_index]
    w_propedit = t.Toplevel(master=w)
    w_propedit.iconbitmap('Icon.ico')
    w_propedit.title(f'Modify <{prop}>')
    w_propedit.resizable(False,False)
    w_propedit.geometry('300x300')
    # b_apply = t.Button(
    #     master=w_propedit,
    #     text='Apply',
    #     font=("Cascadia Code",9)
    # )
    # b_apply.place(relx=0.5,rely=0.9,anchor='center',width=125,height=35)
    match prop:
        case 't':
            Validate_Reg = w.register(lambda P: Validate_Entry(P,numb_only=True,max_chars=1000))
            title = t.Label(
                master=w_propedit,
                font=("Cascadia Code",12),
                text='Input a number:'
            )
            title.place(relx=0.5,rely=0.4,anchor='center')
            inputvar = t.StringVar()
            inputentry = t.Entry(
                master=w_propedit,
                font=("Cascadia Code",9),
                validate='key',
                validatecommand=(Validate_Reg,'%P'),
                textvariable=inputvar
            )
            inputentry.place(relx=0.5,rely=0.5,anchor='center',width=250,height=30)
            inputentry.delete(0,t.END)
            inputentry.insert(0,TaskStructure[action_selected_index][action][prop])
            inputvar.trace('w',lambda *args: PropChange(action_selected_index=action_selected_index,action=action,prop=prop,change=inputvar.get(),inpobj=inputentry))
        case 'txt':
            title = t.Label(
                master=w_propedit,
                font=("Cascadia Code",12),
                text='Input a text:'
            )
            title.place(relx=0.5,rely=0.4,anchor='center')
            inputvar = t.StringVar()
            inputentry = t.Entry(
                master=w_propedit,
                font=("Cascadia Code",8),
                textvariable=inputvar,
            )
            inputentry.place(relx=0.5,rely=0.5,anchor='center',width=250,height=30)
            inputentry.delete(0,t.END)
            inputentry.insert(0,TaskStructure[action_selected_index][action][prop])
            inputvar.trace('w',lambda *args: PropChange(action_selected_index=action_selected_index,action=action,prop=prop,change=inputvar.get()))
        case 'pos':
            Validate_Reg = w.register(lambda P: Validate_Entry(P,numb_only=True,max_chars=5))
            x_title = t.Label(
                master=w_propedit,
                font=("Cascadia Code",12),
                text='x:'
            )
            x_title.place(relx=0.5,rely=0.25,anchor='center')
            x_posvar = t.StringVar()
            x_entry = t.Entry(
                master=w_propedit,
                font=("Cascadia Code",9),
                validate='key',
                validatecommand=(Validate_Reg,'%P'),
                textvariable=x_posvar
            )
            x_entry.place(relx=0.5,rely=0.35,anchor='center',width=250,height=30)
            x_entry.delete(0,t.END)
            x_entry.insert(0,TaskStructure[action_selected_index][action][prop][0])
            x_posvar.trace('w',lambda *args: PropChange(action_selected_index,action,prop,'x',x_posvar.get(),x_entry))

            y_title = t.Label(
                master=w_propedit,
                font=("Cascadia Code",12),
                text='y:'
            )
            y_title.place(relx=0.5,rely=0.45,anchor='center')
            y_posvar = t.StringVar()
            y_entry = t.Entry(
                master=w_propedit,
                font=("Cascadia Code",9),
                validate='key',
                validatecommand=(Validate_Reg,'%P'),
                textvariable=y_posvar
            )
            y_entry.place(relx=0.5,rely=0.55,anchor='center',width=250,height=30)
            y_entry.delete(0,t.END)
            y_entry.insert(0,TaskStructure[action_selected_index][action][prop][1])
            y_posvar.trace('w',lambda *args: PropChange(action_selected_index,action,prop,'y',y_posvar.get(),y_entry))
            if action == 'click':
                def ignoreXY():
                    if cbvar.get() == 1:
                        x_entry.config(state='disabled')
                        y_entry.config(state='disabled')
                        TaskStructure[action_selected_index][action][prop] = [-1,-1]
                    else:
                        x_entry.config(state='normal')
                        y_entry.config(state='normal')
                        TaskStructure[action_selected_index][action][prop] = [int(x_entry.get()),int(y_entry.get())]
                    PropChange(action_selected_index=action_selected_index,action=action,prop='pos',cmdtype='click')
                cbvar = t.IntVar()
                cb_curpos = t.Checkbutton(
                    master=w_propedit,
                    font=("Cascadia Code",9),
                    text='Ignore (x,y) pos, use current cursor position',
                    variable=cbvar,
                    command=ignoreXY,
                    wraplength=250
                )
                cb_curpos.place(relx=0.5,rely=0.75,anchor='center')
        case 'lr':
            title = t.Label(
                master=w_propedit,
                font=("Cascadia Code",12),
                text='Select:'
            )
            title.place(relx=0.5,rely=0.4,anchor='center')
            choice = ttk.Combobox(
                master=w_propedit,
                font=("Cascadia Code",9),
                state="readonly"
            )
            choice.place(relx=0.5,rely=0.5,anchor='center',width=100,height=35)
            choice['values'] = ['left','right']
            choice.set(TaskStructure[action_selected_index][action][prop])
            choice.bind('<<ComboboxSelected>>',lambda*args:PropChange(action_selected_index=action_selected_index,action=action,prop=prop,change=choice.get()))
        case 'ud':
            title = t.Label(
                master=w_propedit,
                font=("Cascadia Code",12),
                text='Select:'
            )
            title.place(relx=0.5,rely=0.4,anchor='center')
            choice = ttk.Combobox(
                master=w_propedit,
                font=("Cascadia Code",9),
                state="readonly"
            )
            choice.place(relx=0.5,rely=0.5,anchor='center',width=100,height=35)
            choice['values'] = ['up','down']
            choice.set(TaskStructure[action_selected_index][action][prop])
            choice.bind('<<ComboboxSelected>>',lambda*args:PropChange(action_selected_index=action_selected_index,action=action,prop=prop,change=choice.get()))
        case 'key':
            title = t.Label(
                master=w_propedit,
                font=("Cascadia Code",12),
                text='Select:'
            )
            title.place(relx=0.5,rely=0.4,anchor='center')
            choice = ttk.Combobox(
                master=w_propedit,
                font=("Cascadia Code",9),
                state="readonly"
            )
            choice.place(relx=0.5,rely=0.5,anchor='center',width=150,height=30)
            choice['values'] = controller.PAG_KEYS
            choice.set(TaskStructure[action_selected_index][action][prop])
            choice.bind('<<ComboboxSelected>>',lambda*args:PropChange(action_selected_index=action_selected_index,action=action,prop=prop,change=choice.get()))
        case 'keys':
            keyslist = t.Listbox(
                master=w_propedit,
                font=("Cascadia Code",8),
                selectmode='single'
            )
            keyslist.place(relx=0.5,rely=0.375,anchor='center',width=250,height=200)
            for i in TaskStructure[action_selected_index][action][prop]:
                keyslist.insert(t.END,i)
            choice = ttk.Combobox(
                master=w_propedit,
                font=("Cascadia Code",9),
                state="readonly"
            )
            choice.place(relx=0.35,rely=0.775,anchor='center',width=150,height=30)
            choice['values'] = controller.PAG_KEYS
            choice.set('a')
            b_add = t.Button(
                master=w_propedit,
                font=("Cascadia Code",9),
                text='Add',
                command=lambda: PropChange(action_selected_index=action_selected_index,action=action,prop=prop,cmdtype='add',change=choice.get(),inpobj=keyslist)
            )
            b_add.place(relx=0.75,rely=0.775,anchor='center',width=80,height=35)
            b_remove = t.Button(
                master=w_propedit,
                font=("Cascadia Code",9),
                text='Remove selected',
                command=lambda: PropChange(action_selected_index=action_selected_index,action=action,prop=prop,cmdtype='remove',change=choice.get(),inpobj=keyslist)
            )
            b_remove.place(relx=0.5,rely=0.9,anchor='center',width=180,height=35)
        


def DeleteAction():
    global taskframe
    global TaskStructure
    global lines_label
    selections = taskframe.curselection()
    if len(selections) == 0:
        msgbox.showerror('Error','Please select a line of action first.')
        return
    
    delstatus = msgbox.askyesno('Delete',f'Delete selected line(s)?')
    if delstatus:
        for index in selections[::-1]:
            TaskStructure.pop(index)
            taskframe.delete(index)
        lines_label.config(text=f'Ln: {taskframe.size()}')

def RunTask():
    global TaskStructure
    global taskframe
    global loopvar
    if taskframe.size() == 0:
        msgbox.showerror('Error','Please add a line of action first.')
        return
    yesno = msgbox.askyesno('Run Task','Run Task? (Note: Press F6 to terminate the task)')
    if yesno:
        w.iconify()
        time.sleep(0.5)
        controller.run_task(TaskStructure,loopvar.get())

menu = t.Menu()
w.config(menu=menu)

filemenu = t.Menu(menu)
menu.add_cascade(label='File',menu=filemenu)
filemenu.add_command(label='New',command=NewFile)
filemenu.add_command(label='Open',command=OpenFile)
filemenu.add_command(label='Save',command=Save)
actionmenu = t.Menu(menu)
menu.add_cascade(label='Actions',menu=actionmenu)
actionmenu.add_command(label='Repeat',command=lambda: AddAction('repeat'))
actionmenu.add_command(label='End repeat',command=lambda: AddAction('endrepeat'))
actionmenu.add_command(label='Wait',command=lambda: AddAction('wait'))
actionmenu.add_command(label='Click',command=lambda: AddAction('click'))
actionmenu.add_command(label='Hold mouse button',command=lambda: AddAction('holdmousebutton'))
actionmenu.add_command(label='Move cursor',command=lambda: AddAction('movecursor'))
actionmenu.add_command(label='Key',command=lambda: AddAction('key'))
actionmenu.add_command(label='Hold key',command=lambda: AddAction('holdkey'))
actionmenu.add_command(label='Comb key',command=lambda: AddAction('combkey'))
actionmenu.add_command(label='Write',command=lambda: AddAction('write'))

task_font = tkFont.Font(family="Google Sans Code",size=10)
taskframe = t.Listbox(
    master=w,
    selectmode='multiple',
    font=task_font
)
taskframe.place(relx=0.5, rely=0.45,anchor='center',width=850,height=550)

yscrollbar = ttk.Scrollbar(taskframe, orient=t.VERTICAL, command=taskframe.yview)
yscrollbar.place(x=830,height=550)

lines_label = t.Label(
    master=w,
    font=("Cascadia Code",8),
    text='Ln: 0',
    justify='right'
)
lines_label.place(relx=0.9,rely=0.04,anchor='center')

b_modify = t.Button(
    master=w,
    text='Modify...',
    font=("Cascadia Code",9),
    command=ModifyAction
)
b_modify.place(relx=0.11, rely=0.875,anchor='center',width=150,height=35)
b_swap = t.Button(
    master=w,
    text='Swap',
    font=("Cascadia Code",9),
    command=SwapAction
)
b_swap.place(relx=0.28, rely=0.875,anchor='center',width=150,height=35)

b_delete = t.Button(
    master=w,
    text='Delete',
    font=("Cascadia Code",9),
    command=DeleteAction
)
b_delete.place(relx=0.11, rely=0.925,anchor='center',width=150,height=35)
b_run = t.Button(
    master=w,
    text='Run',
    font=("Cascadia Code",9),
    command=RunTask
)
b_run.place(relx=0.875, rely=0.875,anchor='center',width=150,height=35)
loopvar = t.BooleanVar()
cb_loop = t.Checkbutton(
    master=w,
    text='Loop task',
    font=("Cascadia Code",9),
    variable=loopvar
)
cb_loop.place(relx=0.875, rely=0.925,anchor='center',width=150,height=35)

keyboard.add_hotkey('f6',lambda:controller.Shortcut('Deactivate'))

w.mainloop()
