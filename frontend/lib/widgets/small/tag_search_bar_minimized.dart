import 'package:flutter/material.dart';

class TagSearchBarMini extends StatefulWidget {
  const TagSearchBarMini(
      {Key key, this.visible, this.searchByTag, this.showTagsStartingWith})
      : super(key: key);

  final Function(String) searchByTag;
  final Function(String) showTagsStartingWith;
  final bool visible;

  @override
  _TagSearchBarMiniState createState() => _TagSearchBarMiniState();
}

class _TagSearchBarMiniState extends State<TagSearchBarMini> {
  String prevTag = "";
  TextEditingController tagEditingController =
      TextEditingController(); //only exists for setting init value
  List<dynamic>
      tagSuggestions; //store tagSuggestions so when submitting uses first suggestion

  //for autocompletion later
  handleTextInput(String pattern) async {
    //get suggestions returns list of Strings that complete tagInput

    if (pattern != prevTag) {
      prevTag = pattern;
      widget.showTagsStartingWith(pattern);
    }
  }

  @override
  void initState() {
    tagEditingController.addListener(() {
      handleTextInput(tagEditingController.text);
    });
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Visibility(
      child: SizedBox(
          child: DecoratedBox(
              decoration: BoxDecoration(color: Colors.orange),
              child: Row(children: [
                Expanded(
                    child: SizedBox(
                  child: TextField(
                      controller: tagEditingController,
                      decoration: InputDecoration(
                        labelText: 'Tag Search',
                      )),
                  width: 50,
                )),
                SizedBox(
                  child: IconButton(
                    icon: Icon(Icons.search),
                    onPressed: () {
                      prevTag = tagEditingController.text;
                      widget.searchByTag(tagEditingController.text);
                    },
                  ),
                  width: 50,
                ),
                Padding(padding: EdgeInsets.symmetric(horizontal: 30))
              ]))),
      visible: widget.visible,
    );
  }
}

enum ReorderMode { swap, dragNdrop }
