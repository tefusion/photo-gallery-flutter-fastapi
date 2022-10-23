import 'package:flutter/material.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:image_server/other/backend_connect.dart' as backend;
import 'dart:convert';

class TagSearchBar extends StatefulWidget {
  const TagSearchBar(
      {Key key,
      this.initialValue,
      this.visible,
      this.searchByTag,
      this.addToTag,
      this.reorderButtonsShown = false,
      this.reorderWithinTag})
      : super(key: key);

  final String initialValue;
  final Function(String) searchByTag;
  final Function(String) addToTag;
  final Function(ReorderMode) reorderWithinTag;
  final bool visible;
  final bool reorderButtonsShown;

  @override
  _TagSearchBarState createState() => _TagSearchBarState();
}

class _TagSearchBarState extends State<TagSearchBar> {
  bool addingToTag = false;
  String prevTag = "";
  TextEditingController tagEditingController =
      TextEditingController(); //only exists for setting init value
  bool initValueSet =
      false; //has to be called in build, since when calling in init everything breaks (cause rebuilds widget again and thats bad says the compiler)
  IconData tagButtonIcon = Icons.add_a_photo;
  List<dynamic>
      tagSuggestions; //store tagSuggestions so when submitting uses first suggestion

  //for autocompletion later
  Future<List<dynamic>> handleTextInput(String pattern) async {
    //get suggestions returns list of Strings that complete tagInput
    if (prevTag == pattern) {
      setState(() {
        tagButtonIcon = Icons.remove_from_queue;
      });
    } else {
      setState(() {
        tagButtonIcon = Icons.add_a_photo;
      });
    }
    var response = await backend.get("/autocomplete?tag_start=" + pattern);
    var data = json.decode(utf8.decode(response.bodyBytes));
    return data["tags"];
  }

  @override
  void initState() {
    prevTag = widget.initialValue;
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    if (!initValueSet) {
      tagEditingController.text = widget.initialValue;
      handleTextInput(widget.initialValue); //was prev called with listener
      //but now called in suggestionsCallback
      //(has to be called here cause otherwise button display wrong)
      initValueSet = true;
    }

    return Visibility(
      child: SizedBox(
        child: DecoratedBox(
          child: Row(children: [
            Expanded(
                child: SizedBox(
              child: TypeAheadField(
                //getImmediateSuggestions: true,
                textFieldConfiguration: TextFieldConfiguration(
                    autocorrect: false,
                    autofocus: false,
                    enabled: !addingToTag,
                    decoration: InputDecoration(
                      labelText: 'Tag Search',
                      hintText: "Enter tag",
                    ),
                    controller: tagEditingController,
                    onSubmitted: (submitTagValue) {
                      if (tagSuggestions != null && tagSuggestions.length > 0) {
                        //only search when user actually typed sth in
                        widget.searchByTag(tagSuggestions[0]);
                        setState(() {
                          tagEditingController.text = tagSuggestions[0];
                        });
                      }
                    }),
                suggestionsCallback: (pattern) async {
                  tagSuggestions =
                      await handleTextInput(pattern); //store for submit use
                  return tagSuggestions;
                },
                itemBuilder: (context, tagSuggestion) {
                  return Card(
                    child: ListTile(
                      title: Text(tagSuggestion),
                    ),
                    color: Colors.orange[200],
                    shape: RoundedRectangleBorder(
                        borderRadius:
                            BorderRadius.all(Radius.elliptical(100, 100))),
                  );
                },
                onSuggestionSelected: (tagSuggestion) {
                  widget.searchByTag(tagSuggestion);
                  setState(() {
                    tagEditingController.text = tagSuggestion;
                  });
                },
                suggestionsBoxDecoration: SuggestionsBoxDecoration(
                  color: Colors.transparent,
                  shadowColor: Colors.black87,
                  shape: RoundedRectangleBorder(
                      borderRadius:
                          BorderRadius.all(Radius.elliptical(100, 100))),
                ),
                hideOnEmpty: true,
                hideOnLoading: true,
                hideOnError: true,
              ),
              width: 50,
            )),
            SizedBox(
              child: IconButton(
                icon: Icon(Icons.search),
                onPressed: () {
                  if (!addingToTag) {
                    prevTag = tagEditingController.text;
                    widget.searchByTag(tagEditingController.text);
                  }
                },
              ),
              width: 50,
            ),
            Padding(padding: EdgeInsets.symmetric(horizontal: 30)),
            SizedBox(
              child: IconButton(
                icon: Icon(tagButtonIcon),
                onPressed: () {
                  if (tagEditingController.text != "") {
                    widget.addToTag(tagEditingController.text);
                    setState(() {
                      addingToTag = !addingToTag;
                    });
                  }
                },
              ),
              width: 50,
            ),
            widget.reorderButtonsShown
                ? SizedBox(
                    child: IconButton(
                        icon: Icon(Icons.switch_account),
                        onPressed: () {
                          widget.reorderWithinTag(ReorderMode.dragNdrop);
                        }),
                    width: 50,
                  )
                : SizedBox.shrink(),
            Padding(padding: EdgeInsets.symmetric(horizontal: 10)),
          ]),
          decoration: BoxDecoration(color: Colors.orange),
        ),
        height: 50,
      ),
      visible: widget.visible,
    );
  }
}

enum ReorderMode { swap, dragNdrop }
