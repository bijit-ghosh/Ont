use std::io::Write;
use std::process::{Command, Stdio};

fn execute(input: &str) -> std::process::Output {
    let mut child = Command::new(env!("CARGO_BIN_EXE_ont-scheduler"))
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .unwrap();
    child
        .stdin
        .take()
        .unwrap()
        .write_all(input.as_bytes())
        .unwrap();
    child.wait_with_output().unwrap()
}
#[test]
fn streams_capacity_recommendations() {
    let output = execute("0 1 0 0 1\n100 1 100 0 1\n");
    assert!(output.status.success());
    assert_eq!(
        String::from_utf8(output.stdout).unwrap(),
        "{\"desired\":1}\n{\"desired\":11}\n"
    );
}
#[test]
fn rejects_bad_and_partial_input() {
    for input in ["nan 1 0 0 1\n", "1 1 0\n", "1 1 -1 0 1\n"] {
        assert!(!execute(input).status.success());
    }
}
