function getQueryParam(name) {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(name);
}

const csvFile = getQueryParam('file');

// Load and parse the CSV
fetch(csvFile)
  .then(response => {
    if (!response.ok) {
      throw new Error(`Could not fetch ${csvFile}`);
    }
    return response.text();
  })
  .then(csv => {
    Papa.parse(csv, {
      header: true,
      skipEmptyLines: true,
      complete: function(results) {
        populateTable(results.data);
        $('#csvTable').DataTable({
          pageLength: 25,
          order: [[1, 'desc']]
        });
      }
    });
  })
  .catch(error => {
    console.error('Error loading CSV:', error);
    document.getElementById("csvTable").innerHTML =
      `<caption>Error loading file: <code>${csvFile}</code></caption>`;
  });

function populateTable(data) {
  const table = document.getElementById("csvTable");
  const thead = table.querySelector("thead");
  const tbody = table.querySelector("tbody");

  if (data.length === 0) return;

  const headers = Object.keys(data[0]);
  const headerRow = document.createElement("tr");
  headers.forEach(header => {
    const th = document.createElement("th");
    th.textContent = header;
    headerRow.appendChild(th);
  });
  thead.appendChild(headerRow);

  data.forEach(row => {
    const tr = document.createElement("tr");
    headers.forEach(header => {
      const td = document.createElement("td");
      td.textContent = row[header];
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
}
