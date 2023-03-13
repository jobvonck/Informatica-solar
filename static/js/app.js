$(document).ready(function () {
  var socket = io.connect();

  socket.on('UpdateSensorData', function (data) {
    document.getElementById("p1").innerHTML = data.Solar;
    document.getElementById("p2").innerHTML = data.Battery;
    document.getElementById("p3").innerHTML = data.Usage;
  });

  socket.on('UpdateButtons', function (data) {
    console.log(data)
  })

  function SendGpio(relay, state) {
    socket.emit('GPIO', {relay: relay, state: state})
  }

  document.querySelectorAll(".switch").forEach(item => {
    item.addEventListener('change', event => {
      if(item.checked) {
        SendGpio(item.id, "on")
      } else {
        SendGpio(item.id, "off")
      }
    })
  })
});
