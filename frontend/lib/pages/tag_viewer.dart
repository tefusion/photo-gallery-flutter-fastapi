import 'package:flutter/material.dart';
import 'package:image_server/other/tile_managers.dart';
import 'package:image_server/other/backend_connect.dart' as backend;
import 'package:image_server/widgets/tiled_grid_view.dart';
import 'package:image_server/widgets/small/tag_search_bar_minimized.dart';

import 'image_viewer.dart';

///Page Class for imageTiles display
///uses 'package:image_server/widgets/TiledGridView.dart' for tile display and
///'package:image_server/widgets/small/tagSearchBar.dart' as a search bar with additional buttons

class TagViewer extends StatefulWidget {
  const TagViewer({Key key}) : super(key: key);

  @override
  _TagViewerState createState() => _TagViewerState();
}

class _TagViewerState extends State<TagViewer> {
  int sortMode = 4;
  int storedTagSortMode = 4;
  Key key = UniqueKey();
  Key updateTagSearchBarKey = UniqueKey();
  bool tagSearchVisible = true;
  List<String> tags;
  ManagerIndex currentManagerId = ManagerIndex.tag;

  final TileGridViewController _tileGridViewController =
      TileGridViewController();

  //overwrites _onWillPop() so that it pops back to tagDisplay
  Future<bool> _onWillPop() async {
    if (currentManagerId == ManagerIndex.image) {
      key = UniqueKey();
      setState(() {
        currentManagerId = ManagerIndex.tag;
        tagSearchVisible = true;
        sortMode = storedTagSortMode; //get previous sortMode back

        //so that tag search bar empty again
        tags = null;
        updateTagSearchBarKey = UniqueKey();
      });
      return false;
    } else {
      return true;
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
                    onSortModeChanged: (int sortModeId) {
                      if (sortModeId == 3) {
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
                      child: Padding(
                          padding: EdgeInsets.symmetric(horizontal: 15))),
                ],
                toolbarHeight: 50)
            : null,
        body: new Column(children: [
          TagSearchBarMini(
            visible: tagSearchVisible,
            searchByTag: (String tag) {
              Navigator.push(
                  context,
                  MaterialPageRoute(
                      builder: (context) => ImageViewer(tags: [tag])));
            },
            showTagsStartingWith: (String pattern) {
              key = UniqueKey();
              setState(() {
                tags = [pattern];
              });
            },
          ),
          Expanded(
            child: SizedBox(
              child: new TileGridView(
                sortMode: sortMode,
                key: key,
                thumbnailSize: 200,
                changetoSelectImages: (id) {},
                hideTagSearch: () {
                  setState(() {
                    tagSearchVisible = !tagSearchVisible; //(un)hide searchBar
                  });
                },
                tags: tags,
                tileManager: TagTileManager(changeTileManager: (newTags) {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => ImageViewer(
                                tags: newTags,
                              )));
                }),
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
  final Function(int) onSortModeChanged;
  final int
      sortMode; //has to be like this and not in stateful widget here to change to POS upon tagsearch, could change to stateless widgets

  SortModeButton({this.onSortModeChanged, this.sortMode});

  @override
  _SortModeButtonState createState() => _SortModeButtonState();
}

class _SortModeButtonState extends State<SortModeButton> {
  @override
  Widget build(BuildContext context) {
    return DropdownButton<int>(
        value: widget.sortMode,
        icon: const Icon(Icons.arrow_downward),
        iconSize: 24,
        elevation: 16,
        style: const TextStyle(color: Colors.deepPurple),
        underline: Container(
          height: 2,
          color: Colors.deepPurpleAccent,
        ),
        onChanged: (int newValue) {
          widget.onSortModeChanged(newValue);
        },
        items: [
          DropdownMenuItem<int>(
            value: 0,
            child: Text("By date"),
          ),
          DropdownMenuItem<int>(
            value: 1,
            child: Text("Most recent"),
          ),
          DropdownMenuItem<int>(
            value: 2,
            child: Text("Position"),
          ),
          DropdownMenuItem<int>(
            value: 3,
            child: Text("Random"),
          ),
          DropdownMenuItem<int>(
            value: 4,
            child: Text("Popularity"),
          ),
        ]);
  }
}

/*
<String>['Most recent', "By date"].map<DropdownMenuItem<String>>((String value){
        return DropdownMenuItem<String>(value: value, child: Text(value),);

      }).toList()
*/

enum ManagerIndex { tag, image }
