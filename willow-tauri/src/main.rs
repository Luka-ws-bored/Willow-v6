#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use tauri::{Manager, Window};
use serde::{Deserialize, Serialize};
use std::process::{Command, Stdio};
use std::path::PathBuf;

#[derive(Debug, Serialize, Deserialize)]
struct WillowResponse {
    success: bool,
    data: Option<String>,
    error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
struct RAGQuery {
    query: String,
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
    
    let mut cmd = Command::new("python")
        .arg(&python_script)
        .arg("--mode")
        .arg("llm")
        .arg("--prompt")
        .arg(&query.prompt)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to execute Python script: {}", e))?;

    let output = cmd.wait_with_output()
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
    
    let mut cmd = Command::new("python")
        .arg(&python_script)
        .arg("--mode")
        .arg("rag")
        .arg("--query")
        .arg(&query.query)
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to execute Python script: {}", e))?;

    let output = cmd.wait_with_output()
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
    
    let mut cmd = Command::new("python")
        .arg(&python_script)
        .arg("--mode")
        .arg("status")
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| format!("Failed to execute Python script: {}", e))?;

    let output = cmd.wait_with_output()
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

// Helper function to get the path to the Willow Python bridge script
fn get_willow_python_path() -> Result<PathBuf, String> {
    // Get the current executable directory
    let exe_dir = std::env::current_exe()
        .map_err(|e| format!("Failed to get executable directory: {}", e))?
        .parent()
        .ok_or("Failed to get parent directory")?
        .to_path_buf();

    // Look for the bridge script relative to the executable
    let bridge_path = exe_dir.join("..").join("..").join("tauri_bridge.py");
    
    if bridge_path.exists() {
        Ok(bridge_path)
    } else {
        // Fallback to current directory
        let fallback = PathBuf::from("tauri_bridge.py");
        if fallback.exists() {
            Ok(fallback)
        } else {
            Err("Could not find Willow Python bridge script".to_string())
        }
    }
}

// Window management commands
#[tauri::command]
async fn close_splashscreen(window: Window) {
    if let Some(splashscreen) = window.get_window("splashscreen") {
        splashscreen.close().unwrap();
    }
    
    window.get_window("main").unwrap().show().unwrap();
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            query_willow_llm,
            query_willow_rag,
            get_willow_status,
            close_splashscreen
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}