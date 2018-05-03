# Add wallpaper slide show

Default wallpaper slide show of Ubuntu are stored as a xml file at

<code>/usr/share/backgrounds/contest</code>

Using gnome-tweak-tool, user can set the background slide show

This simple Python script takes directories names (both absolute and relative) as parameters and add all images in each of them to a separated xml file and stores at
<code>/usr/share/backgrounds/contest</code>

Invalid directories names and non-image files are ignored.
The script does not scan directories recursively. 