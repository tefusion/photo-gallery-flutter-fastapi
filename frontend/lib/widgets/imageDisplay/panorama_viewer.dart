import 'package:flutter/material.dart';
//for panorama 360 view
import 'Panorama/panorama.dart';
//mobile or desktop check
import 'package:flutter/foundation.dart' show defaultTargetPlatform;

class PanoramaViewer extends StatefulWidget {
  final ImageProvider<Object> image;
  const PanoramaViewer({Key key, this.image}) : super(key: key);

  @override
  _PanoramaViewerState createState() => _PanoramaViewerState();
}

class _PanoramaViewerState extends State<PanoramaViewer> {
  bool animated = true;
  bool isDesktop = !(defaultTargetPlatform == TargetPlatform.android ||
      defaultTargetPlatform == TargetPlatform.iOS);
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      child: Panorama(
        child: Image(
          image: widget.image,
        ),
        minZoom: 0.1,
        maxZoom: 20,
        isDesktop: isDesktop,
        sensorControl:
            isDesktop //if this stopped working look in motionSensors.absoluteOrientation
                //.listen((AbsoluteOrientationEvent event) { that _controller.forward() is existent. Otherwise screen not updated
                ? SensorControl.None
                : SensorControl //enable or disable when on Android
                    .Orientation,
        sensitivity: 1.5,
        animSpeed: animated ? 14 : 0,
        zoom: 0.7,
      ),
      onTap: () => Navigator.pop(context),
      onDoubleTap: () {
        setState(() {
          animated = !animated; //switch between image spinning and not spinning
        });
      },
    );
  }
}
