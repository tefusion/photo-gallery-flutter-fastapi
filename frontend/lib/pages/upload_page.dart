import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_server/other/backend_connect.dart' as backend;
import 'package:dio/dio.dart';

//mobile or desktop check
import 'package:flutter/foundation.dart' show kIsWeb;

/// Just a page with an upload Button, should work on all Platforms
class UploadPage extends StatefulWidget {
  @override
  _UploadPageState createState() => _UploadPageState();
}

class _UploadPageState extends State<UploadPage> {
  TextEditingController _titleInput = TextEditingController();
  TextEditingController _descInput = TextEditingController();
  TextEditingController _tagInput = TextEditingController();

  String _title = " ";
  String _description = " ";
  String _tag = " ";
  Widget _image = Container();
  bool compressed = false;
  //Uint8List _fileBytes;

  Widget _submitStatus = Container();
  bool submittable = true;

  void updateTitleVariable() {
    _title = _titleInput.text;
  }

  void updateDescriptionVariable() {
    _description = _descInput.text;
  }

  void updateTagVariable() {
    _tag = _tagInput.text;
  }

  void pickFile() async {
    FilePickerResult result = await FilePicker.platform
        .pickFiles(allowMultiple: true, type: FileType.image);

    if (result != null) {
      setState(() {
        _submitStatus = LinearProgressIndicator();
      });
      submittable = false;

      final uploadFilesData = UploadFilesData(
          title: _title,
          description: _description,
          tag: _tag,
          compressed: compressed);
      if (kIsWeb) {
        //difference between Web version and other is that files have to be saved with bytes and not just the path
        uploadFilesWeb(uploadFilesData, result.files);
      } else {
        uploadFilesDevice(uploadFilesData, result.files);
      }

      //
      changeUIBack();
    }
  }

  changeUIBack() {
    submittable = true;

    setState(() {
      _submitStatus = Center(child: Text("Successfully submitted"));
      _titleInput.text = "";
      _descInput.text = "";
    });
    _title = " ";
    _description = " ";

    Future.delayed(const Duration(seconds: 1), () {
      try {
        if (mounted) {
          setState(() {
            _submitStatus = Container();
          });
        }
      } catch (e) {
        print(e);
      }
    });
  }

  @override
  void initState() {
    super.initState();
    _titleInput.addListener(() => updateTitleVariable());
    _descInput.addListener(() => updateDescriptionVariable());
    _tagInput.addListener(() => updateTagVariable());
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.blueGrey,
        title: Text("Upload Image"),
      ),
      body: Column(children: [
        Container(
            margin: EdgeInsets.fromLTRB(100, 10, 100, 10),
            child: TextField(
              decoration: InputDecoration(
                  border: UnderlineInputBorder(), labelText: 'Enter title'),
              controller: _titleInput,
            )),
        Container(
            margin: EdgeInsets.fromLTRB(100, 10, 100, 10),
            child: TextField(
              decoration: InputDecoration(
                  border: UnderlineInputBorder(),
                  labelText: 'Enter description'),
              controller: _descInput,
            )),
        Container(
            margin: EdgeInsets.fromLTRB(100, 10, 100, 10),
            child: TextField(
              decoration: InputDecoration(
                  border: UnderlineInputBorder(), labelText: 'Enter tag'),
              controller: _tagInput,
            )),
        FloatingActionButton.extended(
          onPressed: () async => pickFile(),
          label: Text("Upload File"),
          backgroundColor: Colors.grey,
          hoverColor: Colors.blueGrey,
          splashColor: Colors.blue[400],
          heroTag: "upload",
        ),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Text(
              "Compress Images",
              style: TextStyle(fontSize: 10),
            ),
            Switch(
                value: compressed,
                onChanged: (compressImages) {
                  setState(() {
                    compressed = compressImages;
                  });
                }),
          ],
        ),
        _submitStatus,
        Expanded(
            child: Container(
                margin: EdgeInsets.fromLTRB(10, 30, 10, 30), child: _image)),
      ]),
    );
  }
}

/// for Mobile/Desktop, generates MultipartsFiles for upload
uploadFilesDevice(UploadFilesData data, List<PlatformFile> filePaths) async {
  List<MultipartFile> toUploadFiles = [];
  for (PlatformFile file in filePaths) {
    toUploadFiles
        .add(await MultipartFile.fromFile(file.path, filename: file.name));
  }

  uploadFiles(data, toUploadFiles);
}

/// converts bytes to MultipartFiles for upload
uploadFilesWeb(UploadFilesData data, List<PlatformFile> files) async {
  List<MultipartFile> toUploadFiles = [];
  files.forEach((file) {
    toUploadFiles.add(MultipartFile.fromBytes(file.bytes, filename: file.name));
    //print(file.name);
  });
  uploadFiles(data, toUploadFiles);
}

/// unified method for uploading files, might need to convert to MultipartFile array first
uploadFiles(UploadFilesData data, List<MultipartFile> files) {
  FormData formData = new FormData.fromMap({
    //formdata from map ignores empty strings, so "" -> " "
    "title": data.title == "" ? " " : data.title,
    "description": data.description == "" ? " " : data.description,
    "files": files,
    "tag": data.tag == "" ? " " : data.tag,
    "compressed": data.compressed
  });
  backend.post(formData, '/images/');
}

class UploadFilesData {
  final String title;
  final String description;
  final String tag;
  final bool compressed;

  UploadFilesData({this.title, this.description, this.tag, this.compressed});
}
