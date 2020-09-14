This program connects the RPi-Cam-Web-Interface from Silvan Melchior and Robert Tidey to a remote PC. The images from the PI are streamed to the PC which uses AI to classify them. In our case we triggered a video recording when birds were detected in the image.
It basically works like this:

- grab a frame from the PI using a http call 
- start the inference (single shot detection)
- if birds are detected start recording on the PI using a ssh call
- if birds are not detected stop the recording using a ssh call

The http call to grab a frame from the PI is a simple GET to http://<IP_of_PI>/html/get_pic.php. The video recording can be triggered by sending a short string to a pipe monitored by the raspimjpeg process installed with the RPi Cam Web Interface (ssh echo "vi 1" >/var/www/html/FIFO11).

No modifications to the standard installation are required PI side but this has one drawback. There is currently no known way to annotate the detected birds with boxes and detection scores within the PI stream. This can only be done on the inference PC as the image above demonstrates. The image above is not of a high quality as it has been reduced in size to speed things up and we do not require the higher resolution of the original stream image to detect birds. The only option known to us is to use the pipe communication to change the annotation of the stream (echo an "birds found" >/var/www/html/FIFO11) does the trick! 

Stephen