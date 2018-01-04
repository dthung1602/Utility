# Add wallpaper directory

Default wallpapers of Ubuntu are stored at

<code>/usr/share/backgrounds</code>

In other to appear in settings/background, these pictures haves to be list in a xml file located at 

<code>/usr/share/gnome-background-properties
</code>

This simple Python script takes directories names (both absolute and relative) as parameters and add all images in each of them to a separated xml file and stores at <code>/usr/share/gnome-background-properties
</code>  

Invalid directories names and non-image files are ignored.
The script does not scan directories recursively. 