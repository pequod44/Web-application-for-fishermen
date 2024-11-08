let map;

function initializeMap() {
  map = L.map("map").setView([46.347141, 48.026459], 14);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution:
      '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
    maxZoom: 18,
  }).addTo(map);
  return map;
}

function parseCoordinates(coordinateData) {
  if (
    coordinateData.type === "Point" &&
    Array.isArray(coordinateData.coordinates)
  ) {
    return {
      lat: parseFloat(coordinateData.coordinates[1]),
      lng: parseFloat(coordinateData.coordinates[0]),
    };
  }
  return null;
}

function loadPoints(map, filterType = "") {
  fetch("/api/v1/points/")
    .then((response) => response.json())
    .then((data) => {
      if (filterType) {
        data = data.filter((point) => point.type === filterType);
      }
      data.forEach((location) => {
        const coords = parseCoordinates(location.as_geojson);
        if (coords) {
          addMarkerToMap(map, location, coords);
        } else {
          displayError("Некорректные координаты:", location);
        }
      });
    })
    .catch((error) => displayError("Ошибка при загрузке точек:", error));
}

function loadAllPointsInfo(sortCriterion = "") {
  const typeMapping = {
    fishing: "Рыбная",
    hunting: "Охотничья",
    camping: "Туристическая база",
  };

  fetch("/api/v1/points/")
    .then((response) => response.json())
    .then((data) => {
      if (sortCriterion) {
        data.sort((a, b) => {
          if (sortCriterion === "name") {
            return a.name.localeCompare(b.name);
          } else if (sortCriterion === "type") {
            return a.type.localeCompare(b.type);
          }
          return 0;
        });
      }

      const pointInfoContainer = document.getElementById("point-list");

      pointInfoContainer.innerHTML = "";

      data.forEach((point) => {
        const coord = parseCoordinates(point.as_geojson);
        const pointInfo = document.createElement("div");
        pointInfo.classList.add("mb-3");
        pointInfo.innerHTML = `
        <div>
        <h5 class="fw-bold">
            <a href="/points/${point.id}/">${point.name}</a>
        </h5>
        <span>@${point.user.username}</span> |
        <a href="/points/${point.type}/" class="badge rounded-pill bg-danger">${
          typeMapping[point.type]
        }</a>
        </div>
        <div class="mb-3">
        <small>(${coord.lat}, ${coord.lng})</small>
        </div>
        <p>${point.description}</p>
        <hr class="my-3">
    `;
        pointInfoContainer.appendChild(pointInfo);
      });
    })
    .catch((error) =>
      displayError("Ошибка при загрузке информации о точках:", error)
    );
}

function addMarkerToMap(map, location, coords) {
  const markerType = {
    fishing: new L.Icon({
      iconUrl: "/static/icons/fishing-icon.png",
      iconSize: [30, 30],
      iconAnchor: [15, 30],
      popupAnchor: [0, -15],
      shadowSize: [30, 30],
    }),
    hunting: new L.Icon({
      iconUrl: "/static/icons/hunting-icon.png",
      iconSize: [30, 30],
      iconAnchor: [15, 30],
      popupAnchor: [0, -15],
      shadowSize: [30, 30],
    }),
    camping: new L.Icon({
      iconUrl: "/static/icons/camping-icon.png",
      iconSize: [30, 30],
      iconAnchor: [15, 30],
      popupAnchor: [0, -15],
      shadowSize: [30, 30],
    }),
  };

  const icon = markerType[location.type] || L.Icon.Default;
  const marker = L.marker([coords.lat, coords.lng], { icon }).addTo(map);
  marker.on("click", function () {
    showPointInfo(location);
  });
}

let tempMarker;

function handleMapClick(e, map) {
  if (tempMarker) {
    map.removeLayer(tempMarker);
  }
  let popup = L.popup();
  let lat = e.latlng.lat;
  let lng = e.latlng.lng;
  let coordinates = { lat: lat, lng: lng };
  $("#coordinates").val(JSON.stringify(coordinates));
  popup
    .setLatLng(e.latlng)
    .setContent(
      '<p>Установить точку здесь?<br/> <button id="addPointButton" class="btn btn-primary" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasWithBothOptions" aria-controls="offcanvasWithBothOptions">Добавить точку</button></p>'
    )
    .openOn(map);

  $("#addPointButton").on("click", function () {
    map.closePopup();
    if (tempMarker) {
      map.removeLayer(tempMarker);
    }
    tempMarker = L.marker(e.latlng).addTo(map);
  });
}

function setupMapEvents(map) {
  map.on("contextmenu click", function (e) {
    handleMapClick(e, map);
  });
  map.on("move start", function () {
    map.closePopup();
  });
  map.on("zoomstart", function () {
    map.closePopup();
  });
}

function setupFormSubmission(map) {
  $(document).on("submit", "#post-form", function (e) {
    e.preventDefault();
    let formData = new FormData($("#post-form")[0]);
    let coordinates = JSON.parse($("#coordinates").val());
    let geojson = JSON.stringify({
      type: "Point",
      coordinates: [coordinates.lng, coordinates.lat],
    });
    formData.append("as_geojson", geojson);
    $.ajax({
      type: "POST",
      url: "/api/v1/points/",
      data: formData,
      contentType: false,
      processData: false,
      success: function (pointData) {
        const coords = parseCoordinates(pointData.as_geojson);
        if (coords) {
          addMarkerToMap(map, pointData, coords);
          let offcanvasAddPoint = bootstrap.Offcanvas.getInstance(
            document.getElementById("offcanvasWithBothOptions")
          );
          if (offcanvasAddPoint) {
            offcanvasAddPoint.hide();
          }
          $("#post-form").trigger("reset");
          if (tempMarker) {
            tempMarker.fire("click");
          }
        } else {
          displayError("Некорректные координаты у созданной точки:", pointData);
        }
      },
      error: function (error) {
        displayError("Ошибка при создании точки:", error.responseJSON);
      },
    });
  });
}

function clearTempMarkerOnHide() {
  const offcanvasElement = document.getElementById("offcanvasWithBothOptions");
  offcanvasElement.addEventListener("hide.bs.offcanvas", function () {
    if (tempMarker) {
      map.removeLayer(tempMarker);
      tempMarker = null;
    }
  });
}

function displayAndAddComment(comment) {
  const commentContainer = document.getElementById("comment-container");
  const commentElement = document.createElement("div");
  commentElement.classList.add(
    "existing-comment",
    "mb-2",
    "p-2",
    "border",
    "rounded"
  );

  const authorElement = document.createElement("h6");
  authorElement.classList.add("comment-author");
  authorElement.textContent = `@${comment.user.username}`;

  const dateElement = document.createElement("small");
  dateElement.classList.add("comment-date", "text-muted");
  const commentDate = new Date(comment.updated_at);
  dateElement.textContent = `Дата: ${commentDate.toLocaleString()}`;

  const messageElement = document.createElement("p");
  messageElement.classList.add("comment-message");
  messageElement.textContent = comment.message;

  commentElement.appendChild(authorElement);
  commentElement.appendChild(dateElement);
  commentElement.appendChild(messageElement);

  commentContainer.appendChild(commentElement);
}

function showPointInfo(location) {
  const typeMapping = {
    fishing: "Рыбная",
    hunting: "Охотничья",
    camping: "Туристическая база",
  };

  const pointInfo = document.getElementById("point-info");
  const offcanvasInstance = bootstrap.Offcanvas.getInstance(pointInfo);
  if (offcanvasInstance && pointInfo.classList.contains("show")) {
    offcanvasInstance.hide();
  }

  const coord = parseCoordinates(location.as_geojson);
  const pointName = document.getElementById("point-name");
  pointName.innerHTML = `<a href="/points/${location.id}/">${location.name}</a>`;
  document.getElementById("point-type").textContent =
    typeMapping[location.type];
  document.getElementById(
    "point-coordinates"
  ).textContent = `(${coord.lat}, ${coord.lng})`;
  document.getElementById("point-description").textContent =
    location.description;
  document.getElementById(
    "point-author"
  ).textContent = `@${location.user.username}`;

  const pointImage = document.getElementById("point-image");
  const pointImageContainer = document.getElementById("point-image-container");
  if (location.image) {
    pointImage.src = location.image;
    pointImageContainer.style.display = "block";
  } else {
    pointImage.src = "";
    pointImageContainer.style.display = "none";
  }

  const commentForm = document.getElementById("comment-form");
  commentForm.setAttribute("data-point-id", location.id);

  const commentContainer = document.getElementById("comment-container");
  commentContainer.innerHTML = "";

  location.comments.forEach((comment) => {
    displayAndAddComment(comment);
  });

  const newOffcanvasInstance = new bootstrap.Offcanvas(pointInfo);
  newOffcanvasInstance.show();
}

function setupCommentFormSubmission() {
  document
    .getElementById("comment-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const pointId = this.getAttribute("data-point-id");
      const comment = document.getElementById("comment").value;
      const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
      ).value;

      fetch(`/api/v1/points/${pointId}/comments/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken,
        },
        body: JSON.stringify({ message: comment }),
      })
        .then((response) => {
          if (!response.ok) {
            return response.text().then((text) => {
              throw new Error(text);
            });
          }
          return response.json();
        })
        .then((data) => {
          displayAndAddComment(data);
          document.getElementById("comment").value = "";
        })
        .catch((error) => {
          displayError("Ошибка при добавлении комментария:", error.message);
        });
    });
}

function displayError(message, details) {
  const errorContainer = document.getElementById("error-container");
  errorContainer.classList.remove("d-none");
  let errorText = "";
  if (
    details &&
    details.non_field_errors &&
    Array.isArray(details.non_field_errors)
  ) {
    errorText = details.non_field_errors.join(" ");
  } else {
    errorText = JSON.stringify(details, null, 2);
  }
  errorContainer.innerHTML = `<strong>${message}</strong> ${errorText}`;
  setTimeout(() => {
    errorContainer.classList.add("d-none");
    errorContainer.innerHTML = "";
  }, 5000);
}

document.addEventListener("DOMContentLoaded", function () {
  let map = initializeMap();
  loadPoints(map);
  setupMapEvents(map);
  setupFormSubmission(map);
  setupCommentFormSubmission();
  clearTempMarkerOnHide();
});

document
  .getElementById("show-all-points")
  .addEventListener("click", function () {
    const sortCriterion = document.getElementById("sort-criteria").value;
    loadAllPointsInfo(sortCriterion);
  });

document
  .getElementById("sort-criteria")
  .addEventListener("change", function () {
    const sortCriterion = document.getElementById("sort-criteria").value;
    loadAllPointsInfo(sortCriterion);
  });

document.addEventListener("click", function (event) {
  const pointInfo = document.getElementById("point-info");
  const pointInfoAll = document.getElementById("point-info-all");
  const targetElement = event.target;

  if (
    !pointInfo.contains(targetElement) &&
    !pointInfoAll.contains(targetElement)
  ) {
    if (pointInfo.classList.contains("show")) {
      const windowSinglePoint = bootstrap.Offcanvas.getInstance(pointInfo);
      if (windowSinglePoint) {
        windowSinglePoint.hide();
      }
    }

    if (pointInfoAll.classList.contains("show")) {
      const windowsAllPoints = bootstrap.Offcanvas.getInstance(pointInfoAll);
      if (windowsAllPoints) {
        windowsAllPoints.hide();
      }
    }
  }
});

document
  .getElementById("point-type-filter")
  .addEventListener("change", function () {
    const selectedType = this.value;
    map.eachLayer((layer) => {
      if (!!layer.toGeoJSON) {
        map.removeLayer(layer);
      }
    });
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors',
      maxZoom: 18,
    }).addTo(map);
    loadPoints(map, selectedType);
  });
