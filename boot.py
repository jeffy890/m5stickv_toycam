import sensor, image, time, lcd, uos
from Maix import GPIO
from fpioa_manager import fm, board_info


lcd.init(freq=15000000)
lcd.rotation(2)

# directory check
dirData = uos.getcwd()

# move to sd
if dirData != "/sd":
    uos.chdir("/sd")

# directory "pictures" is for saving pictures
dirList = uos.listdir()
dirFlag = 0
savingDir = "pictures"
for i in dirList:
    if i == savingDir:
        dirFlag = 1

# if there's no directory "pictures", make the "pictures" directory
if dirFlag == 0:
    uos.mkdir(savingDir)

# picNum is a counting variable for picture saving part
uos.chdir("/sd/pictures")
picNum = len(uos.listdir())

# run the sensor
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
clock = time.clock()
sensor.run(1)


# button settings
fm.register(board_info.BUTTON_A, fm.fpioa.GPIO1)
button_a = GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP)
fm.register(board_info.BUTTON_B, fm.fpioa.GPIO2)
button_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP)
# led setting
fm.register(board_info.LED_R, fm.fpioa.GPIO0)
led_r = GPIO(GPIO.GPIO0, GPIO.OUT)
fm.register(board_info.LED_G, fm.fpioa.GPIO4)
led_g = GPIO(GPIO.GPIO4, GPIO.OUT)
fm.register(board_info.LED_B, fm.fpioa.GPIO3)
led_b = GPIO(GPIO.GPIO3, GPIO.OUT)
ledFlag = 0
led_r.value(1)
led_g.value(1)
led_b.value(1)
# variables for button chattering
countButA = 0
countButB = 0


#preview
def previewPic():
    dirName = "/sd/pictures/"
    listname = uos.listdir()
    countNum = 1
    posX = 12
    posY = 20

    preview = image.Image()
    for j in (reversed(listname)):
        prevList = dirName + j
        preview.draw_image(image.Image(prevList).resize(36,27), posX, posY)

        posX += 36
        if countNum%6 == 0:
            posX = 12
            posY += 27
        if countNum == 25:
            posX = 12
            posY = 20
            coutNum = 1
            break
        countNum += 1
        lcd.display(preview)
    countButAinP = 0
    countButBinP = 0
    while(True):
        if button_a.value() == 0:
            countButAinP += 1
            time.sleep(0.1)
        if button_b.value() == 0:
            countButBinP += 1
            time.sleep(0.1)
        if countButBinP >= 3 or countButAinP >= 3:
            break

# light the led
def litLed(ledFlag):
    ledFlag = not ledFlag
    led_r.value(ledFlag)
    led_g.value(ledFlag)
    led_b.value(ledFlag)
    return ledFlag

# main loop
while(True):
    img = sensor.snapshot()         # Take a picture and return the image.
    tmp = img.resize(180,135)       # Resize the image
    lcd.display(tmp)                # Display on LCD

    # count the number for button A
    if button_a.value() == 0:
        countButA += 1
        time.sleep(0.1)

    # button b has two functions
    if button_b.value() == 0:
        while(True):
            if button_b.value() == 1:
                # if button B plessed longer, light the led
                if countButB >= 10:
                    ledFlag = litLed(ledFlag)
                    countButB = 0
                # if button B plessed not so longer, preview mode
                if countButB >=5:
                    ledFlag = litLed(0)     # before entering preview, off the led
                    previewPic()
                    countButB = 0
                countButB = 0
                break
            countButB += 1
            time.sleep(0.1)

    # image saving part
    if countButA >= 2:
        filename = "/sd/pictures/{0:0=8}.jpg".format(picNum)
        img.save(filename)
        picNum += 1
        lcd.draw_string(10,115,filename, lcd.WHITE, lcd.BLACK)
        countButA = 0
        time.sleep(0.6)
