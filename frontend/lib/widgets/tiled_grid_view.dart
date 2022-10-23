import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:flutter/rendering.dart';
import 'package:image_server/other/tile_data.dart';
import 'package:image_server/other/tile_managers.dart';
import 'package:image_server/other/tile.dart';
import 'package:image_server/pages/image_viewer.dart';
import 'package:http/http.dart' as http;

class TileGridViewController {
  /// Changes tileData according to selected Images and selectMode
  /// DragNDrop not part because handled right after select
  void Function(SelectMode prevSelectMode) changeTileListAfterEdit;
}

class TileGridView extends StatefulWidget {
  const TileGridView(
      {Key key,
      this.tileManager,
      this.sortMode = 0, //basic Stuff
      this.thumbnailSize = 200,
      this.selectMode = SelectMode.none,
      this.selectColor = Colors.red, //delete Stuff
      this.changetoSelectImages,
      this.hideTagSearch,
      this.tags,
      this.tileController}) //tag Stuff
      : super(key: key);

  final TileManager tileManager;
  final int sortMode;
  final double thumbnailSize;
  final SelectMode selectMode;
  final Color selectColor;
  final Function(String) changetoSelectImages;
  final Function() hideTagSearch;
  final List<String> tags;

  final TileGridViewController tileController;

  final double tileSpacing = 10;

  @override
  _TileGridViewState createState() => _TileGridViewState(tileController);
}

class _TileGridViewState<T extends TileGridView> extends State<T> {
  _TileGridViewState(TileGridViewController _tileController) {
    _tileController.changeTileListAfterEdit = changeTileListAfterEdit;
  }
  ScrollController _controller;
  int offset = 0;
  int fetchLimit;
  List<TileData> tileData = [];

  List<int> toSelectImages = []; //delete Stuff

  //tag Stuff
  bool tagSearchHidden = false;
  double lastScrollPos = 0;
  double scrollLimit = 0;

  makeTileList() async {
    //this function gets called every time a certain limit has been
    //reached when scrolling and fetches the new imagelist
    offset += fetchLimit;
    try {
      final http.Response response =
          await widget.tileManager.fetchTileList(getTileFetchData());
      if (response.statusCode != 404) {
        final data = json.decode(utf8.decode(response.bodyBytes));
        //print(data);
        final tileDataJson = data["data"];

        tileDataJson.forEach((key, value) {
          tileData.add(widget.tileManager.convertToTileData(value));
        });

        //print(_controller.position.maxScrollExtent);
        setState(() {
          tileData = tileData;
        });
      }
    } catch (e) {
      print(e);
      return;
    }
  }

  _scrollListener() {
    if (!tagSearchHidden &&
        _controller.position.userScrollDirection == ScrollDirection.reverse) {
      if (scrollLimit >= 50) {
        tagSearchHidden = !tagSearchHidden;
        widget.hideTagSearch();
        try {
          _controller.position.setPixels(_controller.position.pixels - 100);
        } //100==appbar height and tagsearchbar height, also don't use jumpTo cause that causes scroll to be stopped
        catch (e) {
          //ths is just an error when scrolling with mouse wheel, doesn't rly do much harm
        }
      } else {
        scrollLimit += _controller.offset - lastScrollPos;
      }
    } else if (tagSearchHidden &&
        _controller.position.userScrollDirection == ScrollDirection.forward) {
      if (scrollLimit >= 50) {
        tagSearchHidden = !tagSearchHidden;
        widget.hideTagSearch();
        try {
          _controller.position.setPixels(_controller.position.pixels + 100);
        } //100==appbar height and tagsearchbar height, also don't use jumpTo cause that causes scroll to be stopped

        catch (e) {
          //ths is just an error when scrolling with mouse wheel, doesn't rly do much harm
        }
      } else {
        scrollLimit += lastScrollPos - _controller.offset;
      }
    } else {
      scrollLimit = 0;
    }

    if (_controller.offset >= _controller.position.maxScrollExtent - 500 &&
        !_controller.position.outOfRange) {
      if (tileData.length >= offset) {
        //cause otherwise offset gets messed up
        makeTileList();
      }
    }
    lastScrollPos = _controller.offset;
  }

  TileFetchData getTileFetchData() {
    return TileFetchData(offset, fetchLimit, widget.sortMode, widget.tags);
  }

  @override
  void initState() {
    _controller = ScrollController();

    _controller.addListener(() => _scrollListener());

    fetchLimit = (10000 ~/ widget.thumbnailSize);
    offset -=
        fetchLimit; //cause offset+= gets called and otherwise first images not shown
    makeTileList();
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    onTileClicked(int index) {
      widget.tileManager.setTileData(tileData);
      widget.tileManager.onTileClicked(context, index, getTileFetchData());
    }

    ;

    selectModeHandler(int index) {
      if (!toSelectImages.contains(index)) {
        toSelectImages.add(index);
        setState(() {
          tileData[index].overlay = widget.selectColor.withOpacity(0.5);
        });
      } else {
        toSelectImages.remove(index);
        setState(() {
          tileData[index].overlay = Colors.transparent;
        });
      }

      widget.changetoSelectImages(
          tileData[index].id); //actually pass through data to upload

      //extra code for swapping images/dragNDrop
      if (widget.selectMode == SelectMode.swap && toSelectImages.length >= 2) {
        //make the ewww green go away
        setState(() {
          tileData[toSelectImages[0]].overlay = Colors.transparent;
          tileData[toSelectImages[1]].overlay =
              Colors.transparent; //couldve made with loop but damn its 2 items
        });

        //store tile cause easiest way to reorder is to just delete item and insert it at pos
        var storedTileData = tileData[toSelectImages[0]];
        tileData.removeAt(toSelectImages[0]);
        toSelectImages[0] > toSelectImages[1]
            ? //if image behind
            tileData.insert(toSelectImages[1], storedTileData)
            : tileData.insert(toSelectImages[1] - 1,
                storedTileData); //moves image new position locally so not have to reload everything

        toSelectImages =
            []; //rest to nothing cause we always only work with 2 m8

      }
    }

    handleClick(int index) {
      if (widget.selectMode != SelectMode.none) {
        selectModeHandler(index);
      } else {
        onTileClicked(index);
      }
    }

    return GridView.builder(
        controller: _controller,
        gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
            maxCrossAxisExtent: widget.thumbnailSize,
            childAspectRatio: 2 / 2,
            crossAxisSpacing: widget.tileSpacing,
            mainAxisSpacing: widget.tileSpacing),
        itemBuilder: (BuildContext ctx, index) {
          return Tile(
            tileData: tileData[index],
            tileManager: widget.tileManager,
            thumbnailSize: 200,
            onTileClicked: () => handleClick(index),
          );
        },
        itemCount: tileData.length);
  }

  /// Changes tileData according to selected Images and selectMode
  /// DragNDrop not part because handled right after select
  void changeTileListAfterEdit(SelectMode prevSelectMode) {
    //used to make changes after trash or image add button press locally, instead of updating it with server again
    if (prevSelectMode == SelectMode.delete ||
        prevSelectMode == SelectMode.swap) {
      toSelectImages
          .sort((a, b) => b.compareTo(a)); //sorts list in reverse manner
      //without sorting in reverse it for deleting images at pos 3 and 4 it will delete the 3rd image first move the 4th to the 3rd spot
      //and cause graphical errors(deletes wrong image in view)
      toSelectImages.forEach((tileId) {
        tileData.removeAt(tileId);
      });
    } else if (prevSelectMode == SelectMode.tag) {
      toSelectImages.forEach((tileId) {
        tileData[tileId].overlay = Colors.transparent;
      });
    }
    toSelectImages = [];
  }
}
