from textual.app import App, ComposeResult
from textual.containers import ScrollableContainer
from textual.widgets import Button, Footer, Header, Label, Static, Input
from textual.reactive import reactive
from textual import events
from textual.validation import Number
#from videoplayer import start, getmessage, controlkeys
import vlc
import time
import threading
import os

lock = threading.Lock()

class Controls(Static):
    """Contains the Buttons of controlling the app"""


    def compose(self) -> ComposeResult:
        self.bStart = Button("Start", id="start", variant="success")
        self.bOff = Button("Ausschalten", id="poweroff", variant="error")
        yield self.bStart
        yield self.bOff


    def disable(self) -> None:
        self.bStart.disabled = True
        self.bOff.disabled = True

    def enable(self) -> None:
        self.bStart.disabled = False
        self.bOff.disabled = False

class StatusDisplay(Static):
    message = reactive("Hallo")

    def render(self) -> str:
        return f"{self.message}"

    def setMessage(self, message) -> None:
        lock.acquire()
        self.message = message
        lock.release()

class InputFields(Static):
    """Contains input field for length of exhibition"""
    BINDINGS = [
        ("right", "focus_next", "Vor"),
        ("left", "focus_previous", "Zurück")
    ]

    def compose(self) -> ComposeResult:
        self.inputField = Input(
            placeholder="Dauer in Minuten",
            validators=[
                Number(minimum=10)
            ]
        )

        yield self.inputField

    def disable(self) -> None:
        self.inputField.disabled = True

    def enable(self) -> None:
        self.inputField.disabled = False

class Confirmation(Static):
    """Confirmation prompt before shutdown"""

    def compose(self) -> ComposeResult:
        self.hide()
        yield Label("Ausschalten?")
        yield Button("Ja", id="yes", variant="default")
        yield Button("Nein", id="no", variant="default")

    def show(self) -> None:
        self.add_class("show")
        self.remove_class("hide")

    def hide(self) -> None:
        self.remove_class("show")
        self.add_class("hide")



class ScaleGuiApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = "gui.tcss"
    BINDINGS = [("right", "focus_next", "Vor"),
                ("left", "focus_previous", "Zurück"),
                ("down", "focus_next", "Vor"),
                ("up", "focus_previous", "Zurück")]



    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield ScrollableContainer(StatusDisplay(), InputFields(), Controls(), Confirmation())


    def startplayer(self) -> None:
        # videoplayer
        self.end_videos = False
        self.currentVideo = 0
        self.transition_max_duration = 5
        self.repeat_max_duration = 9
        instance = vlc.Instance()
        self.mplayer = instance.media_list_player_new()
        mlist = instance.media_list_new()

        root_dir_path = "/home/ausstellung/videoplayer/files/"

        media_repeat = instance.media_new(root_dir_path + "repeat/10sec.mp4")
        mlist.add_media(media_repeat)
        self.vid_name_list = [root_dir_path + "repeat/10sec.mp4"]


        # get time frame
        inputValue = self.query_one(Input).value
        if not inputValue.isnumeric():
            self.output_field.setMessage("Zeitangabe falsch. Starte mit Gesamtdauer von 10 Minuten.")
            inputValue = 10
            self.stageTimeMaxSeconds = float(inputValue)/20*60
        else:
            if float(inputValue) < 10: 
                inputValue = 10
            self.stageTimeMaxSeconds = float(inputValue)/20*60
            self.output_field.setMessage("Gesamtdauer gegeben: " + str(inputValue) + ", Wechsel alle " + str(self.stageTimeMaxSeconds/60) + " Minuten.")
        

        # there are 41 videos overall
        for i in range(1, 21):
            media_transition = instance.media_new(root_dir_path + "transition/" + str(i) + ".mp4")
            media_repeat = instance.media_new(root_dir_path + "repeat/10sec_" + str(i) + ".mp4")
            mlist.add_media(media_transition)
            mlist.add_media(media_repeat)
            self.vid_name_list.append(root_dir_path + "transition/" + str(i) + ".mp4")
            self.vid_name_list.append(root_dir_path + "repeat/10sec_" + str(i) + ".mp4")

        self.mplayer.set_media_list(mlist)
        self.mplayer.play_item_at_index(self.currentVideo)

        self.loopVideo_start_time = time.time()
        # for debugging:
        self.transition_start_time = time.time()
        self.in_transition = False

        self.stage_start_time = time.time()

        self.thread1 = threading.Thread(target=self.run_time_checks, name='thread1')
        self.thread1.start()


    def run_time_checks(self):
        #self.output_field.setMessage("started loop")
        counter = 0

        while not self.end_videos:
            counter += 1
            #self.output_field.setMessage(counter)
            #self.output_field.setMessage("in loop, video: " + str(self.currentVideo) + ", count: " + str(counter)
            #            + ", loop time: " + str(self.loopVideo_start_time) + ", t time: " + str(self.transition_start_time)
            #            + "in Transition: " + str(self.in_transition))
            #self.output_field.setMessage(self.vid_name_list[self.currentVideo])
            if self.in_transition:
                transition_duration = time.time() - self.transition_start_time
                if transition_duration > self.transition_max_duration:
                    lock.acquire()
                    self.loopVideo_start_time = time.time()
                    self.in_transition = False
                    self.currentVideo += 1
                    self.mplayer.next()
                    lock.release()
                    #print("auto: changing to repeat video #" + str(self.currentVideo))

            else:
                loop_duration = time.time() - self.loopVideo_start_time
                if loop_duration > self.repeat_max_duration:
                    lock.acquire()
                    self.loopVideo_start_time = time.time()
                    self.mplayer.play_item_at_index(self.currentVideo)
                    lock.release()
                stage_duration = time.time() - self.stage_start_time
                if stage_duration > self.stageTimeMaxSeconds:
                    self.stage_start_time = time.time()
                    self.goToNextVideo()
            time.sleep(0.05)

        self.mplayer.stop()
        os.system('clear')
        self.refresh()
        self.output_field.setMessage("Video beendet")


    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.output_field = self.query_one(StatusDisplay)
        button_id = event.button.id
        confirmation = self.query_one(Confirmation)
        controls = self.query_one(Controls)
        inputF = self.query_one(InputFields)
        if button_id == "start":
            self.output_field.setMessage("Starte...")
            #self.exit(button_id)
            #start(0)
            #controlkeys()
            self.keyboard_special_enabled = True
            self.startplayer()
        elif button_id == "newscale":
            self.output_field.setMessage("Kalibriere...")
        elif button_id == "poweroff":
            self.output_field.setMessage("Ausschalten...")
            controls.disable()
            inputF.disable()
            confirmation.show()
        elif button_id == "yes":
            """TODO: shutdown"""
            os.system('shutdown -h now')
            self.exit(button_id)
        elif button_id == "no":
            confirmation.hide()
            controls.enable()
            inputF.enable()

    def key_q(self) -> None:
        self.end_videos = True
        self.exit()

    def key_b(self) -> None:
        if not self.keys_allowed():
            return
        if self.currentVideo > 1:
            lock.acquire()
            self.loopVideo_start_time = time.time()
            self.in_transition = False
            if self.currentVideo % 2 == 0:
                self.currentVideo -= 2
                self.mplayer.play_item_at_index(self.currentVideo)
            else:
                self.currentVideo -= 1
                self.mplayer.play_item_at_index(self.currentVideo)
            lock.release()

            #print("key input: changing to video #" + str(self.currentVideo) + ", is transition: " + str(self.in_transition))
        elif self.currentVideo == 1:
            lock.acquire()
            self.currentVideo = 0
            self.loopVideo_start_time = time.time()
            self.mplayer.play_item_at_index(0)
            lock.release()
            #print("key input: changing to video #" + str(self.currentVideo) + ", is transition: " + str(self.in_transition))


    def goToNextVideo(self) -> None:
        if self.currentVideo < 40:
            #loopVideo_start_time = time.time()
            #self.transition_start_time = time.time()
            lock.acquire()
            self.currentVideo += 1
            if (self.currentVideo % 2 == 1):
                self.transition_start_time = time.time()
                self.in_transition = True
            else:
                self.loopVideo_start_time = time.time()
                self.in_transition = False
            self.mplayer.next()
            lock.release()

    def key_n(self) -> None:
        if not self.keys_allowed():
            return
        self.goToNextVideo()
        self.stage_start_time = time.time()

            #print("key input: changing to video #" + str(self.currentVideo) + ", is transition: " + str(self.in_transition))


    def key_c(self) -> None:
        if not self.keys_allowed():
            return
        self.end_videos = True
        self.keyboard_special_enabled = False


    def action_exit_force(self) -> None:
        self.end_videos = True
        self.exit()


    def keys_allowed(self) -> bool:
        try:
            if self.keyboard_special_enabled == True:
                return True
        except (NameError, AttributeError) as error:
            return False
        return False


if __name__ == "__main__":
    app = ScaleGuiApp()
    app.run()
