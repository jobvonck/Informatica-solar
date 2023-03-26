$(document).ready(function () {
  var socket = io.connect();

  const ctx = document.getElementById("myChart").getContext("2d");

  const myChart = new Chart(ctx, {
    type: "line",
    data: {
      datasets: [{ label: "Solar", borderColor: '#96C3CE', backgroundColor: '#96C3CE', }, { label: "Batterij", borderColor: '#4BC6B9', backgroundColor: '#4BC6B9', }, { label: "Gebruik", borderColor: '#A79AB2', backgroundColor: '#A79AB2', }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(255, 99, 132, 1)',],
    },
  });

  function addData(label, data) {
    myChart.data.labels.push(label);
    myChart.data.datasets[0].data.push(data.Solar);
    myChart.data.datasets[1].data.push(data.Battery);
    myChart.data.datasets[2].data.push(data.Usage);
    myChart.update();
  }

  function removeFirstData() {
    myChart.data.labels.splice(0, 1);
    myChart.data.datasets.forEach((dataset) => {
      dataset.data.shift();
    });
  }

  const MAX_DATA_COUNT = 10;
  //connect to the socket server.
  //   var socket = io.connect("http://" + document.domain + ":" + location.port);
  var socket = io.connect();

  //receive details from server
  socket.on("UpdateSensorData", function (msg) {
    console.log("Received sensorData :: " + msg.date + " :: " + msg.value);

    // Show only MAX_DATA_COUNT data
    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData();
    }
    addData(msg.date, msg);
  });

  socket.emit("StartButtons")

  socket.on('UpdateButtons', function (data) {
    if (data.State == "on") {
      document.getElementById(data.Relay).classList.add('on');
      document.getElementById(data.Relay).classList.remove('off');
      document.getElementById(data.Relay).innerHTML = "aan";
    } else {
      document.getElementById(data.Relay).classList.add('off');
      document.getElementById(data.Relay).classList.remove('on');
      document.getElementById(data.Relay).innerHTML = "uit";
    }
  })
});
