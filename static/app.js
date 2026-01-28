async function fetchEvents() {
  const res = await fetch("/events");
  const data = await res.json();

  const list = document.getElementById("events");
  list.innerHTML = "";

  data.forEach(e => {
    let text = "";

    if (e.action === "PUSH") {
      text = `${e.author} pushed to ${e.to_branch} on ${e.timestamp}`;
    }
    if (e.action === "PULL_REQUEST") {
      text = `${e.author} submitted a pull request from ${e.from_branch} to ${e.to_branch} on ${e.timestamp}`;
    }
    if (e.action === "MERGE") {
      text = `${e.author} merged branch ${e.from_branch} to ${e.to_branch} on ${e.timestamp}`;
    }

    const li = document.createElement("li");
    li.innerText = text;
    list.appendChild(li);
  });
}

fetchEvents();
setInterval(fetchEvents, 15000);
