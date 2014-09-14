function doConnect()
{
    websocket = new WebSocket("ws://localhost:8000/");
    websocket.onopen = function(evt) { onOpen(evt) };
    websocket.onclose = function(evt) { onClose(evt) };
    websocket.onmessage = function(evt) { onMessage(evt) };
    websocket.onerror = function(evt) { onError(evt) };
}

function onOpen(evt)
{
    writeToScreen("socket: connected\n");
}

function onClose(evt)
{
    writeToScreen("socket: disconnected... refresh the page\n");
}

function onMessage(evt)
{
    writeToScreen(evt.data + '\n');
}

function onError(evt)
{
    writeToScreen('socket: error: ' + evt.data + '\n');
	websocket.close();
}

function doSend(message)
{
    writeToScreen('socket: command sent\n');
    websocket.send(message);
}

function writeToScreen(message)
{
    $("#outputtext").append(message);
    $("#outputtext").scrollTop($("#outputtext")[0].scrollHeight);
}

window.addEventListener("load", doConnect, false);