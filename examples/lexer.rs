use viper_lexer::Lexer;

fn main() {
    let lexer = Lexer::new("".to_string()).lex();
    println!("lexer = {:?}", lexer);
}
