import 'package:flutter/material.dart';

class TileData {
  final int id;
  final String url;
  Color overlay; //set value not out of database

  TileData({this.id, this.url, this.overlay});

  factory TileData.fromJson(Map<String, dynamic> json) {
    return TileData(
        id: json['id'],
        url: json['file_path'],
        //maybe solve differently
        overlay: Colors.transparent);
  }
}

class ImageData extends TileData {
  final int id;
  final String title;
  final String description;
  final String url;
  final bool comic;
  final String timeCreated;
  Color overlay; //set value not out of database

  ImageData(
      {this.id,
      this.title,
      this.description,
      this.url,
      this.comic,
      this.timeCreated,
      this.overlay});

  factory ImageData.fromJson(Map<String, dynamic> json) {
    bool comic;
    if (json["comic"] == 0) {
      comic = false;
    } else {
      comic = true;
    }
    return ImageData(
        id: json['id'],
        title: json['title'],
        description: json['description'],
        url: json['file_path'],
        comic: comic,
        timeCreated: json['time_created'],

        //maybe solve differently
        overlay: Colors.transparent);
  }
}

class TagData extends TileData {
  final int id;
  final String name;
  final String url;
  Color overlay; //set value not out of database

  TagData({this.id, this.url, this.name, this.overlay});

  factory TagData.fromJson(Map<String, dynamic> json) {
    return TagData(
        id: json['tag_id'],
        name: json['tname'],
        url: json['file_path'],

        //maybe solve differently
        overlay: Colors.transparent);
  }
}
