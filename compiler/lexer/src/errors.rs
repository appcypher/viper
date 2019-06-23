#[derive(Debug)]
pub struct LexerError {
    message: &'static str,
    row: usize,
    column: usize,
}
