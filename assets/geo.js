window.dash_clientside = Object.assign({}, window.dash_clientside, {
  geo: {
    getPosition: function(n) {
      if (!navigator.geolocation) {
        return { ok: false, error: "Geolocation non supportée" };
      }

      return new Promise((resolve) => {
        navigator.geolocation.getCurrentPosition(
          (pos) => {
            resolve({
              ok: true,
              lat: pos.coords.latitude,
              lon: pos.coords.longitude,
              accuracy_m: pos.coords.accuracy
            });
          },
          (err) => {
            resolve({ ok: false, error: err.message || "Permission refusée" });
          },
          { enableHighAccuracy: false, timeout: 5000, maximumAge: 60000 }
        );
      });
    }
  }
});
