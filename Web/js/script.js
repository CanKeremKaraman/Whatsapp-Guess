//************************************************
//              Upload file to server
//************************************************

const uploadForm = document.getElementById("UploadFile");
const uploadButton = document.getElementById("UploadButton");
const startButton = document.getElementById("StartButton");
const apiHost = location.hostname || "127.0.0.1";
const apiBase = `http://${apiHost}:8000`;

uploadForm.addEventListener("submit", async function (event) {
  event.preventDefault();
  const formData = new FormData(uploadForm);

  uploadButton.disabled = true;
  document.getElementById("UploadStatus").textContent = "Uploading file...";

  try {
    const response = await fetch(`${apiBase}/upload`, {
      method: "POST",
      body: formData,
    });

    console.log("upload response", response.status, response.statusText);

    if (response.ok) {
      const result = await response.json();
      document.getElementById("UploadStatus").textContent =
        result.info || "File uploaded successfully!";
      startButton.hidden = false;
    } else {
      const errorText = await response.text();
      console.error("Upload failed:", response.status, errorText);
      document.getElementById("UploadStatus").textContent =
        `Failed to upload file (${response.status}).`;
    }
  } catch (error) {
    console.error("Error uploading file:", error);
    document.getElementById("UploadStatus").textContent =
      "Error uploading file. Please try again.";
  } finally {
    uploadButton.disabled = false;
  }
});



//************************************************
//            Reset Upload Server
//************************************************

const resetButton = document.getElementById("ResetButton");
resetButton.addEventListener("click", async function () {
  resetButton.disabled = true;
  try {
    const response = await fetch(`${apiBase}/clear-uploads`, {
      method: "POST",
    });
    const result = await response.json();
    document.getElementById("ResetStatus").textContent =
      `Cleared ${result.cleared} files.`;
  } catch (error) {
    console.error("Error clearing uploads:", error);
    document.getElementById("ResetStatus").textContent =
      "Error clearing uploads.";
  } finally {
    resetButton.disabled = false;
    startButton.hidden = true;
  }
});

startButton.addEventListener("click", function () {
  // Replace this URL with the page you want the Start button to go to.
  window.location.href = "guess.html";
});


