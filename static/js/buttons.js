$(document).ready(function () {
    var socket = io.connect();

    socket.emit("StartButtons")
  
    socket.on('UpdateButtons', function (data) {
        if(data.State =="on") {
            button = document.getElementById(data.Relay).checked = true;
        } else {
            button = document.getElementById(data.Relay).checked = false;
        }
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