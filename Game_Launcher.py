# Import necessary libraries for GUI, file handling, HTTP requests, subprocess management, etc.
import subprocess, sys, wx.adv, wx, shutil, io, zipfile, requests, os, ctypes
from subprocess import Popen, PIPE
from wx.lib.agw.aui import close_bits
from wx.lib.pydocview import Print

# Define repository URL and local directories
repo_url = "https://github.com/NotVeryLuvley/Game_Launcher_Project"
zip_url = f"{repo_url}/archive/refs/heads/main.zip"
local_dir = os.path.join(os.getcwd(), "Games")
version_file = os.path.join(local_dir, "downloaded.flag")

# Hide the console window on Windows
def hide_console():
    if sys.platform == "win32":
        kernel32 = ctypes.WinDLL('kernel32')
        hwnd = kernel32.GetConsoleWindow()
        if hwnd != 0:
            ctypes.windll.user32.ShowWindow(hwnd, 0)

# Show the console window on Windows
def show_console():
    if sys.platform == "win32":
        kernel32 = ctypes.WinDLL('kernel32')
        hwnd = kernel32.GetConsoleWindow()
        if hwnd != 0:
            ctypes.windll.user32.ShowWindow(hwnd, 5)

# Download and extract the game repository from GitHub
def download_games():
    show_console()
    print("Downloading latest version from GitHub...")
    try:
        response = requests.get(zip_url)
        if response.status_code == 200:
            print("Download successful. Extracting...")
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))

            temp_dir = os.path.join(os.getcwd(), "Temp_Games")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            zip_file.extractall(temp_dir)
            extracted_dir = os.path.join(temp_dir, "Game_Launcher_Project-main")

            if os.path.exists(local_dir):
                shutil.rmtree(local_dir)
            shutil.move(extracted_dir, local_dir)

            with open(version_file, "w") as f:
                f.write("Downloaded")

            shutil.rmtree(temp_dir)
            print("Games updated successfully.")
            hide_console()
        else:
            print(f"Failed to download. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading or extracting repository: {e}")

# Download games only if the version flag does not exist
if not os.path.exists(version_file):
    print("already installed")
    download_games()

# Delete the downloaded flag file to force re-download on next launch
def delete_flag():
    if os.path.exists(version_file):
        os.remove(version_file)
        print("Flag file deleted. The next launch will re-download the repository.")
    else:
        print("Flag file not found. No need to delete.")

# Find all .exe games in a directory and associate them with icons
def find_games(directory):
    games = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f == '.icon.png':
                icon = f

            if f.endswith('.exe'):
                games.append({
                    "name": os.path.splitext(f)[0].replace('_', ' '),
                    "file": os.path.join(root, f),
                    "icon": os.path.join(root, icon)
                })
                icon = ""
    return games

# Load games from the "Games" directory
games = find_games(r"Games")
print(games)

# Scrollable panel that displays available games as buttons with icons
class game_scrollable(wx.ScrolledWindow):
    def __init__(self, parent):
        self.font = wx.Font(30, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_THIN)
        super().__init__(parent, style=wx.VSCROLL | wx.HSCROLL)
        self.SetFocusIgnoringChildren()
        self.vert_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vert_sizer)
        self.SetBackgroundColour(wx.Colour(wx.Colour(40,40,40)))

        for game in games:
            self.default_color = wx.Colour(25, 25, 25)
            self.hover_color = wx.Colour(60, 60, 60)
            game_name = game['name'].replace("_"," ")
            image_path = game['icon']
            img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
            img = img.Scale(200, 200)
            img_bitmap = wx.StaticBitmap(self, -1, wx.Bitmap(img), pos=(10, 10))

            button = wx.Button(self, label=f"Play {game_name}", size=(500, 100),style=wx.BORDER_NONE)
            button.SetFont(self.font)
            button.SetBackgroundColour(self.default_color)
            button.SetForegroundColour(wx.Colour(255, 255, 255))

            button.Bind(wx.EVT_BUTTON, lambda event, g=game: self.on_game_click(event, g))
            button.Bind(wx.EVT_ENTER_WINDOW, self.on_hover)
            button.Bind(wx.EVT_LEAVE_WINDOW, self.on_leave)

            self.hori_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.hori_sizer.Add(img_bitmap, 0, wx.ALL | wx.EXPAND, 5)
            self.hori_sizer.Add(button, 0, wx.ALL | wx.EXPAND, 5)
            self.vert_sizer.Add(self.hori_sizer, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        self.SetScrollRate(10, 20)

    # Launch the game and minimize the launcher
    def on_game_click(self,event,g,):
        subprocess.Popen(g['file'], cwd=os.path.dirname(g['file']), stderr=subprocess.PIPE)
        self.GetParent().Iconize(True)

    # Change button color on hover
    def on_hover(self, event):
        button = event.GetEventObject()
        button.SetBackgroundColour(self.hover_color)
        button.Refresh()

    # Reset button color on leave
    def on_leave(self, event):
        button = event.GetEventObject()
        button.SetBackgroundColour(self.default_color)
        button.Refresh()

# Main application frame
class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title='Launcher', size=(1200, 800), style=wx.NO_BORDER | wx.FRAME_SHAPED)

        self.close_font = wx.Font(20, wx.FONTFAMILY_SCRIPT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        self.title_bar = wx.Panel(self, size=(940, 40), style=wx.NO_BORDER)
        self.title_bar.SetBackgroundColour(wx.Colour(20, 20, 20))

        self.title_label = wx.StaticText(self.title_bar, label="Launcher", pos=(10, 10))
        self.title_label.SetForegroundColour(wx.Colour(255, 255, 255))

        # Close button
        close_button = wx.Button(self.title_bar, label="x", size=(30, 30), style=wx.BORDER_NONE)
        close_button.SetFont(self.close_font)
        close_button.SetBackgroundColour(wx.Colour(200, 50, 50))
        close_button.SetForegroundColour(wx.Colour(255, 255, 255))
        close_button.Bind(wx.EVT_BUTTON, self.on_close)
        close_button.SetPosition((1160, 5))

        # Minimize button
        minimize_button = wx.Button(self.title_bar, label="-", size=(30, 30), style=wx.BORDER_NONE)
        minimize_button.SetFont(self.close_font)
        minimize_button.SetBackgroundColour(wx.Colour(50, 50, 50))
        minimize_button.SetForegroundColour(wx.Colour(255, 255, 255))
        minimize_button.Bind(wx.EVT_BUTTON, self.on_minimize)
        minimize_button.SetPosition((1120, 5))

        # Update/download button
        update_button = wx.Button(self.title_bar, label="^", size=(30, 30), style=wx.BORDER_NONE)
        update_button.SetFont(self.close_font)
        update_button.SetBackgroundColour(wx.Colour(0, 150, 0))
        update_button.SetForegroundColour(wx.Colour(0, 0, 0))
        update_button.Bind(wx.EVT_BUTTON, self.on_update)
        update_button.SetPosition((1080, 5))

        self.title_bar.Bind(wx.EVT_LEFT_DOWN, self.on_drag_start)
        self.title_bar.Bind(wx.EVT_MOTION, self.on_drag_move)

        # Add the scrollable game panel below the title bar
        self.panel = game_scrollable(self)
        frame_sizer = wx.BoxSizer(wx.VERTICAL)
        frame_sizer.Add(self.title_bar, 0, wx.EXPAND)
        frame_sizer.Add(self.panel, 1, wx.EXPAND)

        self.SetSizer(frame_sizer)
        self.Layout()
        self.Centre()
        self.Show()

        self.dragging = False
        self.drag_pos = wx.Point(0, 0)

    # Handle game update
    def on_update(self, event):
        delete_flag()
        download_games()
        global games
        games = find_games(r"Games")
        self.panel.Destroy()
        self.panel = game_scrollable(self)
        self.GetSizer().Add(self.panel, 1, wx.EXPAND)
        self.Layout()

    def on_close(self, event):
        self.Close()

    def on_minimize(self, event):
        self.Iconize(True)

    # Start dragging the window
    def on_drag_start(self, event):
        self.dragging = True
        self.drag_pos = event.GetPosition()

    # Move window with drag
    def on_drag_move(self, event):
        if self.dragging and event.Dragging() and event.LeftIsDown():
            x, y = self.ClientToScreen(event.GetPosition())
            origin = self.ClientToScreen(self.drag_pos)
            dx = x - origin[0]
            dy = y - origin[1]
            pos = self.GetPosition()
            self.Move(pos.x + dx, pos.y + dy)

    def on_drag_end(self, event):
        self.dragging = False

# Start the application
app = wx.App(redirect=False)
frame = MyFrame()
frame.Show()
app.MainLoop()
