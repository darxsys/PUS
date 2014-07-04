#!/usr/bin/env python

# example helloworld.py

import sys
import threading

import pygtk
pygtk.require('2.0')
import gtk

from sp import ServiceProvider

class StopableThread(threading.Thread):
    def __init__(self, target):
        super(StopableThread, self).__init__(target=target)
        self.stop = False

    def run(self):
        self._Thread__target()
        # while True:
        #     if self.stop:
        #         break
        #     self._Thread__target()

class GUI:
    def __init__(self, service_provider):
        self.sp = service_provider
        # tcp thread
        self.thread = StopableThread(target=self.sp.listen)
        self.thread.daemon = True
        self.thread.start()

        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.sp.name)
        # self.window.set_default_size(200, 200)
        self.user_entry = gtk.Entry()
        self.pass_entry = gtk.Entry()
        self.pass_entry.set_visibility(False)
        self.ok_button = gtk.Button('LOGIN')
        self.ok_button.connect('clicked', self.login_clicked, None)
    
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
    
        self.window.set_border_width(10)
    
        vbox = gtk.VBox()
        vbox.pack_start(self.user_entry, False)
        vbox.pack_start(self.pass_entry, False)
        vbox.pack_start(self.ok_button, False)

        self.user_entry.show()
        self.pass_entry.show()
        self.ok_button.show()
        vbox.show()

        self.window.add(vbox)
        self.window.show()

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        self.thread.stop = True
        # self.thread.join()
        gtk.main_quit()

    def show_main(self):
        self.window.remove(self.window.get_children()[0])
        sp_button = gtk.Button('Get SP list')
        file_button = gtk.Button('Get a file')
        sp_button.connect('clicked', self.get_sp_list, None)        
        file_button.connect('clicked', self.get_file, None)

        vbox = gtk.VBox()
        vbox.pack_start(sp_button, False)       
        vbox.pack_start(file_button, False)
        sp_button.show()
        file_button.show()
        vbox.show()

        self.window.add(vbox)
        self.window.show()       

    def login_clicked(self, widget, data=None):
        print 'Login'
        # print(data)
        # print(widget)
        # print(self.user_entry.get_text())
        username = self.user_entry.get_text()
        password = self.pass_entry.get_text()
        if username in self.sp.users and self.sp.users[username] == password:
            self.show_main()
            self.sp.username = username

    def go_back(self, wiget, data=None):
        self.show_main()

    def get_sp_list(self, widget, data=None):
        self.window.remove(self.window.get_children()[0])
        sp_list = self.sp.middle.get_sp_list()

        out = ""
        for key in sorted(sp_list.iterkeys()):
            out += str(key)
            out += " " + sp_list[key][0]
            out += " " + sp_list[key][1]
            out += " " + str(sp_list[key][2])
            out += "\n"

        buff = gtk.TextBuffer()
        buff.set_text(out)
        text = gtk.TextView()
        text.set_buffer(buff)
        text.set_editable(False)
        text.show()

        vscrollbar = gtk.VScrollbar(text.get_vadjustment())
        vscrollbar.show()
        hbox = gtk.HBox()
        hbox.pack_start(text)
        hbox.pack_start(vscrollbar)
        hbox.show()

        # back button
        back = gtk.Button('Go back')
        back.connect('clicked', self.go_back, None)
        back.show()

        vbox = gtk.VBox()
        vbox.pack_start(hbox, False)
        vbox.pack_start(back, False)
        vbox.show()
        self.window.add(vbox)
        self.window.show()
        # self.window.resize(150, 150)

    def get_file(self, widget, data=None):
        self.window.remove(self.window.get_children()[0])
        files = self.sp.middle.get_file_list()

        out = "File_ID File_Name Author Info Location_ID\n"
        for key in sorted(sorted(files.iterkeys())):
            out += str(key)
            out += " " + files[key][0]
            out += " " + files[key][1][1]
            out += " " + files[key][1][2]
            out += " " + files[key][2]
            out += "\n"

        buff = gtk.TextBuffer()
        buff.set_text(out)
        text = gtk.TextView()
        text.set_buffer(buff)
        text.set_editable(False)
        text.show()

        vscrollbar = gtk.VScrollbar(text.get_vadjustment())
        vscrollbar.show()
        hbox = gtk.HBox()
        hbox.pack_start(text)
        hbox.pack_start(vscrollbar)
        hbox.show()

        # entry
        self.file_entry = gtk.Entry()
        self.file_entry.show()

        # back button
        back = gtk.Button('Go back')
        back.connect('clicked', self.go_back, None)
        back.show()

        # ok button
        ok_button = gtk.Button("Open")
        ok_button.connect('clicked', self.display_file, None)
        ok_button.show()

        hbox_but = gtk.HBox()
        hbox_but.pack_start(ok_button)
        hbox_but.pack_start(back)
        hbox_but.show()

        vbox = gtk.VBox()
        vbox.pack_start(hbox, False)
        vbox.pack_start(self.file_entry, False)
        vbox.pack_start(hbox_but, False)
        vbox.show()
        self.window.add(vbox)
        self.window.show()       

    def display_file(self, widget, data=None):
        file_id = self.file_entry.get_text()
        self.window.remove(self.window.get_children()[0])
        print("File id: " + file_id)

        f = self.sp.middle.fetch_file(file_id, self.sp.id, self.sp.username, 
                self.sp.certificates, self.sp.certificate, self.sp.key)

        if f == None:
            f = "File does not exist."

        buff = gtk.TextBuffer()
        buff.set_text(f)
        text = gtk.TextView()
        text.set_buffer(buff)
        text.set_editable(False)
        text.show()

        vscrollbar = gtk.VScrollbar(text.get_vadjustment())
        vscrollbar.show()
        hbox = gtk.HBox()
        hbox.pack_start(text)
        hbox.pack_start(vscrollbar)
        hbox.show()

        back = gtk.Button('Go back')
        back.connect('clicked', self.go_back, None)
        back.show()

        vbox = gtk.VBox()
        vbox.pack_start(hbox, False)
        # vbox.pack_start(self.file_entry)
        vbox.pack_start(back, False)
        vbox.show()
        self.window.add(vbox)
        self.window.show() 

    def main(self):
        gtk.threads_init()
        gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
    if len(sys.argv) < 8:
      print("./script <name> <host_ip> <host_port> <own_ip> <own_port> <file_list> <users_dir>")
      raise ValueError("Not enough arguments.")

    name = sys.argv[1]
    host_ip = sys.argv[2]
    host_port = int(sys.argv[3])
    own_ip = sys.argv[4]
    own_port = int(sys.argv[5])
    file_list = sys.argv[6]
    users = sys.argv[7]

    buffer_size = 4096
    sp = ServiceProvider(name, host_ip, host_port, own_ip, own_port, 
        buffer_size, file_list, users)

    hello = GUI(sp)
    hello.main()