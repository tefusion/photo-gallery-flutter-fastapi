import 'package:flutter/material.dart';
import 'tile_data.dart';
import 'tile_managers.dart';
import 'backend_connect.dart' as backend;

class TileFetchData {
  final int offset;
  final int fetchLimit;
  final int sortMode;
  final List<String> tags;
  TileFetchData(this.offset, this.fetchLimit, this.sortMode, this.tags);
}

class Tile extends StatelessWidget {
  final TileData tileData;
  final TileManager tileManager;
  final double thumbnailSize;
  final Function onTileClicked;

  Future<ImageProvider<Object>> fetchThumbnail() async {
    return Image.network(backend.baseUrl + "/t/" + tileData.url).image;
  }

  const Tile(
      {Key key,
      this.tileData,
      this.tileManager,
      this.thumbnailSize,
      this.onTileClicked})
      : super(key: key);
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
                              tileData.overlay, BlendMode.multiply)),
                    ),
                    child: Align(
                      child: tileManager.tileText(tileData),
                      alignment: Alignment.bottomCenter,
                    )),
                onTap: () => onTileClicked());
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
