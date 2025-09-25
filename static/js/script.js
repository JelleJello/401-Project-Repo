// Example of custom JavaScript
document.addEventListener('DOMContentLoaded', function() {
  const currentLocation = window.location.pathname;
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    if (link.getAttribute('href') === currentLocation) {
      link.classList.add('active');
    }
  });
});

// Asset allocation donut chart
new Chart(document.getElementById("assetdoughnut"), {
  type: "pie",
  data: {
    labels: ["NVIDIA", "AMD", "INTEL"],
    datasets: [{
      data: [54, 125, 260],
      backgroundColor: [
        "#21a842ff",
        "#e07c11ff",
        "#066acfff"
      ],
      borderColor: "transparent"
    }]
  },
  options: {
    maintainAspectRatio: false,
    cutoutPercentage: 65,
  }
});