const { config } = require("process");

var querystring = require("querystring"),
  url = require("url"),
  fs = require("fs");

let { PythonShell } = require('python-shell')

function start(response) {
  console.log("Request handler 'start' was called.");

  response.writeHead(200, { 'Content-Type': 'text/html' });
  //取得路徑

  fs.readFile("main.html", "utf8", function (error, data) {
    //當fs讀不到檔案或發生錯誤時，error會是true
    if (error) {
      response.writeHead(404, { 'Content-Type': 'text/html' });
      response.end("404 not found");
      return 0;
    }
    response.writeHead(200, { 'Content-Type': 'text/html' });
    response.write(data);
    response.end();
  });


}

function show(response) {
  console.log("Request handler 'show' was called.");
  fs.readFile("/tmp/test.png", "binary", function (error, file) {
    if (error) {
      response.writeHead(500, { "Content-Type": "text/plain" });
      response.write(error + "\n");
      response.end();
    } else {
      response.writeHead(200, { "Content-Type": "image/png" });
      response.write(file, "binary");
      response.end();
    }
  });
}

function qry(response, request) {
  var s = querystring.parse(url.parse(request.url).query)['str'];
  let options = {
    pythonPath: 'C:\\Users\\scsha\\AppData\\Local\\Microsoft\\WindowsApps\\python',
    args:
      [
        s,
      ]
  }
  PythonShell.run('./qry.py', options, (err, data) => {
    if (err) response.end(err)
    // response.write(data[0]);
    // response.end();

    response.end(data[0]);
  })
}

function dictqry(response, request) {
  var s = querystring.parse(url.parse(request.url).query)['str'];
  let options = {
    pythonPath: 'C:\\Users\\scsha\\AppData\\Local\\Microsoft\\WindowsApps\\python',
    args:
      [
        s,
      ]
  }
  PythonShell.run('./dictqry.py', options, (err, data) => {
    if (err) response.end(err)
    // var s="",i;
    // for(i=0;i<data.length;i++){
    //   s=s+data[i];
    // }
    // response.write(s);
    // response.end();
    
    fs.readFile("result.txt", "utf8", function (error, data) {
      //當fs讀不到檔案或發生錯誤時，error會是true
      if (error) {
        response.writeHead(404, { 'Content-Type': 'text/html' });
        response.end("404 not found");
        return 0;
      }
      // response.writeHead(200, { 'Content-Type': 'text/html' });
      response.write(data);
      response.end();
    });
  })
}

exports.start = start;
exports.show = show;
exports.qry = qry;
exports.dictqry = dictqry;