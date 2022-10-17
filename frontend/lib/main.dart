import 'package:flutter/material.dart';

import 'pages/upload_page.dart';
import 'pages/tag_viewer.dart';

void main() => runApp(MaterialApp(
      routes: {
        '/': (context) => TagViewer(),
        '/upload': (context) => UploadPage(),
      },
    ));
