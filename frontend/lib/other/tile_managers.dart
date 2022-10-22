import 'package:flutter/material.dart';
import 'backend_connect.dart' as backend;
import 'package:image_server/widgets/imageDisplay/image_popup.dart';
import 'tile_data.dart';
import 'tile.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

/// TileManagers use inheritance and 'manage' the tiles in the TiledGridView
/// this includes fetching Data and adding the tiles/changing them
class TileManager {
  final Function(List<String>) changeTileManager;
  List<dynamic> tileData =
      []; //stores all tile data, gets it before onTileClicked in TiledGridView

  void setTileData(List<dynamic> tileData) {
    this.tileData = tileData;
  }

  void addTileData(List<dynamic> tileData) {
    this.tileData.addAll(tileData);
  }

  TileManager({this.changeTileManager});
  convertToTileData(json) {
    return TileData.fromJson(json);
  }

  fetchTileList(TileFetchData tileFetchData) async {}
  onTileClicked(BuildContext context, int index, TileFetchData tileFetchData) {}

  Widget tileText(dynamic tileData) {
    return Text(tileData.id.toString());
  }
}

class ImageManager extends TileManager {
  final Function(List<String>) changeTileManager;
  ImageManager({this.changeTileManager});
  convertToTileData(json) {
    return ImageData.fromJson(json);
  }

  fetchTileList(TileFetchData tileFetchData) async {
    String sortMode = "?sort_mode=";
    switch (tileFetchData.sortMode) {
      case 0:
        {
          sortMode += "DATE";
        }
        break;
      case 1:
        {
          sortMode += "MOST_RECENT";
        }
        break;
      case 2:
        {
          sortMode += "POSITION";
        }
        break;
      case 3:
        {
          sortMode += "RANDOM";
        }
        break;

      default:
        {
          sortMode += "DATE";
        }
        break;
    }

    String url = '/imagelist/' +
        tileFetchData.fetchLimit.toString() +
        "/" +
        tileFetchData.offset.toString() +
        sortMode;
    if (tileFetchData.tags != null &&
        tileFetchData.tags.length > 0 &&
        tileFetchData.tags.first != "") {
      url += "&tag=" + tileFetchData.tags.first;
    }
    var response = await backend.get(url);
    return response;
  }

  onTileClicked(
    BuildContext context,
    int index,
    TileFetchData tileFetchData,
  ) async {
    if (index >= tileData.length - 1) {
      tileFetchData = TileFetchData(
          tileFetchData.offset + tileFetchData.fetchLimit,
          tileFetchData.fetchLimit,
          tileFetchData.sortMode,
          tileFetchData.tags);
      final http.Response response = await fetchTileList(tileFetchData);
      if (response.statusCode != 404) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        final tileDataJson = data["data"];
        await tileDataJson.forEach((key, value) {
          tileData.add(convertToTileData(value));
        });
      }
    }

    showDialog(
        context: context,
        builder: (_) {
          try {
            if (index + 1 < tileData.length)
              fetchImageDisplayData(tileData[index + 1]);
          } catch (e) {
            print(e);
          } //new way of preloading cause otherwise aspect not in
          if (index >= 0 && index <= tileData.length - 1) {
            return ImagePopup(
              imageData: tileData[index],
              showLeftImage: () {
                Navigator.pop(context);
                onTileClicked(
                  context,
                  index - 1,
                  tileFetchData,
                );
              },
              showRightImage: () {
                //print(imageData.length);
                Navigator.pop(context);
                onTileClicked(
                  context,
                  index + 1,
                  tileFetchData,
                );
              },
            );
          } else {
            return Container();
          }
        });
  }

  Widget tileText(dynamic tileData) {
    return Text(tileData.title);
  }
}

class TagTileManager extends TileManager {
  final Function(List<String>) changeTileManager;
  TagTileManager({this.changeTileManager});
  convertToTileData(json) {
    return TagData.fromJson(json);
  }

  fetchTileList(TileFetchData tileFetchData) async {
    String sortMode = "?sort_mode=";
    switch (tileFetchData.sortMode) {
      case 0:
        {
          sortMode += "DATE";
        }
        break;
      case 1:
        {
          sortMode += "MOST_RECENT";
        }
        break;
      case 2:
        {
          sortMode += "POSITION";
        }
        break;
      case 3:
        {
          sortMode += "RANDOM";
        }
        break;
      case 4:
        {
          sortMode += "POPULARITY";
        }
        break;
      default:
        {
          sortMode += "DATE";
        }
        break;
    }

    String url = '/taglist/' +
        tileFetchData.fetchLimit.toString() +
        "/" +
        tileFetchData.offset.toString() +
        sortMode;
    tileFetchData.tags != null ? url += "&tag=" + tileFetchData.tags.first : "";
    var response = await backend.get(url);
    return response;
  }

  @override
  onTileClicked(
    BuildContext context,
    int index,
    TileFetchData tileFetchData,
  ) {
    //print(allTileData[index].name);
    changeTileManager([tileData[index].name]);
  }

  Widget tileText(dynamic tileData) {
    return Stack(children: [
      Text(
        tileData.name,
        style: TextStyle(
          fontSize: 20,
          foreground: Paint()
            ..style = PaintingStyle.stroke
            ..strokeWidth = 3
            ..color = Colors.black.withOpacity(0.5),
        ),
        textAlign: TextAlign.center,
      ),
      Text(
        tileData.name,
        style: TextStyle(color: Colors.orange[50], fontSize: 20),
        textAlign: TextAlign.center,
      )
    ]);
  }
}
