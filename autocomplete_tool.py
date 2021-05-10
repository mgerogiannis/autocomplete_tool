import sys
import os
import tkinter
from keras.preprocessing.sequence import pad_sequences
from keras.layers import Embedding, LSTM, Dense, Dropout, GRU
from keras.preprocessing.text import Tokenizer
from keras.callbacks import EarlyStopping
from keras.models import Sequential
import keras.utils as ku
import numpy as np
import nltk
import matplotlib.pyplot as plt
import tensorflow as tf
from nltk.probability import FreqDist
import re
from tkinter import *


data = open(r'C:\ThePlaceWhereYouInsertedYourTextFile\text.txt').read()


#tokenization with nltk
tokens = nltk.word_tokenize(data)
print(tokens)

#print most common tokens
fdist = FreqDist(tokens)
print(fdist.most_common(30))

#show most common tokens
fdist.plot(30, cumulative = False)
plt.show()




tokenizer = Tokenizer(filters='!"#$%&,-?@\\^_`|~\t\n')



def dataset_preparation(data):
    # basic cleanup
    corpus = data.lower().split("\n")

    # tokenization
    tokenizer.fit_on_texts(corpus)
    total_words = len(tokenizer.word_index) + 1

    # create input sequences using list of tokens
    input_sequences = []
    for line in corpus:
        token_list = tokenizer.texts_to_sequences([line])[0]
        for i in range(1, len(token_list)):
            n_gram_sequence = token_list[:i + 1]
            input_sequences.append(n_gram_sequence)

    # pad sequences
    max_sequence_len = max([len(x) for x in input_sequences])
    input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))

    # create predictors and label
    predictors, label = input_sequences[:, :-1], input_sequences[:, -1]
    label = ku.to_categorical(label, num_classes=total_words)

    return predictors, label, max_sequence_len, total_words


def create_model(predictors, label, max_sequence_len, total_words):
      
  

    #GRU
    model = Sequential()

    model.add(Embedding(input_dim=total_words,output_dim= total_words, input_length=max_sequence_len - 1))
    
   
     
    model.add(GRU(units=150, return_sequences=True ))

    model.add(GRU(units=50))


    model.add(Dense(units=total_words, activation="softmax"))
    model.compile(loss="categorical_crossentropy", optimizer="adam", metrics=['acc'])
    #earlystop = EarlyStopping(monitor='val_loss', min_delta=0, patience=5, verbose=1, mode='auto')
    model.fit(predictors, label, batch_size=128, epochs=3, verbose=1)
    print
    model.summary()
    return model

#Autocomplete Plugin
try:
    from Tkinter import StringVar, Entry, Frame, Listbox, Scrollbar
    from Tkconstants import *
except ImportError:
    from tkinter import StringVar, Entry, Frame, Listbox, Scrollbar
    from tkinter.constants import *


def autoscroll(sbar, first, last):
    """Hide and show scrollbar as needed."""
    first, last = float(first), float(last)
    if first <= 0 and last >= 1:
        sbar.grid_remove()
    else:
        sbar.grid()
    sbar.set(first, last)


class Combobox_Autocomplete(Entry, object):
    def __init__(self, master, list_of_items=None, autocomplete_function=None, listbox_width=None, listbox_height=7, ignorecase_match=False, startswith_match=True, vscrollbar=True, hscrollbar=True, **kwargs):
        if hasattr(self, "autocomplete_function"):
            if autocomplete_function is not None:
                raise ValueError("Combobox_Autocomplete subclass has 'autocomplete_function' implemented")
        else:
            if autocomplete_function is not None:
                self.autocomplete_function = autocomplete_function
            else:
                if list_of_items is None:
                    raise ValueError("If not guiven complete function, list_of_items can't be 'None'")

                if ignorecase_match:
                    if startswith_match:
                        def matches_function(entry_data, item):
                            return item.startswith(entry_data)
                    else:
                        def matches_function(entry_data, item):
                            return item in entry_data

                    self.autocomplete_function = lambda entry_data: [item for item in self.list_of_items if matches_function(entry_data, item)]
                else:
                    if startswith_match:
                        def matches_function(escaped_entry_data, item):
                            if re.match(escaped_entry_data, item, re.IGNORECASE):
                                return True
                            else:
                                return False
                    else:
                        def matches_function(escaped_entry_data, item):
                            if re.search(escaped_entry_data, item, re.IGNORECASE):
                                return True
                            else:
                                return False
                    
                    def autocomplete_function(entry_data):
                        escaped_entry_data = re.escape(entry_data)
                        return [item for item in self.list_of_items if matches_function(escaped_entry_data, item)]

                    self.autocomplete_function = autocomplete_function

        self._listbox_height = int(listbox_height)
        self._listbox_width = listbox_width

        self.list_of_items = list_of_items
        
        self._use_vscrollbar = vscrollbar
        self._use_hscrollbar = hscrollbar

        kwargs.setdefault("background", "white")

        if "textvariable" in kwargs:
            self._entry_var = kwargs["textvariable"]
        else:
            self._entry_var = kwargs["textvariable"] = StringVar()

        Entry.__init__(self, master, **kwargs)

        self._trace_id = self._entry_var.trace('w', self._on_change_entry_var)
        
        self._listbox = None

        self.bind("<Tab>", self._on_tab)
        self.bind("<Up>", self._previous)
        self.bind("<Down>", self._next)
        self.bind('<Control-n>', self._next)
        self.bind('<Control-p>', self._previous)

        self.bind("<Return>", self._update_entry_from_listbox)
        self.bind("<Escape>", lambda event: self.unpost_listbox())
        
    def _on_tab(self, event):
        self.post_listbox()
        return "break"

    def _on_change_entry_var(self, name, index, mode):
        
        entry_data = self._entry_var.get()

        if entry_data == '':
            self.unpost_listbox()
            self.focus()
        else:
            values = self.autocomplete_function(entry_data)
            if values:
                if self._listbox is None:
                    self._build_listbox(values)
                else:
                    self._listbox.delete(0, END)

                    height = min(self._listbox_height, len(values))
                    self._listbox.configure(height=height)

                    for item in values:
                        self._listbox.insert(END, item)
                
            else:
                self.unpost_listbox()
                self.focus()

    def _build_listbox(self, values):
        listbox_frame = Frame()

        self._listbox = Listbox(listbox_frame, background="white", selectmode=SINGLE, activestyle="none", exportselection=False)
        self._listbox.grid(row=0, column=0,sticky = N+E+W+S)

        self._listbox.bind("<ButtonRelease-1>", self._update_entry_from_listbox)
        self._listbox.bind("<Return>", self._update_entry_from_listbox)
        self._listbox.bind("<Escape>", lambda event: self.unpost_listbox())
        
        self._listbox.bind('<Control-n>', self._next)
        self._listbox.bind('<Control-p>', self._previous)

        if self._use_vscrollbar:
            vbar = Scrollbar(listbox_frame, orient=VERTICAL, command= self._listbox.yview)
            vbar.grid(row=0, column=1, sticky=N+S)
            
            self._listbox.configure(yscrollcommand= lambda f, l: autoscroll(vbar, f, l))
            
        if self._use_hscrollbar:
            hbar = Scrollbar(listbox_frame, orient=HORIZONTAL, command= self._listbox.xview)
            hbar.grid(row=1, column=0, sticky=E+W)
            
            self._listbox.configure(xscrollcommand= lambda f, l: autoscroll(hbar, f, l))

        listbox_frame.grid_columnconfigure(0, weight= 1)
        listbox_frame.grid_rowconfigure(0, weight= 1)

        x = -self.cget("borderwidth") - self.cget("highlightthickness") 
        y = self.winfo_height()-self.cget("borderwidth") - self.cget("highlightthickness")

        if self._listbox_width:
            width = self._listbox_width
        else:
            width=self.winfo_width()

        listbox_frame.place(in_=self, x=x, y=y, width=width)
        
        height = min(self._listbox_height, len(values))
        self._listbox.configure(height=height)

        for item in values:
            self._listbox.insert(END, item)

    def post_listbox(self):
        if self._listbox is not None: return

        entry_data = self._entry_var.get()
        if entry_data == '': return

        values = self.autocomplete_function(entry_data)
        if values:
            self._build_listbox(values)

    def unpost_listbox(self):
        if self._listbox is not None:
            self._listbox.master.destroy()
            self._listbox = None

    def get_value(self):
        return self._entry_var.get()

    def set_value(self, text, close_dialog=False):
        self._set_var(text)

        if close_dialog:
            self.unpost_listbox()

        self.icursor(END)
        self.xview_moveto(1.0)
        
    def _set_var(self, text):
        self._entry_var.trace_vdelete("w", self._trace_id)
        self._entry_var.set(text)
        self._trace_id = self._entry_var.trace('w', self._on_change_entry_var)

    def _update_entry_from_listbox(self, event):
        if self._listbox is not None:
            current_selection = self._listbox.curselection()
            
            if current_selection:
                text = self._listbox.get(current_selection)
                self._set_var(text)

            self._listbox.master.destroy()
            self._listbox = None

            self.focus()
            self.icursor(END)
            self.xview_moveto(1.0)
            
        return "break"

    def _previous(self, event):
        if self._listbox is not None:
            current_selection = self._listbox.curselection()

            if len(current_selection)==0:
                self._listbox.selection_set(0)
                self._listbox.activate(0)
            else:
                index = int(current_selection[0])
                self._listbox.selection_clear(index)

                if index == 0:
                    index = END
                else:
                    index -= 1

                self._listbox.see(index)
                self._listbox.selection_set(first=index)
                self._listbox.activate(index)

        return "break"

    def _next(self, event):
        if self._listbox is not None:

            current_selection = self._listbox.curselection()
            if len(current_selection)==0:
                self._listbox.selection_set(0)
                self._listbox.activate(0)
            else:
                index = int(current_selection[0])
                self._listbox.selection_clear(index)
                
                if index == self._listbox.size() - 1:
                    index = 0
                else:
                    index +=1
                    
                self._listbox.see(index)
                self._listbox.selection_set(index)
                self._listbox.activate(index)
        return "break"


#Prediction method  
def generate_text(input_txt):



    for _ in range(7):
        token_list = tokenizer.texts_to_sequences([input_txt])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_len - 1, padding='pre')
        predicted = model.predict_classes(token_list, verbose=0)

        output_word = ""

        for word, index in tokenizer.word_index.items():
            if index == predicted:
                output_word = word
                break

        input_txt += " " +output_word

    return input_txt




predictors, label, max_sequence_len, total_words = dataset_preparation(data)
model = create_model(predictors, label, max_sequence_len, total_words)

import io
import base64

if __name__ == '__main__':
    try:
        from Tkinter import Tk
    except ImportError:
        from tkinter import Tk
        
        try:
            from Tkinter import Tk, Label, Entry, Toplevel, Canvas
        except ImportError:
            from tkinter import Tk, Label, Entry, Toplevel, Canvas

from PIL import Image, ImageDraw, ImageTk, ImageFont


BASE64_BACKGROUND = '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'

##################
## First Example
#
root = Tk()

image_file = io.BytesIO(base64.b64decode(BASE64_BACKGROUND))
image = Image.open(image_file)

width, height = image.size

# I disallow window to resizing and I make the size of the window the same than the size of the background image
root.resizable(width=False, height=False)
root.geometry("%sx%s"%(width, height))

draw = ImageDraw.Draw(image)



# Use here a nice ttf font
#   font = ImageFont.truetype("YOUR_FONT.ttf", 12)
#   width_text, height_text = font.getsize(text)
#   draw.text((text_x, text_y), text, fill="white", font=font)




photoimage = ImageTk.PhotoImage(image)
Label(root, image=photoimage).place(x=0,y=0)

entry_pady = 7




list_of_items = [generate_text('for') , generate_text('if'), generate_text('public'), generate_text('while') , generate_text('import'), generate_text('try'), generate_text('catch'),  generate_text('.'),  generate_text('hashmap') ]

    #root = Tk()
    #root.geometry("300x200")

combobox_autocomplete = Combobox_Autocomplete(root, list_of_items, highlightthickness=1)
combobox_autocomplete.pack()
    
combobox_autocomplete.focus()
    
root.mainloop()
    
