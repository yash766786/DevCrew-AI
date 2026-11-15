const API_BASE = "http://127.0.0.1:8000";

export async function createProject(prompt: string, sessionId: string) {
  const response = await fetch(`${API_BASE}/projects`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      prompt,
      session_id: sessionId,
    }),
  });

  return response.json();
}

export async function respondToProject(projectId: string, message: string) {
  const response = await fetch(`${API_BASE}/projects/${projectId}/respond`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
    }),
  });

  return response.json();
}

export async function modifyProject(projectId: string, message: string) {
  const response = await fetch(`${API_BASE}/projects/${projectId}/modify`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
    }),
  });

  return response.json();
}

export async function downloadProject(projectId: string) {
  const response = await fetch(`${API_BASE}/projects/${projectId}/download`);

  if (!response.ok) {
    throw new Error("Download failed");
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");

  a.href = url;
  a.download = `${projectId}.zip`;
  document.body.appendChild(a);

  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
