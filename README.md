# WebServerGstreamer

## installation
### PyGObject

1) https://developer.microsoft.com/en-US/windows/downloads/windows-10-sdk
2) install Choco
3) choco install -y python2 gtk-runtime microsoft-build-tools libjpeg-turbo
2) install python
3) hook up system env to python/scripts
4) run  pip install PyGObject
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
11) include 4 libraries  farstreamer, gst-pluginds, gst-plugins-more, gst-plugins-extra, Gstreamer, gtk+

### Django install
1) install anaconda
2) conda install -c anaconda django for django
3) pip install Django
4) django-admin startproject mysite (create a new project)
5) Run the web-server: python manage.py runserver
6) choco install sqlite 
7) conda install -c anaconda sqlalchemy 
10) https://www.pythoncentral.io/how-to-install-sqlalchemy/


### Django usage
1) tutorials at https://docs.djangoproject.com/en/2.0/intro/tutorial01/
2) python manage.py migrate ( to migrate database)
3) python manage.py startapp polls (create a start app named )
4) make migrations when changing Model: python manage.py migrate
5) migrate new model: python manage.py sqlmigrate polls 0001
6) apply to database: python manage.py migrate

### django apps and framework
1) https://djangopackages.org/categories/apps/
2) https://djangopackages.org/categories/frameworks/

### django CMS
1) http://docs.django-cms.org/en/latest/introduction/install.html


