function returnItem(orderId) {
  fetch("/return-item", {
    method: "POST",
    body: JSON.stringify({ order_id: orderId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}
