import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:image_server/other/tile_managers.dart';
import 'package:image_server/other/backend_connect.dart' as backend;
import 'package:image_server/widgets/tiled_grid_view.dart';
import 'package:image_server/widgets/small/tag_search_bar.dart';

///Page Class for imageTiles display
///uses 'package:image_server/widgets/TiledGridView.dart' for tile display and
///'package:image_server/widgets/small/tagSearchBar.dart' as a search bar with additional buttons

class ImageViewer extends StatefulWidget {
  const ImageViewer({Key key, this.tags}) : super(key: key);
  final List<String> tags;

  @override
  _ImageViewerState createState() => _ImageViewerState();
}

class _ImageViewerState extends State<ImageViewer> {
  @override
  void initState() {
    tags = widget.tags;
    super.initState();
  }

  SortModeImages sortMode = SortModeImages.position;
  Key key = UniqueKey();
  Key updateTagSearchBarKey = UniqueKey();
  bool selectModeOn = false;
  SelectMode selectMode = SelectMode.none;
  bool tagSearchVisible = true;
  Color selectColor = Colors.red;
  List<int> toDeleteImages =
      []; //couldve made in one variable, but just in case so I don't delete stuff by tagging it im gonna make it obviously different
  List<int> toTagImages = [];
  List<String> tags;

  final TileGridViewController _tileGridViewController =
      TileGridViewController();
//reorder stuff
  List<int> toSwapImages = []; //used for both swapping and dragNDrop images
  //delete Functions

  ///updates List of images that will be deleted upon another click of trash can button
  changeToDeleteImages(int id) {
    if (toDeleteImages.contains(id)) {
      toDeleteImages.remove(id);
    } else {
      toDeleteImages.add(id);
    }
  }

  ///called after click of IconButton with icon delete_sharp -> requests server to delete images one by one
  deleteImagesFromServer(List<int> toDeleteImages) {
    toDeleteImages.forEach((imageId) {
      backend.delete("/image/" + imageId.toString());
    });
  }

  //Tag stuff
  ///updates List of images that will be tagged with current value of tagSearch upon additional click on camera icon button
  changeToTagImages(int id) {
    if (toTagImages.contains(id)) {
      toTagImages.remove(id);
    } else {
      toTagImages.add(id);
    }
  }

  ///requests server to tag images within toTagImages with tag from searchBar
  tagImagesOnServer(List<int> toTagImages, String tag) async {
    FormData tagData =
        new FormData.fromMap({"tag": tag, "images": toTagImages});
    try {
      var response = await backend.post(tagData, '/tag/');
    } catch (e) {
      print("Failed to tag images on Server");
    }
  }

  ///requests server to untag images within to(Un)TagImages with tag from searchBar
  ///if tag from search bar is same with current tag search value
  untagImagesOnServer(List<int> toTagImages, String tag) async {
    FormData tagData =
        new FormData.fromMap({"tag": tag, "images": toTagImages});
    try {
      await backend.post(tagData, '/untag/');
    } catch (e) {
      print("Failed to untag images on Server");
    }
  }

  //reorderStuff
  ///updates List from selection in TiledGridView
  changeToSwapImages(int id) {
    if (toSwapImages.contains(id)) {
      toSwapImages.remove(id);
    } else {
      toSwapImages.add(id);
    }
    if (toSwapImages.length >= 2) {
      //code for requesting database to reorder
      backend.put("/reorder/" +
          tags[0] +
          "/" +
          (toSwapImages[0]).toString() +
          "?idDestination=" +
          toSwapImages[1].toString() +
          "&mode=1"); //maybe add more modes mode 1 currently just dragNDrop
      setState(() {
        selectMode = SelectMode.none;
      });
      toSwapImages = [];
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        backgroundColor: Colors.black38,
        appBar: tagSearchVisible
            ? AppBar(

                ///has a bunch of expanded Paddings to display in we
                title: Text("Image Viewer"),
                backgroundColor: Colors.orange,
                actions: [
                  Padding(
                      padding: EdgeInsets.symmetric(
                          horizontal:
                              10)), //extra padding to ensure that back button not overlayed
                  Expanded(
                      flex:
                          10, //high flex so tht appbar buttons move to right and only slightly get more spacing
                      child: Padding(
                          padding: EdgeInsets.symmetric(horizontal: 50))),
                  SortModeButton(
                    onSortModeChanged: (SortModeImages sortModeId) {
                      if (sortModeId == SortModeImages.random) {
                        backend.get("/randomize");
                      }
                      key = UniqueKey();
                      setState(() {
                        this.sortMode = sortModeId;
                      });
                    },
                    sortMode: this.sortMode,
                  ),
                  Expanded(
                      child: Padding(
                          padding: EdgeInsets.symmetric(horizontal: 10))),
                  TextButton.icon(
                    onPressed: () => Navigator.pushNamed(context, '/upload'),
                    icon: Icon(Icons.upload_file),
                    label: Text("Upload"),
                  ),
                  Expanded(
                      child: Padding(
                          padding: EdgeInsets.symmetric(horizontal: 10))),
                  Expanded(
                      child: IconButton(
                          icon: Icon(Icons.delete_sharp),
                          onPressed: () {
                            if (selectMode == SelectMode.delete) {
                              deleteImagesFromServer(toDeleteImages);
                              _tileGridViewController
                                  .changeTileListAfterEdit(selectMode);
                              setState(() {
                                selectMode = SelectMode.none;
                              });
                            } else if (selectMode == SelectMode.none) {
                              setState(() {
                                selectMode = SelectMode.delete;
                                selectColor = Colors.red;
                              });
                            }
                          })),
                  Expanded(
                      child: Padding(
                          padding: EdgeInsets.symmetric(horizontal: 15))),
                ],
                toolbarHeight: 50)
            : null,
        body: new Column(children: [
          TagSearchBar(
              key: updateTagSearchBarKey,
              initialValue: tags == null ? "" : tags.first,
              reorderButtonsShown: tags == null ? false : true,
              visible: tagSearchVisible,
              searchByTag: (tag) {
                key = UniqueKey();
                setState(() {
                  if (tag != "") {
                    this.sortMode = SortModeImages.position;
                    tags = [tag];
                    updateTagSearchBarKey = UniqueKey();
                  } else {
                    tags = null;
                  }
                });
              },
              addToTag: (tag) {
                if (selectMode == SelectMode.none) {
                  setState(() {
                    selectColor = Colors.blue;
                    selectMode = SelectMode.tag;
                  });
                } else if (selectMode == SelectMode.tag) {
                  if (tag != tags[0]) {
                    tagImagesOnServer(toTagImages, tag);
                    _tileGridViewController
                        .changeTileListAfterEdit(SelectMode.tag);
                  } else {
                    //if tag in search bar same actually remove from tag (cause otherwise button would make no sense
                    untagImagesOnServer(toTagImages, tag);
                    _tileGridViewController
                        .changeTileListAfterEdit(SelectMode.delete);
                  }

                  toTagImages = [];

                  setState(() {
                    selectMode = SelectMode.none;
                  });
                }
              },
              reorderWithinTag: (reorderMode) {
                if (reorderMode == ReorderMode.dragNdrop) {
                  setState(() {
                    selectColor = Colors.green[300];
                    selectMode = SelectMode.swap;
                  });
                }
              }),
          Expanded(
            child: SizedBox(
              child: new TileGridView(
                sortMode: sortMode.index,
                key: key,
                thumbnailSize: 200,
                selectMode: selectMode,
                selectColor: selectColor,
                changetoSelectImages: (id) {
                  switch (selectMode) {
                    case SelectMode.delete:
                      changeToDeleteImages(id);
                      break;
                    case SelectMode.tag:
                      changeToTagImages(id);
                      break;
                    case SelectMode.swap:
                      changeToSwapImages(id);
                      break;
                    case SelectMode.none:
                      break;
                  }
                }, //couldve done with same functions but I like safety
                hideTagSearch: () {
                  setState(() {
                    tagSearchVisible = !tagSearchVisible; //(un)hide searchBar
                  });
                },
                tags: tags,
                tileManager: ImageManager(changeTileManager: (newTags) {}),
                tileController: _tileGridViewController,
              ),
              height: 400,
            ),
            flex: 10,
          )
        ]));
  }
}

///Button that changes current SortMode of images / tags
class SortModeButton extends StatefulWidget {
  final Function(SortModeImages) onSortModeChanged;
  final SortModeImages
      sortMode; //has to be like this and not in stateful widget here to change to POS upon tagsearch, could change to stateless widgets

  SortModeButton({this.onSortModeChanged, this.sortMode});

  @override
  _SortModeButtonState createState() => _SortModeButtonState();
}

class _SortModeButtonState extends State<SortModeButton> {
  @override
  Widget build(BuildContext context) {
    return DropdownButton<SortModeImages>(
        value: widget.sortMode,
        icon: const Icon(Icons.arrow_downward),
        iconSize: 24,
        elevation: 16,
        style: const TextStyle(color: Colors.deepPurple),
        underline: Container(
          height: 2,
          color: Colors.deepPurpleAccent,
        ),
        onChanged: (SortModeImages newValue) {
          widget.onSortModeChanged(newValue);
        },
        items: [
          DropdownMenuItem<SortModeImages>(
            value: SortModeImages.date,
            child: Text("By date"),
          ),
          DropdownMenuItem<SortModeImages>(
            value: SortModeImages.dateReverse,
            child: Text("Most recent"),
          ),
          DropdownMenuItem<SortModeImages>(
            value: SortModeImages.position,
            child: Text("Position"),
          ),
          DropdownMenuItem<SortModeImages>(
            value: SortModeImages.random,
            child: Text("Random"),
          )
        ]);
  }
}

enum SelectMode { none, delete, tag, swap }

enum SortModeImages { date, dateReverse, position, random }

enum ManagerIndex { tag, image }
