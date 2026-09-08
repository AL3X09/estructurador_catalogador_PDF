use tauri_plugin_shell::process::CommandEvent;
use tauri_plugin_shell::ShellExt;

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            // Launch the sidecar depending on environment
            // Actually, tauri's `Command::new_sidecar` abstracts it.
            // But we need a binary present for new_sidecar to work, even in dev.
            // For now, in dev we can spawn python directly.

            let mut cmd = if cfg!(debug_assertions) {
                app.shell().command("python").args(["python/api.py"])
            } else {
                app.shell()
                    .sidecar("pdf-sidecar")
                    .expect("failed to create sidecar command")
            };

            let (mut rx, child) = cmd.spawn().expect("Failed to spawn sidecar");

            // Optionally spawn a task to read sidecar stdout/stderr
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(line) => {
                            println!("Sidecar stdout: {:?}", String::from_utf8_lossy(&line));
                        }
                        CommandEvent::Stderr(line) => {
                            eprintln!("Sidecar stderr: {:?}", String::from_utf8_lossy(&line));
                        }
                        _ => {}
                    }
                }
            });

            // The child process will be killed when the app exits because we used tauri's shell plugin

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
