async function testGet() {
  const res = await fetch("http://localhost:3000/api/get");
  document.getElementById("output").innerText = await res.text();
}

const cors = require("cors");
app.use(cors()); // allow all origins

async function testPost() {
  const res = await fetch("http://localhost:3000/api/post", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: "Samuel" })
  });
  document.getElementById("output").innerText = await res.text();
}

async function testPut() {
  const res = await fetch("http://localhost:3000/api/put/123", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ update: "New Data" })
  });
  document.getElementById("output").innerText = await res.text();
}

async function testPatch() {
  const res = await fetch("http://localhost:3000/api/patch/123", {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ partial: "Updated" })
  });
  document.getElementById("output").innerText = await res.text();
}
