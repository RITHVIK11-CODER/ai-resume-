const form = document.getElementById("analyzer-form");
const fileInput = document.getElementById("resume-file");
const uploadZone = document.getElementById("upload-zone");
const filePreview = document.getElementById("file-preview");
const fileName = document.getElementById("file-name");
const fileSize = document.getElementById("file-size");
const removeFileButton = document.getElementById("remove-file");
const jobDescription = document.getElementById("job-description");
const characterCount = document.getElementById("character-count");
const analyzeButton = document.getElementById("analyze-button");
const buttonText = document.getElementById("button-text");
const errorMessage = document.getElementById("error-message");
const loadingMessage = document.getElementById("loading-message");
const resultsSection = document.getElementById("results-section");

const MAX_FILE_SIZE = 4 * 1024 * 1024;
let selectedFile = null;

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.hidden = false;
}

function clearError() {
  errorMessage.textContent = "";
  errorMessage.hidden = true;
}

function formatBytes(bytes) {
  return bytes < 1024 * 1024
    ? `${(bytes / 1024).toFixed(0)} KB`
    : `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function validateFile(file) {
  if (!file) return "Please select a PDF resume.";
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    return "Please choose a PDF file.";
  }
  if (file.size > MAX_FILE_SIZE) {
    return "Your PDF must be 4 MB or smaller.";
  }
  if (file.size === 0) {
    return "The selected file is empty.";
  }
  return "";
}

function selectFile(file) {
  clearError();

  const error = validateFile(file);
  if (error) {
    selectedFile = null;
    fileInput.value = "";
    updateFilePreview();
    showError(error);
    return;
  }

  selectedFile = file;
  updateFilePreview();
}

function updateFilePreview() {
  if (!selectedFile) {
    filePreview.hidden = true;
    uploadZone.hidden = false;
    return;
  }

  fileName.textContent = selectedFile.name;
  fileSize.textContent = formatBytes(selectedFile.size);
  filePreview.hidden = false;
  uploadZone.hidden = true;
}

fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) selectFile(file);
});

removeFileButton.addEventListener("click", () => {
  selectedFile = null;
  fileInput.value = "";
  updateFilePreview();
  clearError();
});

["dragenter", "dragover"].forEach((eventName) => {
  uploadZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadZone.classList.add("dragging");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  uploadZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    uploadZone.classList.remove("dragging");
  });
});

uploadZone.addEventListener("drop", (event) => {
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file) selectFile(file);
});

function updateCharacterCount() {
  characterCount.textContent = `${jobDescription.value.length} / 20000`;
}

jobDescription.addEventListener("input", updateCharacterCount);
updateCharacterCount();

function addSkillChips(containerId, skills, missing = false) {
  const container = document.getElementById(containerId);
  container.replaceChildren();

  skills.forEach((skill) => {
    const chip = document.createElement("span");
    chip.className = missing ? "skill-chip missing" : "skill-chip";
    chip.textContent = skill;
    container.appendChild(chip);
  });
}

function renderResults(data) {
  document.getElementById("score-value").textContent = `${data.score}%`;

  document.getElementById("score-ring").style.background =
    `conic-gradient(var(--primary) ${data.score}%, #eceaf5 ${data.score}%)`;

  const heading = document.getElementById("score-heading");
  const description = document.getElementById("score-description");

  if (data.score >= 75) {
    heading.textContent = "Strong keyword alignment";
    description.textContent =
      "Your resume matches many of the detected job requirements. Review the details below.";
  } else if (data.score >= 45) {
    heading.textContent = "Room to strengthen your match";
    description.textContent =
      "Some requirements align. Check the missing skills and refine your resume where appropriate.";
  } else {
    heading.textContent = "An opportunity to improve";
    description.textContent =
      "The detected overlap is limited. Review the role requirements and your relevant experience.";
  }

  document.getElementById("text-score").textContent =
    `${data.text_similarity}%`;
  document.getElementById("skill-score").textContent =
    `${data.skill_coverage}%`;

  addSkillChips("matched-skills", data.matched_skills);
  addSkillChips("missing-skills", data.missing_skills, true);

  document.getElementById("matched-empty").hidden =
    data.matched_skills.length !== 0;
  document.getElementById("missing-empty").hidden =
    data.missing_skills.length !== 0;

  const suggestionsList = document.getElementById("suggestions-list");
  suggestionsList.replaceChildren();

  data.suggestions.forEach((suggestion) => {
    const item = document.createElement("li");
    item.textContent = suggestion;
    suggestionsList.appendChild(item);
  });

  document.getElementById("word-count").textContent =
    `${data.resume_word_count.toLocaleString()} words analyzed`;

  resultsSection.hidden = false;
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearError();

  const jobText = jobDescription.value.trim();

  if (!selectedFile) {
    showError("Please upload your PDF resume first.");
    return;
  }

  const fileError = validateFile(selectedFile);
  if (fileError) {
    showError(fileError);
    return;
  }

  if (!jobText) {
    showError("Please paste the target job description.");
    return;
  }

  const formData = new FormData();
  formData.append("resume", selectedFile);
  formData.append("job_description", jobText);

  analyzeButton.disabled = true;
  buttonText.textContent = "Analyzing...";
  loadingMessage.hidden = false;
  resultsSection.hidden = true;

  try {
    const response = await fetch("/api", {
      method: "POST",
      body: formData
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(data.error || "Analysis failed. Please try again.");
    }

    renderResults(data);
  } catch (error) {
    showError(
      error.message ||
      "Unable to connect to the analysis service. Please try again."
    );
  } finally {
    analyzeButton.disabled = false;
    buttonText.textContent = "Analyze my resume";
    loadingMessage.hidden = true;
  }
});

document.getElementById("reset-button").addEventListener("click", () => {
  resultsSection.hidden = true;
  resultsSection.querySelectorAll(".skill-chip").forEach((chip) => chip.remove());
  window.scrollTo({ top: document.getElementById("analyzer").offsetTop - 20, behavior: "smooth" });
});

document.getElementById("print-button").addEventListener("click", () => {
  window.print();
});
