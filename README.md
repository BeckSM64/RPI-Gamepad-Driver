# Raspberry Pi Portable Gamepad Driver
This is a driver I wrote for the gamepad for my Raspberry Pi Portable running RetroPie. All of the buttons are connected to available GPIO pins as well as the two HiLetgo Analog Joy Sticks.

# Motivation
The main motivation to write this instead of using something like [GPIOnext](https://github.com/mholgatem/GPIOnext) was the joysticks. I couldn't seem to find anywhere online that solved the problem of converting the analog value from the sticks to a digital value that the pie can read and use for retro gaming. I'm sure someone has done it, but I had no luck when it came to these specific joysticks, or something similar like the AdaFruit analog sticks. And analog sticks were a requirement for my project as I was intending to use this portable RetroPie to play Playstation 1 games, mainly Ape Escape, which requires analog input.

# Phyiscal Parts this Software Supports
I used a few specific parts that this software interfaces with. The buttons are simply tact switches wired directly to the GPIO pins. There is nothing special about those. But for the analog sticks, I used HiLetgo Joysticks I found on Amazon. For the Analog Digital Converter (ADC), I'm using the NOYITO PCF8591 Analog to Digital Converter that I also found on amazon. I'll list links to where I bought each part below.

- [HiLetgo Analog Stick](https://www.amazon.com/HiLetgo-Controller-JoyStick-Breakout-Arduino/dp/B00P7QBGD2)
- [NOYITO PCF8591 ADC](https://www.amazon.com/dp/B07DQGQYJW?psc=1&ref=ppx_yo2ov_dt_b_product_details)

# Issues
The problem with these joysticks is they kind of are terrible. They feel great, but the values read seem to be inaccurate. For example, on one of the sticks I got, the Y value produced the exact expected values once run through the ADC, but the X Axis had a range of 2 -> 252 with a mid value (neutral position) of 207. A correct reading would be a range of 0 -> 255 with a mid value of 128. It'll never be perfect, but this was WAY off. I accounted for this in the software. Right now, the software is hardcoded for my specific joysticks. Both of mine read different values, so I handled them directly in code. I'll update this in the future to be more abstract and maybe right some callibration software. But know that if you use this software in its current state, you'll need to figure out what values you're reading off the ADC yourself for your specific sticks and account for it in the code.
