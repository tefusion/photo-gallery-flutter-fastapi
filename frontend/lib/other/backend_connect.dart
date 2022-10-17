import 'dart:io';

import 'package:dio/dio.dart';
import 'package:http/http.dart' as http;

//for hosting on another device change this to the ip of the device
final String baseUrl = "http://127.0.0.1:8000";

var dio = Dio();

get(String url) async {
  try {
    return await http.get(Uri.parse(baseUrl + url));
  } on SocketException catch (e) {
    //if connection failed handle here
    print("Server most likely not online (SocketException)");
    return http.Response(
        "", 404); //for handling parsing data, can check status code
  } on http.ClientException catch (e) {
    print("Server most likely not online (ClientException)");
    return http.Response("", 404);
  }

  //otherwise handle outside
}

delete(String url) async {
  try {
    return await http.delete(Uri.parse(baseUrl + url));
  } catch (e) {
    print(e);
  }
}

put(String url) async {
  try {
    return await http.put(Uri.parse(baseUrl + url));
  } catch (e) {
    print(e);
  }
}

post(FormData formData, String urlPath) async {
  dio.options.baseUrl = baseUrl;
  try {
    var response = await dio.post(urlPath, data: formData);
    return response;
  } on http.ClientException catch (e) {
    print("Server most likely not online, failed post (ClientException)");
  } catch (e) {
    print(e);
  }
}
