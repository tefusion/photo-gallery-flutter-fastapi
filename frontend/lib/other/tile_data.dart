import 'package:flutter/material.dart';

class TileData {
  final String id;
  final String url;
  Color overlay; //set value not out of database

  TileData({this.id, this.url, this.overlay});

  factory TileData.fromJson(Map<String, dynamic> json) {
    return TileData(
        id: json['uuid'],
        url: json['uuid'] + "." + json["type"],
        //maybe solve differently
        overlay: Colors.transparent);
  }
}

class ImageData extends TileData {
  final String id;
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
        id: json['uuid'],
        title: json['title'],
        description: json['description'],
        url: json['uuid'] + "." + json["type"],
        comic: comic,
        timeCreated: json['time_created'],

        //maybe solve differently
        overlay: Colors.transparent);
  }
}

class TagData extends TileData {
  final String id;
  final String name;
  final String url;
  Color overlay; //set value not out of database

  TagData({this.id, this.url, this.name, this.overlay});

  factory TagData.fromJson(Map<String, dynamic> json) {
    return TagData(
        id: json['tname'],
        name: json['tname'],
        url: json['uuid'] + "." + json["type"],

        //maybe solve differently
        overlay: Colors.transparent);
  }
}
