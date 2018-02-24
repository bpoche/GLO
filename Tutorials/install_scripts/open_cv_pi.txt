#!/bin/bash
# full update
sudo apt-get update
sudo apt-get -y upgrade
sudo rpi-update

# reboot required
read -r -p "You may need to reboot your RPi. Would you like to do that? [y/N] " response
if [[ $response =~ ^([yY][eE][sS]|[yY])$ ]]
then
    sudo reboot
fi

# install build git cmake and some others
sudo apt-get install -y build-essential checkinstall git cmake wget unzip

# ffmpeg dependencies
sudo apt-get install -y libjack-jackd2-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libsdl1.2-dev libtheora-dev libva-dev libvdpau-dev libvorbis-dev libx11-dev libxfixes-dev libxvidcore-dev texi2html yasm zlib1g-dev libsdl1.2-dev libvpx-dev

# install image codecs
sudo apt-get install -y libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev

# gstreamer
sudo apt-get install -y libgstreamer0.10-0 libgstreamer0.10-dev gstreamer0.10-tools gstreamer0.10-plugins-base libgstreamer-plugins-base0.10-dev gstreamer0.10-plugins-good gstreamer0.10-plugins-ugly gstreamer0.10-plugins-bad

# install video codecs
sudo apt-get install -y libavcodec-dev libavformat-dev libswscale-dev libv4l-dev v4l-utils
sudo apt-get install -y libxvidcore-dev libx264-dev x264

# GTK to support OpenCV GUI
sudo apt-get install -y libgtk2.0-dev libqt4-dev libqt4-opengl-dev

# matrix operations optimization
sudo apt-get install -y libatlas-base-dev gfortran

# install python 2 and 3 and some python libs with pip
sudo apt-get install -y python2.7-dev python3-dev python-pip
sudo apt-get install -y python-tk python-numpy python3-tk python3-numpy python-qt4

mkdir ~/source
cd ~/source
# ffmpeg from git repo
git clone https://github.com/FFmpeg/FFmpeg.git
cd FFmpeg/
# build ffmpeg
./configure --enable-gpl --enable-libmp3lame --enable-libopencore-amrnb --enable-libopencore-amrwb --enable-libtheora --enable-libvorbis --enable-libx264 --enable-libxvid --enable-nonfree --enable-postproc --enable-version3 --enable-x11grab --enable-shared --enable-libvpx --enable-pic
make
sudo make install
sudo ldconfig -v

# opencv compilation
sudo apt-get autoremove libopencv-dev python-opencv
# download opencv
cd ~/source
wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.1.0.zip
unzip opencv.zip
cd opencv-3.1.0/
mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D WITH_V4L=ON -D WITH_QT=ON -D INSTALL_C_EXAMPLES=OFF ..
make -j $(nproc)
sudo make install
sudo /bin/bash -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
sudo ldconfig -v