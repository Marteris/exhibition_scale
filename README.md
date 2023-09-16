# Video Player

## How to start

- Connect HDMI Cable, Power Cable (with Power Button), Keyboard (USB-Stick)
- Optionally connect AUX audio cable
- Press button on power cable

The Raspberry Pi should start. If it works, you should see something like this:

![](screenshots/startscreen.png)


## Functions

You can navigate with the arrow keys. Press down to select "Start" or "Ausschalten".

Insert time as number. It sets the overall time of the playing video.
If the number is smaller than 10, it is automatically set to 10 minutes.

### Example

If you insert 30 minutes, then each stage of the video plays for 1 minute 30
seconds (30 : 20 = 1.5).

After 30 minutes, you should reach the last video (with the butterfly).
That video plays endlessly.

### Keyboard Functions During Video

- **N**: Next (switches to next video)
  - During the first five seconds of the video stages, the "transition" is shown.
  So you need to press twice to go to the next stage.
- **B**: Before (switches to previous video)
- **C**: Cancel (exit video and go back to start screen)
- **If nothing works**: Press Ctrl+Alt+Delete (Strg+Alt+Entf) or press power button
  - Restarts raspberry pi
  - Shouldn't be necessary in normal cases.
  - Might break something

### Keyboard Controls on Start Screen

- Use the arrow keys to switch between number field and buttons.
  - Up/Down, Left/Right
- Use keyboard to insert a number.
  - Only numbers, 2 hours is 120, not 2:00 or something.
- Use Enter to push a button.

Button is selected if it has the black background:

![](screenshots/buttonselected.png)
