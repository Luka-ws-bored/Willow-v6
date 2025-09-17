#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::process::{Command, Stdio};
use tauri::{AppHandle, Manager};

#[derive(Debug, Serialize, Deserialize)]
struct WillowResponse {
    success: bool,
    data: Option<String>,
    error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct RAGQuery {
    prompt: String, // Changed from 'query' to 'prompt'
    documents: Option<Vec<String>>,
    top_k: Option<u32>,
}

#[derive(Debug, Serialize, Deserialize)]
struct LLMQuery {
    prompt: String,
    model: Option<String>,
    max_tokens: Option<u32>,
}

// Tauri command to query Willow's LLM functionality
#[tauri::command]
async fn query_willow_llm(query: LLMQuery) -> Result<WillowResponse, String> {
    let python_script = get_willow_python_path()?;

    let cmd = Command::new("python")
        .arg(&python_script)
        .arg("--mode")
        .arg("llm")
        .arg("--prompt")
        .arg(&query.prompt)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to execute Python script: {}", e))?;

    let output = cmd
        .wait_with_output()
        .map_err(|e| format!("Failed to read output: {}", e))?;

    if output.status.success() {
        let response = String::from_utf8_lossy(&output.stdout).trim().to_string();
        Ok(WillowResponse {
            success: true,
            data: Some(response),
            error: None,
        })
    } else {
        let error = String::from_utf8_lossy(&output.stderr).trim().to_string();
        Ok(WillowResponse {
            success: false,
            data: None,
            error: Some(error),
        })
    }
}

// Tauri command to query Willow's RAG functionality
#[tauri::command]
async fn query_willow_rag(query: RAGQuery) -> Result<WillowResponse, String> {
    let python_script = get_willow_python_path()?;

    let cmd = Command::new("python")
        .arg(&python_script)
        .arg("--mode")
        .arg("rag")
        .arg("--query")
        .arg(&query.prompt) // Updated to use 'prompt' field
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to execute Python script: {}", e))?;

    let output = cmd
        .wait_with_output()
        .map_err(|e| format!("Failed to read output: {}", e))?;

    if output.status.success() {
        let response = String::from_utf8_lossy(&output.stdout).trim().to_string();
        Ok(WillowResponse {
            success: true,
            data: Some(response),
            error: None,
        })
    } else {
        let error = String::from_utf8_lossy(&output.stderr).trim().to_string();
        Ok(WillowResponse {
            success: false,
            data: None,
            error: Some(error),
        })
    }
}

// Tauri command to get Willow's capabilities and status
#[tauri::command]
async fn get_willow_status() -> Result<WillowResponse, String> {
    let python_script = get_willow_python_path()?;

    let cmd = Command::new("python")
        .arg(&python_script)
        .arg("--mode")
        .arg("status")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to execute Python script: {}", e))?;

    let output = cmd
        .wait_with_output()
        .map_err(|e| format!("Failed to read output: {}", e))?;

    if output.status.success() {
        let response = String::from_utf8_lossy(&output.stdout).trim().to_string();
        Ok(WillowResponse {
            success: true,
            data: Some(response),
            error: None,
        })
    } else {
        let error = String::from_utf8_lossy(&output.stderr).trim().to_string();
        Ok(WillowResponse {
            success: false,
            data: None,
            error: Some(error),
        })
    }
}

// Additional commands that the frontend may call
#[tauri::command]
async fn get_system_info() -> Result<WillowResponse, String> {
    // Mock response for system info - replace with actual implementation
    Ok(WillowResponse {
        success: true,
        data: Some(r#"{"cpu_percent": 45.2, "memory": {"used": 8589934592, "total": 17179869184}, "uptime": 86400}"#.to_string()),
        error: None,
    })
}

#[tauri::command]
async fn get_performance_metrics() -> Result<WillowResponse, String> {
    // Mock response for performance metrics - replace with actual implementation
    Ok(WillowResponse {
        success: true,
        data: Some(
            r#"{"cache_hit_rate": 0.85, "avg_response_time": 0.234, "total_requests": 1247}"#
                .to_string(),
        ),
        error: None,
    })
}

#[tauri::command]
async fn add_document_to_rag(
    _content: String,
    _metadata: Option<serde_json::Value>,
) -> Result<WillowResponse, String> {
    // Mock response for adding document - replace with actual RAG implementation
    Ok(WillowResponse {
        success: true,
        data: Some("Document added successfully".to_string()),
        error: None,
    })
}
// Helper function to get the path to the Willow Python bridge script using Tauri APIs
fn get_willow_python_path() -> Result<PathBuf, String> {
    // In development, look for the bridge script in the project root
    let dev_path = PathBuf::from("../../tauri_bridge.py");
    if dev_path.exists() {
        return Ok(dev_path);
    }

    // Fallback paths for different deployment scenarios
    let fallback_paths = vec![
        PathBuf::from("../../../tauri_bridge.py"),
        PathBuf::from("tauri_bridge.py"),
        PathBuf::from("./tauri_bridge.py"),
    ];

    for path in fallback_paths {
        if path.exists() {
            return Ok(path);
        }
    }

    Err(
        "Could not find Willow Python bridge script. Please ensure tauri_bridge.py is accessible."
            .to_string(),
    )
}

// Window management commands
#[tauri::command]
async fn close_splashscreen(app_handle: AppHandle) {
    if let Some(splashscreen) = app_handle.get_webview_window("splashscreen") {
        let _ = splashscreen.close();
    }

    if let Some(main_window) = app_handle.get_webview_window("main") {
        let _ = main_window.show();
    }
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            query_willow_llm,
            query_willow_rag,
            get_willow_status,
            get_system_info,
            get_performance_metrics,
            add_document_to_rag,
            close_splashscreen
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
