import customtkinter as ctk
from datetime import datetime
import pandas as pd
import requests
import tkinter as tk
from tkinter import filedialog

app = ctk.CTk()
app.geometry('500x250')
app.resizable(False, False)
app.sourceFolder = ''
app.urls_file = 'urls.txt'
app.results = tk.StringVar()
app.title('URL StatusCheck')


def messagebox(message, title):
    toplevel = tk.Toplevel(app)
    toplevel.title(title)
    toplevel.geometry(f"250x100+{app.winfo_x() + 125}+{app.winfo_y() + 75}")
    message_lbl = ctk.CTkLabel(toplevel, text=message, font=('System', 16))
    message_lbl.place(relx=0.5, y=30, anchor=tk.CENTER)
    ok_btn = ctk.CTkButton(toplevel, text="Ok", command=toplevel.destroy, width=45)
    ok_btn.place(relx=0.5, y=65, anchor=tk.CENTER)


def choose_file():
    app.urls_file = filedialog.askopenfilename(parent=app, initialdir="/", title='Please select a directory')
    browse_url_ent.delete(0, 9999)
    browse_url_ent.insert(0, app.urls_file)
    app.results.set('')


def add_url():
    new_url = add_url_ent.get().lower()

    # DONT ADD EMPTY LINES TO URLS.TXT
    if new_url == '':
        messagebox('Input Field is Empty', 'Input Error')
        return

    # FORMAT USER INPUT INTO VALID URL
    if new_url[0:7] != 'http://':
        new_url = 'http://' + new_url

    # APPEND URL TO LIST FILE
    filename = open(app.urls_file, 'a')
    filename.write(new_url.strip() + '\n')
    filename.close()
    add_url_ent.delete(0, 9999)
    messagebox('URL Added', 'Add URL')


def clear_error_log():
    # CLEARS THE ERROR REPORTS FROM THE LOG CSV FILE
    filename = open('error_log.csv', 'w')
    filename.write('url,status,timestamp\n')
    filename.close()
    messagebox('Error Log Cleared', 'Clear Log')


def get_timestamp():
    now = datetime.now()
    timestamp = now.strftime("%m-%d-%Y %H:%M:%S")
    return timestamp


def get_status(url):
    try:
        request = requests.get(url, timeout=5)
        return request.status_code
    except:
        return 999


def get_pass_ratio(bad_urls):
    # RETURN ARRAY WITH NUMBER OF ACTIVE URLS & TOTAL URLS
    urls = set(open(app.urls_file).read().split())
    return [len(urls) - len(bad_urls), len(urls)]


def log_errors(bad_urls):
    columns = ['url', 'status', 'timestamp']
    data_frame = pd.DataFrame(list(zip(bad_urls[0], bad_urls[1], bad_urls[2])), columns=columns)
    data_frame.to_csv('error_log.csv', mode='a', header=False, index=False)
    del data_frame


def check_urls():
    urls = set(open(app.urls_file).read().split())
    bad_urls = []
    status_codes = []
    timestamps = []
    for url in urls:
        print(url)
        status = get_status(url)
        if status != 200:
            bad_urls.append(url)
            status_codes.append(status)
            timestamps.append(get_timestamp())
    return [bad_urls, status_codes, timestamps]


def run_status_check():
    bad_urls = check_urls()
    log_errors(bad_urls)
    ratio = get_pass_ratio(bad_urls[0])
    app.results.set(f'Online: {ratio[0]} / {ratio[1]}')


# GUI DESIGN
browse_url_ent = ctk.CTkEntry(master=app, placeholder_text=app.urls_file,
                              width=330, height=45, corner_radius=4, font=('System', 22), takefocus=False)
browse_url_ent.place(x=40, y=20)
url_list = browse_url_btn = ctk.CTkButton(master=app, text='Browse', width=75, height=45, command=choose_file)
browse_url_btn.place(x=390, y=20)

add_url_ent = ctk.CTkEntry(master=app, placeholder_text='http://',
                           width=330, height=45, corner_radius=4, font=('System', 22), takefocus=False)
add_url_ent.place(x=40, y=85)
add_url_btn = ctk.CTkButton(master=app, text='Add URL', width=75, height=45, command=add_url)
add_url_btn.place(x=390, y=85)

run_check_btn = ctk.CTkButton(master=app, text='Run Status Check', width=330, height=45, command=run_status_check)
run_check_btn.place(x=40, y=150)

error_log_btn = ctk.CTkButton(master=app, text='Clear Log', width=75, height=45, command=clear_error_log)
error_log_btn.place(x=390, y=150)

results_lbl = ctk.CTkLabel(master=app, textvariable=app.results, font=('System', 24), text_color='#717171')
results_lbl.place(relx=0.5, y=220, anchor=tk.CENTER)

app.mainloop()
