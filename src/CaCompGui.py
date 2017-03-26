# California compensation by city. Files are updated every working weekday
#
# Copyright (c) <2017> <Larz60+>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Credits:
#     Thanks to Snippsat for showing me how to scrape ASP.NET page.
#
# Author Larz60+
#
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tfd
import tkinter.messagebox as tmb
import json
import getpass
import requests
from urllib.parse import urlparse
import UpdateCatalog
import socket
import os


class CaCompGui:
    def __init__(self, parent=None, title='Tk'):
        if parent:
            self.parent = parent
        else:
            self.parent = tk.Tk()
        if socket.gethostbyname(socket.gethostname()) != '127.0.0.1':
            self.s = ttk.Style()
            self.s.theme_use('classic')

            userid = getpass.getuser()
            # print('userid: {}'.format(userid))
            self.title = '{} -- {}'.format(title, userid)

            catalog_url = 'http://publicpay.ca.gov/Reports/RawExport.aspx'
            newcat = UpdateCatalog.UpdateCatalog()
            newcat.build_json_data(catalog_url)

            with open('data/CaCityCompensation.json') as f:
                self.data = json.load(f)

            self.parent.title(self.title)
            self.parent_width = 1190
            self.parent_height = 670
            self.parent.geometry('{}x{}+10+10'.format(self.parent_width,
                                                      self.parent_height))

            # GUI prototypes
            self.fmain1 = tk.Frame
            self.fmain2 = tk.Frame
            self.frame2 = tk.Frame
            self.frame3a = tk.Frame
            self.frame3b = tk.Frame
            self.frow=0
            self.tree = ttk.Treeview
            self.textwin = tk.Text
            self.txscroll = tk.Scrollbar

            # tkinter variables
            self.dest_dir = tk.StringVar()
            self.dest_dir.set('Not defined')
            self.url = tk.StringVar()
            self.status = tk.StringVar()
            self.treeheight_cat = 19
            self.treeheight_download = 6
            self.download_list = []
            self.iid_list = []

            self.build_gui()

            self.status.set('Updating Catalog (changes daily)')
            catalog_url = 'http://publicpay.ca.gov/Reports/RawExport.aspx'
            newcat = UpdateCatalog.UpdateCatalog()
            newcat.build_json_data(catalog_url)
            self.status.set('Catalog is up to date')

            with open('data/CaCityCompensation.json') as f:
                self.data = json.load(f)

            self.parent.mainloop()
        else:
            tmb.showerror('Internet', 'Please enable internet and restart')

    def build_gui(self):
        self.create_main_frames()
        self.create_frame2()
        self.create_frame3()
        self.create_tree()
        self.create_textwin()
        self.create_statusbar()

    def create_main_frames(self):
        self.fmain1 = tk.Frame(self.parent, bd=2, relief=tk.RAISED)
        self.fmain1.grid(row=self.frow, rowspan=self.treeheight_cat+1,
                         column=0, sticky='nwew')
        self.fmain2 = tk.Frame(self.parent, bd=2, relief=tk.RAISED)
        self.fmain2.grid(row=self.frow, rowspan=self.treeheight_cat,
                         column=1, columnspan=3)
        self.frow += self.treeheight_cat+1

    def create_frame2(self):
        self.frame2 = tk.Frame(self.parent, bd=2, padx=2,
                               pady=2, relief=tk.RAISED)
        self.frame2.grid(row=self.frow, rowspan=2, column=0,
                         columnspan=4, sticky='ew')
        self.fb1 = tk.Button(self.frame2, text='Choose',
                             command=self.get_dir)
        self.fb1.grid(row=0, column=0, sticky='ns')
        self.f2l1 = tk.Label(self.frame2, bd=2, text='Destination Directory: ')
        self.f2l1.grid(row=0, column=1, sticky='w')
        self.f2l2 = tk.Label(self.frame2, textvar=self.dest_dir)
        self.f2l2.grid(row=0, column=2, sticky='w')
        self.frow += 2

    def create_frame3(self):
        self.items_in_tree = 0
        self.frame3a = tk.Frame(self.parent, bd=2, padx=2,
                               pady=2, relief=tk.RAISED)
        self.frame3a.grid(row=self.frow, rowspan=self.treeheight_download, column=0,
                         sticky='nsew')
        self.frame3b = tk.Frame(self.parent, bd=2, padx=2,
                               pady=2, relief=tk.RAISED)
        self.frame3b.grid(row=self.frow, rowspan=self.treeheight_download, column=1,
                         columnspan=4, sticky='nsew')

        self.download_tree = ttk.Treeview(self.frame3b,
                                 height=self.treeheight_download,
                                 padding=(2, 2, 2, 2),
                                 selectmode="extended")
        self.download_tree.heading('#0', text='Files to download',
                                   anchor=tk.CENTER)
        self.download_tree.column('#0', stretch=tk.YES, width=400)

        tree_down_scrolly = tk.Scrollbar(self.frame3b, orient=tk.VERTICAL,
                                   command=self.download_tree.yview)

        tree_down_scrolly.grid(row=0, rowspan=self.treeheight_download,
                         column=4, sticky='ns')

        tree_down_scrollx = tk.Scrollbar(self.frame3b, orient=tk.HORIZONTAL,
                                   command=self.download_tree.xview)
        tree_down_scrollx.grid(row=self.treeheight_download + 1, column=0,
                         columnspan=4, sticky='ew')
        self.download_tree.configure(yscroll=tree_down_scrolly)
        self.download_tree.configure(xscroll=tree_down_scrollx)
        self.download_tree.grid(row=0, rowspan=self.treeheight_download,
                                column=1, columnspan=3, sticky='nsew')
        self.b1 = tk.Button(self.frame3a, text='Get Files', padx=2, pady=2, bd=2,
                            relief=tk.RAISED, command=self.download)
        self.b1.grid(row=0, column=0, sticky='nsew')
        self.b2 = tk.Button(self.frame3a, text='Exit', padx=2, pady=2, bd=2,
                            relief=tk.RAISED, command=self.quit)
        self.b2.grid(row=2, column=0, sticky='nsew')
        self.frow += self.treeheight_download + 1

    def get_dir(self):
        d = str(tfd.askdirectory())
        print('d: {}'.format(d))
        self.dest_dir.set(d)

    def quit(self):
        self.parent.destroy()

    def create_tree(self):
        treestyle = ttk.Style()
        treestyle.configure('Treeview.Heading', foreground='white',
                            borderwidth=2, background='SteelBlue',
                            rowheight=self.treeheight_cat,
                            height=3)

        self.tree = ttk.Treeview(self.fmain1,
                                 height=self.treeheight_cat,
                                 padding=(2, 2, 2, 2),
                                 columns=('Year'),
                                 selectmode="extended")

        self.tree.heading('#0', text='Category', anchor=tk.CENTER)
        self.tree.heading('#1', text='Year', anchor=tk.CENTER)
        self.tree.column('#0', stretch=tk.YES, width=180)
        self.tree.column('#1', stretch=tk.YES, width=50)

        vatid = 1
        for category, ignore in self.data['url_dict'].items():
            if category == 'DataDictionary':
                continue
            id = '{}'.format(vatid)
            # print('id: {}, category: {}'.format(id, category))
            self.tree.insert('', iid=id, index='end',
                             text='{}'.format(category))
            subid = 1
            all_added = False
            for year, url in self.data['url_dict'][category].items():
                sid = '{}_{}'.format(id, subid)
                if not all_added:
                    self.tree.insert(id, iid=sid, index='end',
                                     text='{}'.format(category),
                                     value='All')
                    all_added = True
                else:
                    self.tree.insert(id, iid=sid, index='end',
                                     text='{}'.format(category),
                                     value='{}'.format(year))
                subid += 1
            vatid += 1
        self.tree.tag_configure('monospace', font='courier')
        treescrolly = tk.Scrollbar(self.fmain1, orient=tk.VERTICAL,
                                   command=self.tree.yview)
        treescrolly.grid(row=0, rowspan=self.treeheight_cat, column=1, sticky='ns')

        treescrollx = tk.Scrollbar(self.fmain1, orient=tk.HORIZONTAL,
                                   command=self.tree.xview)
        treescrollx.grid(row=self.treeheight_cat + 1, column=0, columnspan=2, sticky='ew')
        self.tree.configure(yscroll=treescrolly)
        self.tree.configure(xscroll=treescrollx)
        self.tree.grid(row=0, rowspan=self.treeheight_cat, column=0, sticky='nsew')
        self.tree.bind('<Double-1>', self.file_selected)

    def create_textwin(self):
        self.textwin = tk.Text(self.fmain2, bd=2, bg='#CEF6EC',
                               width=113, relief=tk.RAISED)

        txscrolly = tk.Scrollbar(self.fmain2, orient=tk.VERTICAL,
                                   command=self.textwin.yview)
        txscrolly.grid(row=0, rowspan=self.treeheight_cat+1, column=5, sticky='ns')

        txscrollx = tk.Scrollbar(self.fmain2, orient=tk.HORIZONTAL,
                                   command=self.textwin.xview)
        txscrollx.grid(row=self.treeheight_cat+2, column=3, columnspan=2, sticky='ew')


        txscrollx.config(command=self.textwin.xview)
        txscrolly.config(command=self.textwin.yview)

        # self.textwin.configure(yscrollcommand=txscrolly.set)
        # self.textwin.configure(xscrollcommand=txscrollx.set)

        # self.textwin.configure(yscroll=txscrolly)
        # self.textwin.configure(xscroll=txscrollx)

        self.textwin.grid(row=0, rowspan=self.treeheight_cat+1, column=3,
                          columnspan=2, padx=2, pady=2, sticky='nsew')

        self.textwin.tag_configure('center', justify='center')

        self.textwin.insert('end', 'Data Dictionary\n')
        # self.textwin('center', 1.0, 'end')
        for key, value in self.data['data_dict'].items():
            # print('key: {}, value: {}'.format(key, value))
            line = '\n{} -- {}\n'.format(key, value)
            self.textwin.insert(tk.END, line)
            self.textwin.insert(tk.END, '-------------------------------------------------------')

    def create_statusbar(self):
        self.sb = tk.Frame(self.parent, bd=2, padx=2,
                               pady=2)
        self.sb.grid(row=self.frow, rowspan=2, column=0,
                         columnspan=4, sticky='nsew')
        self.sbl1 = tk.Label(self.sb, bd=2, textvariable=self.status)
        self.sbl1.grid(row=0, column=0, sticky='nsew')


    def file_selected(self, event):
        curitem = self.tree.focus()
        cdict = self.tree.item(curitem)
        category = cdict['text']
        year = cdict['values'][0]
        if year == 'All':
            for nyear, url in self.data['url_dict'][category].items():
                if url in self.download_list:
                    tmb.showerror('Select File', 'File already in list')
                    break
                self.download_list.append(url)
                self.download_tree.insert('', index='end', text='{}'.format(url))
        else:
            url = self.data['url_dict'][category][str(year)]
            # print('category: {}, year: {}, url: {}'.format(category, year, url))
            if url in self.download_list:
                tmb.showerror('Select File', 'File already in list')
            else:
                self.download_list.append(url)
                self.download_tree.insert('', index='end', text='{}'.format(url))

    def download(self):
        if self.dest_dir.get() == 'Not defined':
            tmb.showerror('Download dir', 'Please specify download directory')
        elif len(self.download_list) == 0:
            tmb.showerror('Download files', 'Please select some files')
        else:
            for url in self.download_list:
                urlsplit = urlparse(url)
                basename = os.path.basename(urlsplit.path)
                # print('urlsplit: {}'.format(urlsplit))
                outfile = '{}/{}'.format(self.dest_dir.get(), basename)
                # print('outfile: {}'.format(outfile))
                self.status.set('downloading file: {}'.format(url))
                with open(outfile, 'wb') as fo:
                    response = requests.get(url)
                    fo.write(response.content)
                self.status.set('Clearing download list: {}'.format(url))
                self.download_list = []
                for row in self.download_tree.get_children():
                    self.download_tree.delete(row)
                self.status.set('Download Complete: {}'.format(url))


if __name__ == '__main__':
    tt = CaCompGui(title='California City Compensation Datasets')
