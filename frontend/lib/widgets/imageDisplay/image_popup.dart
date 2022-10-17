import 'package:flutter/gestures.dart';
import 'package:flutter/material.dart';
import 'package:image_server/widgets/imageDisplay/panorama_viewer.dart';
import 'package:photo_view/photo_view.dart';
import 'package:image_server/other/tile_data.dart';
import 'package:image_server/other/backend_connect.dart' as backend;
//for determining height
import 'dart:async';

/// Base Class for showing an image
/// can handle swiping left,right, and down (for pano view)
/// upon just clicking closes popup again
class ImagePopup extends StatelessWidget {
  final ImageData imageData;
  final Function showLeftImage;
  final Function showRightImage;

  const ImagePopup({
    Key key,
    this.imageData,
    this.showLeftImage,
    this.showRightImage,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    void manageSwipes(Offset velocity) {
      if (velocity.dx < -300) {
        showRightImage();
      } else if (velocity.dx > 300) {
        showLeftImage();
      }
    }

    ///function for showing a 360° view after clicking the button at the bottom, just opens another popup
    void showPanorama(ImageProvider<Object> image) {
      Navigator.push(context, new MaterialPageRoute(builder: (_) {
        return PanoramaViewer(image: image);
      }));
    }

    void showDescription(ImageProvider<Object> image) {}

    return FutureBuilder<ImageDisplayData>(
        future: fetchImageDisplayData(imageData),
        builder: (context, AsyncSnapshot<ImageDisplayData> snapshot) {
          PhotoViewController photoViewController = PhotoViewController();
          final ImagePointerManager pointerManager = new ImagePointerManager(
              showLeftImage: showLeftImage,
              showRightImage: showRightImage,
              showPanorama: () => showPanorama(snapshot.data.image),
              showDescription: () => showDescription(snapshot.data.image),
              threshold: 2.5);
          if (snapshot.hasData) {
            return GestureDetector(
              //detector only for tap to quit, because for dragging HitTestBehavior.translucent is not working
              child: Listener(
                  child: Container(
                    padding: EdgeInsets.symmetric(horizontal: 20),
                    child: Column(children: [
                      Expanded(
                        flex: 20,
                        child: Row(children: [
                          Visibility(
                              child: Expanded(
                                  flex: 1,
                                  child: FloatingActionButton(
                                    heroTag: "left",
                                    onPressed: () => showLeftImage(),
                                    backgroundColor: Colors.blueGrey,
                                    shape: RoundedRectangleBorder(
                                        borderRadius:
                                            BorderRadius.circular(20)),
                                    child: Icon(
                                      Icons.arrow_left_rounded,
                                      color: Colors.lightGreen,
                                      size: 33,
                                    ),
                                  )),
                              visible: snapshot.data.showButtons),
                          Expanded(
                            flex: 8,
                            child: Container(
                              padding: EdgeInsets.symmetric(horizontal: 20),
                              child: PhotoView(
                                imageProvider: snapshot.data.image,
                                filterQuality: FilterQuality.high,
                                backgroundDecoration: BoxDecoration(
                                    color: Colors.transparent,
                                    backgroundBlendMode: BlendMode.darken),
                                basePosition: snapshot.data.alignment,
                                initialScale: snapshot.data.initialScale,
                                gestureDetectorBehavior:
                                    HitTestBehavior.translucent,
                                controller: photoViewController,
                              ),
                            ),
                          ),
                          Visibility(
                            child: Expanded(
                                flex: 1,
                                child: FloatingActionButton(
                                  heroTag: "right",
                                  onPressed: () => showRightImage(),
                                  backgroundColor: Colors.blueGrey,
                                  shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(20)),
                                  child: Icon(
                                    Icons.arrow_right_rounded,
                                    color: Colors.lightGreen,
                                    size: 33,
                                  ),
                                )),
                            visible: snapshot.data.showButtons,
                          )
                        ]),
                      ),
                      Visibility(
                          child: Expanded(
                              flex: 1,
                              child: Center(
                                child: Column(
                                  children: [
                                    Text(imageData.description),
                                    Expanded(
                                        child: GestureDetector(
                                      onTap: () =>
                                          showPanorama(snapshot.data.image),
                                      child: Container(
                                        width: 30,
                                        height: 15,
                                        decoration:
                                            BoxDecoration(color: Colors.green),
                                        child: Text(
                                          "360°",
                                          textAlign: TextAlign.center,
                                        ),
                                      ),
                                    ))
                                  ],
                                ),
                              )))
                    ]),
                    constraints: BoxConstraints.expand(),
                  ),
                  onPointerMove: pointerManager.onPointerMove,
                  onPointerUp: pointerManager.onPointerUp,
                  onPointerHover: pointerManager.onPointerHover,
                  onPointerSignal: (pointerSignal) {
                    if (pointerSignal is PointerScrollEvent) {
                      //adds scrolling down for images, cause otherwise photoView on PC not as useful
                      photoViewController.position -= pointerSignal.scrollDelta;
                    }
                  }),
              onTap: () => Navigator.pop(context),
              behavior: HitTestBehavior.translucent,
            );
          } else {
            return Container(
                width: 200,
                height: 200,
                margin: EdgeInsets.fromLTRB(100, 100, 100, 100),
                child: GestureDetector(
                  child: CircularProgressIndicator(
                    backgroundColor: Colors.blue,
                  ),
                  onHorizontalDragEnd: (dragVelocity) =>
                      manageSwipes(dragVelocity.velocity.pixelsPerSecond),
                  onTap: () => Navigator.pop(context),
                ));
          }
        });
  }
}

class ImageDisplayData {
  final ImageProvider image;
  final Alignment alignment;
  final dynamic initialScale;
  final bool showButtons;

  ImageDisplayData(
      {this.image, this.alignment, this.initialScale, this.showButtons});
}

Future<ImageDisplayData> fetchImageDisplayData(ImageData imageData) async {
  Image image =
      Image.network(backend.baseUrl + "/f/" + imageData.url); //get Image
  Alignment imageAlignment;
  PhotoViewComputedScale imageScale;
  bool showButtons;

  //get Image ratio to decide how to display
  final Completer<ImageInfo> completer = Completer<ImageInfo>();
  image.image
      .resolve(new ImageConfiguration())
      .addListener(ImageStreamListener((ImageInfo info, bool _) async {
    try {
      completer.complete(info);
    } catch (e) {
      return info;
    }
  }));

  ImageInfo info = await completer.future;
  if (info.image.height / info.image.width > 3.0) {
    //print(info.image.height / info.image.width);
    imageAlignment = Alignment.topCenter;
    //imageScale = PhotoViewComputedScale.contained *
    //    (info.image.height / info.image.width).toDouble();
    imageScale = PhotoViewComputedScale.covered;
    showButtons = false;
  } else {
    imageAlignment = Alignment.center;
    imageScale = PhotoViewComputedScale.contained;
    showButtons = true;
  }
  return ImageDisplayData(
      image: image.image,
      alignment: imageAlignment,
      initialScale: imageScale,
      showButtons: showButtons);
}

class ImagePointerManager {
  final PointerManagerRightThresholdReached showRightImage;
  final PointerManagerLeftThresholdReached showLeftImage;
  final PointerManagerDownThresholdReached showPanorama;
  final PointerManagerUpThresholdReached showDescription;
  final double threshold;
  List<Offset> lastVelocities = [];
  ImagePointerManager(
      {this.showLeftImage,
      this.showRightImage,
      this.showPanorama,
      this.showDescription,
      this.threshold = 1.5});
  void onPointerMove(PointerMoveEvent pointerMoveEvent) {
    Offset velocity = pointerMoveEvent.localDelta;
    if (lastVelocities.length > 10) {
      lastVelocities.removeAt(0);
    }
    lastVelocities.add(velocity);
  }

  void onPointerUp(PointerUpEvent pointerUpEvent) {
    checkIfThresholdReached();
  }

  void onPointerHover(PointerHoverEvent pointerCancelEvent) {
    checkIfThresholdReached();
  }

  void checkIfThresholdReached() {
    if (lastVelocities.isEmpty) {
      return;
    }
    final Offset lastVelocityAverage = getLastVelocityAverage();

    if (lastVelocityAverage.dx.abs() > lastVelocityAverage.dy.abs()) {
      //if horzontalswipe check horizontal threshold
      if (lastVelocityAverage.dx < -threshold &&
          lastVelocities.last.dx < -threshold / 2) {
        //check avg and last value extra (if user stopped swipe last sec dont count as swipe)
        showRightImage();
      } else if (lastVelocityAverage.dx > threshold &&
          lastVelocities.last.dx > threshold / 2) {
        showLeftImage();
      }
    } else {
      //if vertical swipe check that
      if (lastVelocityAverage.dy > threshold &&
          lastVelocities.last.dy > threshold / 2) {
        //downswipe
        showPanorama();
      } else if (lastVelocityAverage.dy < -threshold &&
          lastVelocities.last.dy < -threshold / 2) {
        showDescription();
      }
    }
    //print(lastVelocityAverage);
    lastVelocities = [];
  }

  Offset getLastVelocityAverage() {
    Offset velocities = Offset(0, 0);
    lastVelocities.forEach((element) {
      velocities += element;
    });
    return velocities.scale(
        1 / lastVelocities.length, 1 / lastVelocities.length);
  }
}

typedef PointerManagerDownThresholdReached = Function();
typedef PointerManagerLeftThresholdReached = Function();
typedef PointerManagerRightThresholdReached = Function();
typedef PointerManagerUpThresholdReached = Function();
