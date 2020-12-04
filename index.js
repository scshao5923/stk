var server = require("./server");
var router = require("./router");
var requestHandlers = require("./requestHandlers");

var handle = {}
handle["/"] = requestHandlers.start;
handle["/start"] = requestHandlers.start;
handle["/upload"] = requestHandlers.upload;
handle["/show"] = requestHandlers.show;
handle["/webdict/stk/qry"] = requestHandlers.qry;
handle["/webdict/qry"] = requestHandlers.dictqry;

server.start(router.route, handle);