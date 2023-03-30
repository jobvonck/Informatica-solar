$(document).ready(function () {
  const clock = document.querySelector('.clock');
 
  const tick = () => {
    const now = new Date();
    let h = now.getHours();
    const m = now.getMinutes();
    const s = now.getSeconds();

    var today = new Date();
    var date = today.getDate() + '-' + (today.getMonth() + 1) + '-' + today.getFullYear();

    const html =
      `<h1 style="text-align:center; margin-bottom:0;">
    <span>${("0" + h).slice(-2)}</span> : 
    <span>${("0" + m).slice(-2)}</span> : 
    <span>${("0" + s).slice(-2)}</span></h1>
    <p style="text-align:center;">${date}</p>
    `;

    clock.innerHTML = html;
  };

  setInterval(tick, 1000);

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

  const MAX_DATA_COUNT = 50;
  var socket = io.connect();

  socket.on("UpdateSensorData", function (msg) {
    document.getElementById("mprice").innerHTML = "€" + msg.Price[0];
    document.getElementById("price").innerHTML = "€" + msg.Price[1];
    document.getElementById("charge").innerHTML = msg.Charge + "<sup>%</sup>";

    document.getElementById("BatteryVoltage").innerHTML = msg.BatteryVoltage + " V";
    document.getElementById("SolarVoltage").innerHTML = msg.SolarVoltage + " V";
    document.getElementById("BatteryCurrent").innerHTML = msg.BatteryCurrent + " A";
    document.getElementById("SolarCurrent").innerHTML = msg.SolarCurrent + " A";
    document.getElementById("SolarPower").innerHTML = msg.Solar + " W";
    document.getElementById("BatteryPower").innerHTML = msg.Battery + " W";

    if (msg.Charge < 20) {
      document.getElementById("charge").classList.add('off');
    } else {
      document.getElementById("charge").classList.remove('off');
    }

    if (myChart.data.labels.length > MAX_DATA_COUNT) {
      removeFirstData();
    }
    addData(msg.date, msg);
  });

  socket.on("GetWeather", function (msg) {
    const icon = "http://openweathermap.org/img/w/" + msg.weather[0]["icon"] + ".png"
    const data = `<h2 class="city-name" data-name="${msg.name},${msg.sys.country}"><span>${msg.name}</span><sup>${msg.sys.country}</sup></h2><div class="city-temp">${Math.round(msg.main.temp)}<sup>°C</sup></div><figure><img class="city-icon" src="${icon}" alt="${msg.weather[0]["description"]}"><figcaption>${msg.weather[0]["description"]}</figcaption></figure>`;
    document.getElementById("weer").innerHTML = data;

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

  const PChart = document.getElementById('PriceChart');

  const PriceChart = new Chart(PChart, {
    type: "line",
    data: {
      datasets: [{ label: "Totaal", borderColor: '#96C3CE', backgroundColor: '#96C3CE', }, { label: "Marktprijs", borderColor: '#4BC6B9', backgroundColor: '#4BC6B9', }],
    },
    options: {
      borderWidth: 3,
      borderColor: ['rgba(255, 99, 132, 1)',],
    },
  });

  socket.on('UpdatePrice', function (data) {
    PriceChart.data.labels.length = 0;
    PriceChart.data.datasets[0].length = 0;
    PriceChart.data.datasets[1].length = 0;

    data.forEach((element) => {
      PriceChart.data.labels.push(element[0]);
      PriceChart.data.datasets[0].data.push(element[1]);
      PriceChart.data.datasets[1].data.push(element[2]);
    });

    PriceChart.update();
  })

  socket.on('DataGraph', function (data) {
    console.log(data);
    myChart.data.labels = data.date;
    myChart.data.datasets[0].data = data.Solar;
    myChart.data.datasets[1].data = data.Battery;
    myChart.data.datasets[2].data = data.Usage;
    myChart.update();
  })
});
