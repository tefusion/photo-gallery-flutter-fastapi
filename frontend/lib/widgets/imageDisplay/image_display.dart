import 'package:flutter/material.dart';
import 'package:image_server/other/tile_data.dart';
import 'package:image_server/other/backend_connect.dart' as backend;
//for determining height
import 'dart:async';

/// ImageTiles are used in TiledGridView as the tiles and contain the thumbnails
/// overlay color is changeable using imageData.overlay
/// onClick ImagePopup gets called as a Popup
class ImageTile extends StatelessWidget {
  final ImageData imageData;
  final double thumbnailSize;
  final Function showImagePopup;

  Future<ImageProvider<Object>> fetchThumbnail() async {
    return Image.network(backend.baseUrl + "/t/" + imageData.url).image;
  }

  const ImageTile({
    Key key,
    this.imageData,
    this.thumbnailSize,
    this.showImagePopup(),
  }) : super(key: key);
  @override
  Widget build(BuildContext context) {
    return FutureBuilder<ImageProvider<Object>>(
        future: fetchThumbnail(),
        builder: (context, AsyncSnapshot<ImageProvider<Object>> snapshot) {
          if (snapshot.hasData) {
            return GestureDetector(
                child: Container(
                  width: thumbnailSize,
                  height: thumbnailSize,
                  decoration: BoxDecoration(
                    image: DecorationImage(
                        image: snapshot.data,
                        fit: BoxFit.cover,
                        colorFilter: ColorFilter.mode(
                            imageData.overlay, BlendMode.multiply)),
                  ),
                ),
                onTap: () => showImagePopup());
          } else {
            return Container(
                width: thumbnailSize,
                height: thumbnailSize,
                margin: EdgeInsets.all(100),
                child: CircularProgressIndicator(
                  backgroundColor: Colors.red,
                ));
          }
        });
  }
}
