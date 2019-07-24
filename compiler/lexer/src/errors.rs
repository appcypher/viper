#[derive(Debug)]
pub struct LexerError {
    message: String,
    row: usize,
    column: usize,
}

impl LexerError {
    pub fn new(message: String, row: usize, column: usize) -> Self {
        Self {
            message, row, column,
        }
    }
}
