$(document).ready(function () {
  var socket = io.connect();

  socket.on('UpdateSensorData', function (data) {
    document.getElementById("p1").innerHTML = data.Solar;
    document.getElementById("p2").innerHTML = data.Battery;
    document.getElementById("p3").innerHTML = data.Usage;
  });
});
