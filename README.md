# WebServerGstreamer

## installation
### PyGObject
1) Go to http://www.msys2.org/ and download the x86_64 installer
2) Follow the instructions on the page for setting up the basic environment
3) Run C:\msys64\mingw32.exe - a terminal window should pop up
4) Execute pacman -Suy
5) Execute pacman -S mingw-w64-i686-gtk3 mingw-w64-i686-python2-gobject mingw-w64-i686-python3-gobject
6) To test that GTK+3 is working you can run gtk3-demo
7) Copy the hello.py script you created to C:\msys64\home\<username>
8) In the mingw32 terminal execute python3 hello.py - a window should appear.
9) download the Libraries https://sourceforge.net/projects/pygobjectwin32/files/ or run /install/pygi.exe
10) indicate location of python at C:\msys64\mingw32\bin
11) include 4 libraries  farstreamer, gst-pluginds, gst-plugins-more, gst-plugins-extra, Gstreamer
12) install anaconda
13) conda install -c anaconda django for django
14) pip install Django
15) django-admin startproject mysite (create a new project)
16) Run the web-server: python manage.py runserver
17) choco install sqlite 
18) conda install -c anaconda sqlalchemy 
19) https://www.pythoncentral.io/how-to-install-sqlalchemy/
